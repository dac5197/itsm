from django.apps import apps
from django.contrib.auth.decorators import login_required
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

from access.decorators import allowed_users
from access.models import *
from access.utils import get_user_roles
from base.forms import *
from base.models import *
from base.utils import *
from tracking.forms import *
from tracking.models import *
from tracking.utils import *

# Create your views here.
@login_required(login_url='/access/login')
def incident(request):
    form = IncidentForm()
    context = {
        'form' : form
        }

    return render(request, 'ticket/incident.html', context)

@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
def incident_create(request):
    #Create new incident
    incident = Incident.objects.create()

    #Set default values not in model
    incident.status = get_status_default(id=1)
    incident.priority = get_priority_default()
    incident.ticket_type = TicketType.objects.get(id=1)

    #Save new incident
    incident.save()
    
    #Set the relationship fields on the matching sysID
    set_sysID_relationship_fields(incident)

    #Create work note
    work_note = create_work_note(sysID=incident.sysID, newly_created=True, request=request)

    inc_detail_url = 'incident-detail/' + incident.number
    return redirect(inc_detail_url)

@login_required(login_url='/access/login')
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
        
        #Add attachment to ticket
        if 'add_attachment' in request.POST:

            #Save attachment
            attachment_form = add_attachment(request=request, obj=incident)
            
            #If any errors then display in inc form 
            if attachment_form.errors:
                context = {
                    'incident' : incident,
                    'form' : form,
                    'work_notes' : work_notes,
                    'wn_form' : wn_form,
                    'attachments' : attachments,
                    'attachment_form' : attachment_form,
                } 

                return render(request, 'ticket/incident-detail.html', context)
            
            #Return to INC
            else:
                return redirect('incident-detail', number=number)

        #If Resolve button was clicked, then change status to 'resolved' before checking if form is valid
        if 'resolve' in request.POST:
            request.POST._mutable = True        
            request.POST['status'] = get_status_resolved(id=1)

        form = IncidentForm(request.POST, instance=incident)        

       

        if form.is_valid():
            instance = form.save(commit=False)
            instance.ticket_type = TicketType.objects.get(id=1)
            instance.created_by = request.user.customer
            
            #Set updated field to NOW            
            instance.updated = timezone.now()

            #Get the resolved status for the ticket 
            status_resolved = get_status_resolved(id=1)
            print(status_resolved)
            #If ticket was reopened (changed from 'Resolved' to another status), then increment reopened value by 1
            if incident_status == status_resolved and instance.status != status_resolved:
                instance.reopened += 1
                print('reopened')

            #Resolve ticket if resolve submit button was clicked OR status was set to "resolved" AND text was entered in resolution textbox
            if instance.status == status_resolved and instance.resolution:
                print('resolved')
                instance.resolved = timezone.now()
                instance.status = get_status_resolved(id=1)
                instance.save()

                #Create work note
                work_note_changes = get_object_notes(instance, id=1)
                changes = compare_field_changes(work_note_data, work_note_changes)
                work_note = create_work_note(sysID=instance.sysID, request=request, changes=changes)


                return redirect('incident-detail', number=number) 
            else:
                #If ticket is not being resolved, then clear the data from the resolved field
                if instance.status != get_status_resolved(id=1):
                    instance.resolved = None
            
            #If ticket status is default (ie. Created [order_value=1]), then set the next status (order_value=2)
            if instance.status == get_status_default(id=1):
                instance.status = Status.objects.get(ticket_type=instance.ticket_type, order_value=2)

            instance.save()

            #Create work note
            work_note_changes = get_object_notes(instance, id=1)
            changes = compare_field_changes(work_note_data, work_note_changes)
            work_note = create_work_note(sysID=instance.sysID, request=request, changes=changes)

            #Redirect url based on submit button
            if 'save_stay' in request.POST:
                return redirect('incident-detail', number=number) 
            elif 'save_return' in request.POST:
                return redirect('homepage')

    else:
        form = IncidentForm(instance=incident)

    #Get user roles from group membership
    user_roles = get_user_roles(request)

    #If ticket in closed status, then disable all fields
    if incident.status == get_status_closed(id=1):
        form = disable_form_fields(form)

    context = {
        'incident' : incident,
        'form' : form,
        'work_notes' : work_notes,
        'wn_form' : wn_form,
        'attachments' : attachments,
        'attachment_form' : attachment_form,
        'user_roles' : user_roles,
    } 

    return render(request, 'ticket/incident-detail.html', context)

@login_required(login_url='/access/login')
def load_assignees(request):
    assignment_group_id = request.GET.get('assignment_group')
    grp = ITSMGroup.objects.get(id=assignment_group_id)

    assignees = Customer.objects.filter(itsm_group_membership=grp).order_by('last_name')

    context = {
        'assignees' : assignees,
    }

    return render(request, 'ticket/assignee_select_list_options.html', context)

@login_required(login_url='/access/login')
def incident_search(request):

    incidents = Incident.objects.all()
    inc_filter = IncidentFilter(request.GET, queryset=incidents)
    collapse_filter = False

    #Set search results to filter queryset if search args passed in GET
    #Else set queryset to blank
    if request.GET:
        incidents = inc_filter.qs

        #If assignee__isnull is in request.GET parameters then filter qs where assignee is null
        assignee_isnull = request.GET.get('assignee_isnull')
        if assignee_isnull:
            incidents = incidents.filter(assignee__isnull=True)

        #If collapse_filter, then set to GET parameter
        #Set to True will set the Search Filters accordion to collapse on page load
        collapse_filter = request.GET.get('collapse_filter')

    else:
        incidents = ''

    #If export button -> export data to csv
    if 'export' in request.GET:
        return export_csv(queryset=incidents, obj_type='incident')

    #Get user roles from group membership
    user_roles = get_user_roles(request)

    context = {
        'filter' : inc_filter,
        'incidents' : incidents,
        'collapse_filter' : collapse_filter,
        'user_roles' : user_roles,
        }

    return render(request, 'ticket/incident-search.html', context)

@login_required(login_url='/access/login')
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
    

