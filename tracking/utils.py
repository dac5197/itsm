import json
from .models import *

def record_work_note_field_changes(field_name, old_value, new_value):
    work_note_json = {
            "field" : field_name,
            "old_value" : old_value,
            "new_value" : new_value
    }

    return work_note_json

def get_object_notes(obj, id=None):

    if id:
        ticket_type = TicketType.objects.get(id=id)
    else:
        ticket_type = TicketType.objects.get(id=obj.ticket_type.id)

    watcher = Watcher.objects.get(ticket_type=ticket_type)
    work_note_data = {}
    #work_note_json = {}
    for field in obj._meta.get_fields():
        if field.name in watcher.watch_fields:
            value = getattr(obj, field.name)
            work_note_data.update({field.name : value})
            
            #print(work_note_data)

            #work_note_json.update(data)
    
    return work_note_data


def compare_field_changes(old_dict, new_dict):
    data_set_old_dict = set(old_dict.items())
    data_set_new_dict = set(new_dict.items())
    field_changes = data_set_new_dict ^ data_set_old_dict

    print(data_set_old_dict)

    notes = {}

    for change in field_changes:
        if change in data_set_old_dict:
            print(f"old key: {change}")
            
            
            field_name = change[0]
            old_value = change[1].__str__()

            print(f"old key: {field_name}")
            print(f"old value: {old_value}")

            if field_name in notes:
                notes[field_name]['old_value'] = old_value
                #notes['old_value'] = old_value
            else:
                notes.update({field_name : {'old_value' : old_value, 'new_value' : 'x'}})
                #notes.update({'field' : field_name, 'old_value' : old_value, 'new_value' : 'x'})
        else:
            print(f"new key: {change}")
            field_name = change[0]
            new_value = change[1].__str__()
            print(f"new value: {new_value}")

            if field_name in notes:
                notes[field_name]['new_value'] = new_value
                #notes['new_value'] = new_value
            else:
                notes.update({field_name : {'old_value' : 'x', 'new_value' : new_value}})
                #notes.update({'field' : field_name, 'old_value' : 'x', 'new_value' : new_value})

    print(f"notes: {notes}")

    return notes

def get_created_dict():
    created_dict = {'status': {'old_value': '', 'new_value': 'Created'}}
    return created_dict