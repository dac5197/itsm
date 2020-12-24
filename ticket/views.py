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
from access.utils import get_user_roles, get_sidebar_items
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

    #Create incident
    incident = create_tsm_object(customer=request.user.customer, obj_app='ticket', obj_model='incident')
   
    #Redirect to the incident's url
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

            #If ticket was reopened (changed from 'Resolved' to another status), then increment reopened value by 1
            if incident_status == status_resolved and instance.status != status_resolved:
                instance.reopened += 1

            #Resolve ticket if resolve submit button was clicked OR status was set to "resolved" AND text was entered in resolution textbox
            if instance.status == status_resolved and instance.resolution:
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
            if 'create_copy' in request.POST:
                new_incident = create_tsm_object(customer=request.user.customer, obj_app='ticket', obj_model='incident', copy_obj_id=instance.id)
                new_inc_detail_url = '/ticket/incident-detail/' + new_incident.number
                return redirect(new_inc_detail_url)
            elif 'save_stay' in request.POST:
                return redirect('incident-detail', number=number) 
            elif 'save_return' in request.POST:
                return redirect('homepage')

    else:
        form = IncidentForm(instance=incident)

    #If ticket in closed status OR 
    #If user is NOT a member of the assignment group, does NOT have the Service Desk role, and is NOT an admin:
    #   Then disable all fields
    if incident.status == get_status_closed(id=1) or not (incident.assignment_group in ITSMGroup.objects.filter(members=request.user.customer) or 'Service Desk' in request.user.customer.roles or 'TSM Admin' in request.user.customer.roles or request.user.is_staff):
        form = disable_form_fields(form)

    context = {
        'incident' : incident,
        'form' : form,
        'work_notes' : work_notes,
        'wn_form' : wn_form,
        'attachments' : attachments,
        'attachment_form' : attachment_form,
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

    context = {
        'filter' : inc_filter,
        'incidents' : incidents,
        'collapse_filter' : collapse_filter,
    }

    return render(request, 'ticket/incident-search.html', context)

@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
def request_create(request):

    #Create incident
    req = create_tsm_object(customer=request.user.customer, obj_app='ticket', obj_model='request')
   
    #Redirect to the incident's url
    return redirect('request-detail', number=req.number)

@login_required(login_url='/access/login')
def request_detail(request, number):
    req = Request.objects.get(number=number)
    form = RequestForm(instance=req)

    #Get initial field values for work notes
    work_note_data = get_object_notes(req)
    work_notes = WorkNote.objects.filter(foreign_sysID=req.sysID).order_by('-created')
    wn_form = WorkNoteForm()

    #Get inital field values
    req_status = req.status

    #Get attachments
    attachments = Attachment.objects.filter(foreign_sysID=req.sysID).order_by('-id')
    attachment_form = AttachmentForm()

    ### POST ###
    if request.method == 'POST':
        
        #Add attachment to ticket
        if 'add_attachment' in request.POST:

            #Save attachment
            attachment_form = add_attachment(request=request, obj=req)
            
            #If any errors then display in inc form 
            if attachment_form.errors:
                context = {
                    'req' : req,
                    'form' : form,
                    'work_notes' : work_notes,
                    'wn_form' : wn_form,
                    'attachments' : attachments,
                    'attachment_form' : attachment_form,
                } 

                return render(request, 'ticket/request-detail.html', context)
            
            #Return to INC
            else:
                return redirect('request-detail', number=number)

        #If Resolve button was clicked, then change status to 'resolved' before checking if form is valid
        if 'resolve' in request.POST:
            request.POST._mutable = True        
            request.POST['status'] = get_status_resolved(id=2)

        form = RequestForm(request.POST, instance=req)        

        if form.is_valid():
            instance = form.save(commit=False)
            instance.ticket_type = TicketType.objects.get(id=2)
            instance.created_by = request.user.customer
            
            #Set updated field to NOW            
            instance.updated = timezone.now()

            #Get the resolved status for the ticket 
            status_resolved = get_status_resolved(id=2)

            #If ticket was reopened (changed from 'Resolved' to another status), then increment reopened value by 1
            if req_status == status_resolved and instance.status != status_resolved:
                instance.reopened += 1

            #Resolve ticket if resolve submit button was clicked OR status was set to "resolved" AND text was entered in resolution textbox
            if instance.status == status_resolved and instance.fulfillment_notes:
                instance.fulfilled = timezone.now()
                instance.status = get_status_resolved(id=2)
                instance.save()

                #Create work note
                work_note_changes = get_object_notes(instance, id=2)
                changes = compare_field_changes(work_note_data, work_note_changes)
                work_note = create_work_note(sysID=instance.sysID, request=request, changes=changes)

                return redirect('request-detail', number=number) 
                
            else:
                #If ticket is not being resolved, then clear the data from the resolved field
                if instance.status != get_status_resolved(id=2):
                    instance.fulfilled = None
            
            #If ticket status is default (ie. Created [order_value=1]), then set the next status (order_value=2)
            if instance.status == get_status_default(id=2):
                instance.status = Status.objects.get(ticket_type=instance.ticket_type, order_value=2)

            instance.save()

            #Create work note
            work_note_changes = get_object_notes(instance, id=2)
            changes = compare_field_changes(work_note_data, work_note_changes)
            work_note = create_work_note(sysID=instance.sysID, request=request, changes=changes)

            #Redirect url based on submit button
            if 'create_copy' in request.POST:
                new_incident = create_incident(customer=request.user.customer, obj_app='ticket', obj_model='incident', copy_obj_id=instance.id)
                return redirect('request-detail', number=new_incident.number)
            elif 'save_stay' in request.POST:
                return redirect('request-detail', number=number) 
            elif 'save_return' in request.POST:
                return redirect('homepage')

    else:
        form = RequestForm(instance=req)

    #If ticket in closed status OR 
    #If user is NOT a member of the assignment group, does NOT have the Service Desk role, and is NOT an admin:
    #   Then disable all fields
    if req.status == get_status_closed(id=1) or not (req.assignment_group in ITSMGroup.objects.filter(members=request.user.customer) or 'Service Desk' in request.user.customer.roles or 'TSM Admin' in request.user.customer.roles or request.user.is_staff):
        form = disable_form_fields(form)

    context = {
        'req' : req,
        'form' : form,
        'work_notes' : work_notes,
        'wn_form' : wn_form,
        'attachments' : attachments,
        'attachment_form' : attachment_form,
    } 

    return render(request, 'ticket/request-detail.html', context)
    

