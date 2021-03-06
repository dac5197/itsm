import json

from django.contrib.auth.models import User

from .forms import *
from .models import *

from access.models import *

#Create a dictionary of object fields 
#Fields recorded are determined by the related Watcher object
def get_object_notes(obj, id=None):

    #Get object ticket type
    if id:
        ticket_type = TicketType.objects.get(id=id)
    else:
        ticket_type = TicketType.objects.get(id=obj.ticket_type.id)

    #Get dictionary of field names from watcher model
    watcher = Watcher.objects.get(ticket_type=ticket_type)

    #For each field in object, if field and watcher match, then add field, value to dictionary
    work_note_data = {}
    for field in obj._meta.get_fields():
        if field.name in watcher.watch_fields:
            value = getattr(obj, field.name)
            work_note_data.update({field.name : value})
    
    return work_note_data

#Compare two dictionaries of object fields and return a new dictionary of the changed field
def compare_field_changes(old_dict, new_dict):

    #Get changes where field is in both old_dict and new_dict
    data_set_old_dict = set(old_dict.items())
    data_set_new_dict = set(new_dict.items())
    field_changes = data_set_new_dict ^ data_set_old_dict

    #Create note dictionary for each field change
    #Format:    {
    #               'field1': 
    #                   {
    #                       'old_value1': 'value1', 
    #                       'new_value1': 'value1',
    #                   },
    #               'field2': 
    #                   {
    #                       'old_value2': 'value2', 
    #                       'new_value2': 'value2',
    #                   },
    #           }

    notes = {}
    for change in field_changes:

        if change in data_set_old_dict:
            field_name = change[0]
            old_value = change[1].__str__()

            if field_name in notes:
                notes[field_name]['old_value'] = old_value
            else:
                notes.update({field_name : {'old_value' : old_value, 'new_value' : 'x'}})
                
        else:
            field_name = change[0]
            new_value = change[1].__str__()

            if field_name in notes:
                notes[field_name]['new_value'] = new_value
            else:
                notes.update({field_name : {'old_value' : 'x', 'new_value' : new_value}})
                
    return notes

#Create dictionary for newly created items
def get_created_dict():
    created_dict = {'status': {'old_value': '', 'new_value': 'Created'}}
    return created_dict

def get_copied_dict(copied_ticket):
    copied_dict = {'status': {'old_value': '', 'new_value': f'Copied from {copied_ticket.number}'}}
    return copied_dict

#Create work note and related field objects
def create_work_note(sysID, request=None, changes=None, newly_created=False, attachment=False, customer=None, copied_ticket=None):

    #If customer is none, then set customer to request.user
    if customer is None:
        customer = Customer.objects.get(user=request.user)

    if attachment or newly_created:
        #Create work note for newly created ticket
        #Set only change as Status from Blank to Created
        work_note = WorkNote.objects.create(foreign_sysID=sysID, note_taker=customer)
        
        #Get dict of copied ticket or newly created ticket
        if newly_created:
            if copied_ticket:
                changes = get_copied_dict(copied_ticket=copied_ticket)
            else:
                changes = get_created_dict()
        
        work_note.changed_data = changes
        #work_note.note_taker = Customer.objects.get(user=request.user)
        work_note.save()

        #Create field changes for each change
        for key, value in changes.items():
                FieldChange.objects.create(work_note_id=work_note, field=key, old_value=value['old_value'], new_value=value['new_value'])
    #Create work note for existing ticket
    else:        
        #Declare work_note and set to none
        work_note = None

        #If data in changes, then create work note for the field changes
        if changes:
            work_note = WorkNote.objects.create(foreign_sysID=sysID, changed_data=changes, note_taker=customer)
        
            #Create field changes for each change
            for change, value in changes.items():
                FieldChange.objects.create(work_note_id=work_note, field=change, old_value=value['old_value'], new_value=value['new_value'])

        #If request is passed:
        #   Set the work note form
        #   If anything in notes field, then create separate work note
        if request:
            wn_form = WorkNoteForm(request.POST)
            wn_instance = wn_form.save(commit=False)

            #If text in notes, then create separate work note
            if wn_instance.notes:
                if work_note == None:
                    work_note = WorkNote.objects.create(foreign_sysID=sysID, note_taker=customer) 
                work_note.notes = wn_instance.notes
                work_note.customer_visible = wn_instance.customer_visible
                work_note.save()

    return work_note
    