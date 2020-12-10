from django.core.paginator import Paginator
from django.apps import apps
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse


import datetime
import json

from rest_framework.decorators import api_view
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_api.serializers import IncidentSerializer

from .filters import *
from .forms import *
from .models import *
from .utils import *

from access.models import *
from base.forms import *
from base.models import *
from base.utils import *
from tracking.forms import *
from tracking.models import *
from tracking.utils import *

# Create your views here.

def incident(request):
    form = IncidentForm()
    context = {
        'form' : form
        }

    return render(request, 'ticket/incident.html', context)

def incident_create(request):
    #Create new incident
    incident = Incident.objects.create()

    #Set default values not in model
    incident.status = get_status_default(id=1)
    incident.priority = get_priority_default()
    incident.ticket_type = TicketType.objects.get(id=1)

    #Save new incident
    incident.save()
    
    #Create work note
    work_note = create_work_note(sysID=incident.sysID, newly_created=True, request=request)

    inc_detail_url = 'incident-detail/' + incident.number
    return redirect(inc_detail_url)

def incident_detail(request, number):
    incident = Incident.objects.get(number=number)
    form = IncidentForm(instance=incident)

    #Get initial field values for work notes
    work_note_data = get_object_notes(incident)
    work_notes = WorkNote.objects.filter(foreign_sysID=incident.sysID).order_by('-created')
    wn_form = WorkNoteForm()

    #Get inital field values
    incident_status = incident.status

    #Get select options
    status_select_choices = get_status_choices(id=1)
    priority_select_choices = get_priority_choices()
    assignment_group_select_choices = get_assignment_group_choices()

    #Get attachments
    attachments = Attachment.objects.filter(foreign_sysID=incident.sysID).order_by('-id')
    attachment_form = AttachmentForm()



    ### POST ###
    if request.method == 'POST':

        form = IncidentForm(request.POST, instance=incident)        

        #Add attachment to ticket
        if 'add_attachment' in request.POST:

            add_attachment(request=request, obj=incident)
            return redirect('incident-detail', number=number)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.ticket_type = TicketType.objects.get(id=1)
         
            #Set updated field to NOW            
            instance.updated = timezone.now()

            #Get the resolved status for the ticket 
            status_resolved = get_status_resolved(id=1)

            #If ticket was reopened (changed from 'Resolved' to another status), then increment reopened value by 1
            if incident_status == status_resolved and instance.status != status_resolved:
                instance.reopened += 1

            #Resolve ticket if resolve submit button was clicked OR status was set to "resolved" AND text was entered in resolution textbox
            if ('resolve' in request.POST or instance.status == status_resolved) and instance.resolution:
                instance.resolved = timezone.now()
                instance.status = get_status_resolved(id=1)
                instance.save()

                #Create work note
                work_note_changes = get_object_notes(instance, id=1)
                changes = compare_field_changes(work_note_data, work_note_changes)
                work_note = create_work_note(obj=instance.sysID, request=request, changes=changes)


                return redirect('incident-detail', number=number) 
            else:
                #If ticket is not being resolved, then clear the data from the resolved field
                if instance.status != get_status_resolved(id=1):
                    instance.resolved = None
            
            instance.save()

            #Create work note
            work_note_changes = get_object_notes(instance, id=1)
            changes = compare_field_changes(work_note_data, work_note_changes)
            work_note = create_work_note(sysID=instance.sysID, request=request, changes=changes)

            #Redirect url based on submit button
            if 'save_stay' in request.POST:
                return redirect('incident-detail', number=number) 
            elif 'save_return' in request.POST:
                return redirect('incident')

    else:
        form = IncidentForm(instance=incident)

    context = {
        'incident' : incident,
        'form' : form,
        'work_notes' : work_notes,
        'wn_form' : wn_form,
        'attachments' : attachments,
        'attachment_form' : attachment_form,
    } 

    return render(request, 'ticket/incident-detail.html', context)


def incident_search(request):

    form = IncidentForm()

    incidents = Incident.objects.all()
    inc_filter = IncidentFilter(request.GET, queryset=incidents)

    #Set search results to filter queryset if search args passed in GET
    #Else set queryset to blank
    if request.GET:
        incidents = inc_filter.qs
        paginator = Paginator(incidents.order_by('id'), 10)
    else:
        incidents = ''
        paginator = Paginator(incidents, 10)

    #Setup paginator
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    #If export button -> export data to csv
    if 'export' in request.GET:
        return export_csv(queryset=incidents, obj_type='incident')

    context = {
        'form' : form,
        'filter' : inc_filter,
        'incidents' : incidents,
        'page_obj' : page_obj,
        }

    return render(request, 'ticket/incident-search.html', context)


def export_csv(queryset, obj_type):

    #Dictionary of 'model name : app name'
    #Used for apps.get_model function
    MODEL_APP_DICT = {
		'tickettype' : 'ticket',
		'customer' : 'access',
		'location' : 'access',
		'priority' : 'ticket', 
		'status' : 'ticket',
		'group' : 'access',		
	}

    #Ignore these fields in queryset
    EXCLUDE_FIELDS = ['id','sysID','ticket_ptr']
    EXCLUDE_FIELD_NAMES = ['id','sysID_id','ticket_ptr_id']

    #For forieign keys where the name is different than the model
    FK_REPLACE_FIELD_NAMES = {
        'assignment_group' : 'group',
        'assignee' : 'customer',
    }

    #Set export filename
    timestamp = format(timezone.now(), 'U')
    file_name = f"{obj_type}-{timestamp}.csv"

    #Get field names
    #Ignore field names in EXCLUDE_FIELDS list
    field_names = [field.name for field in queryset.model._meta.fields if not (field.name in EXCLUDE_FIELDS)]

    # Create the HttpResponse object with CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={file_name}'
    writer = csv.writer(response)

    #Write header row
    writer.writerow(field_names)  

    #Build and write rows for each instance in the queryset
    for instance in queryset.values():

        value_list = []
        for field, value in instance.items():

            #Ignore fields in the EXCLUDE_FIELD_NAMES dict
            if not (field in EXCLUDE_FIELD_NAMES):
                #If value in a foriegn key (ends with '_id')
                if '_id' in field:

                    #Remove '_id' from end of string
                    f_name = field.replace('_id', '')
                    
                    #If field name is different than the model name, then replace it
                    if f_name in FK_REPLACE_FIELD_NAMES:
                        f_name = f_name.replace(f_name, FK_REPLACE_FIELD_NAMES[f_name])

                    #Get value from model
                    if value:
                        f_name = f_name.replace('_', '')
                        model = apps.get_model(MODEL_APP_DICT[f_name], f_name)
                        obj = model.objects.get(id=value)
                        value = obj

                #Add value to list (row)
                value_list.append(value)
            
        #Write row
        writer.writerow(value_list)

    return response
    

