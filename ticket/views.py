from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse

import datetime
import json

from rest_framework.decorators import api_view
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_api.serializers import IncidentSerializer

from .models import *
from .forms import *
from .utils import *

from access.models import *
from tracking.forms import *
from tracking.models import *
from tracking.utils import *

# Create your views here.

def incident(request):
    form = IncidentForm()
    context = {'form' : form}

    return render(request, 'ticket/incident.html', context)

def incident_create(request):
    #Create new incident
    number = increment_inc_number()
    incident = Incident.objects.create()

    #Set default values not in model
    incident.status = get_status_default(id=1)
    incident.priority = get_priority_default()
    incident.ticket_type = TicketType.objects.get(id=1)

    #Save new incident
    incident.save()
    
    work_note = WorkNote.objects.create(foreign_sysID=incident.sysID)
    created_dict = get_created_dict()
    for key, value in created_dict.items():
            FieldChange.objects.create(work_note_id=work_note, field=key, old_value=value['old_value'], new_value=value['new_value'])

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

    context = {
        'incident' : incident,
        'form' : form,
        'wn_form' : wn_form,
        'work_notes' : work_notes
    }

    ### POST ###
    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)        
        
        
        if form.is_valid():
            #print("INC form is valid")
            #print(f"120 inc: {vars(incident2)}")
            instance = form.save(commit=False)
            #print(f"122 ins: {vars(instance)}")
            instance.ticket_type = TicketType.objects.get(id=1)
            work_note_changes = get_object_notes(instance, id=1)
            #print(f"CHANGED: {work_note_changes}")
            changes = compare_field_changes(work_note_data, work_note_changes)

            work_note = None

            if changes:
                work_note = WorkNote.objects.create(foreign_sysID=instance.sysID, changed_data=changes)
            
            wn_form = WorkNoteForm(request.POST)
            wn_instance = wn_form.save(commit=False)

            if wn_instance.notes:
                if work_note == None:
                    work_note = WorkNote.objects.create(foreign_sysID=instance.sysID) 
                work_note.notes = wn_instance.notes
                work_note.customer_visible = wn_instance.customer_visible
                work_note.save()

            for change, value in changes.items():
                print(f"change: {change}")
                print(f"value: {value['old_value']}")
                FieldChange.objects.create(work_note_id=work_note, field=change, old_value=value['old_value'], new_value=value['new_value'])
            instance.updated = timezone.now()
            status_resolved = get_status_resolved(id=1)

            #If ticket was reopened (changed from 'Resolved' to another status), then increment reopened value by 1
            if incident_status == status_resolved and instance.status != status_resolved:
                instance.reopened += 1

            if ('resolve' in request.POST or instance.status == status_resolved) and instance.resolution:
                print('resolve')
                #instance.resolution.required = True
                #form.fields['resolution'].required = True
                instance.resolved = timezone.now()
                instance.status = get_status_resolved(id=1)
                instance.save()
                return redirect('incident-detail', number=number) 
            else:
                if instance.status != get_status_resolved(id=1):
                    instance.resolved = None
            
            instance.save()

            if 'save_stay' in request.POST:
                print('save and stay')
                return redirect('incident-detail', number=number) 
            elif 'save_return' in request.POST:
                print('save and return')
                return redirect('incident')

        else:
            print(form.errors)
            return redirect('incident-detail', number=number) 



    return render(request, 'ticket/incident-detail.html', context)
