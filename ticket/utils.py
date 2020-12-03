import csv

from django.utils import timezone
from django.utils.dateformat import format

from .filters import *
from .models import *
  

def increment_ticket_number(prefix, id):
    number = prefix + str(id).zfill(7)
    return number

def increment_inc_number():
    try:
        last_inc_id = Incident.objects.all().order_by('id').last().id
        last_inc_id += 1
    except:
        last_inc_id = 1
    return increment_ticket_number('INC', last_inc_id)  

def increment_pwrst_number():
    try:
        last_pwrst_id = PasswordReset.objects.all().order_by('id').last().id
        last_pwrst_id += 1
    except:
        last_pwrst_id = 1
    return increment_ticket_number('PWRST', last_pwrst_id)  

def increment_req_number():
    try:
        last_id = Request.objects.all().order_by('id').last().id
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('REQ', last_id)  

def increment_out_number():
    try:
        last_id = Outage.objects.all().order_by('id').last().id
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('OUT', last_id)  

def get_status_choices(id):
    ticket_type = TicketType.objects.get(id=id)
    statuses = Status.objects.filter(ticket_type=ticket_type).order_by('order_value')
    choices = [(status.id, status.value) for status in statuses]
    return choices

def get_priority_choices():
    priorities = Priority.objects.all().order_by('value')
    choices = [(priority.id, priority.name) for priority in priorities]
    return choices

def get_assignment_group_choices():
    assignment_groups = Group.objects.filter(is_assignment=True).order_by('name')
    choices = [(group.id, group.name) for group in  assignment_groups]
    return choices

def get_status_default(id):
    ticket_type = TicketType.objects.get(id=id)
    status = Status.objects.get(ticket_type=ticket_type, default_value=True)
    return status

def get_priority_default():
    priority = Priority.objects.get(default_value=True)
    return priority

def get_status_resolved(id):
    ticket_type = TicketType.objects.get(id=id)
    status = Status.objects.get(ticket_type=ticket_type, resolved_value=True)
    return status


#Export queryset to csv
#https://stackoverflow.com/a/63228849
def export_query_to_csv(queryset, qs_type='items', **override):
    timestamp = format(timezone.now(), 'U')

    file_name = f"{qs_type}-{timestamp}.csv"
    field_names = [field.name for field in queryset.model._meta.fields]
    
    def field_value(row, field_name):
        if field_name in override.keys():
            return override[field_name]
        else:
            return row[field_name]

    with open(file_name, 'w') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL, delimiter=',')
        writer.writerow(field_names)  # write the header

        for row in queryset.values(*field_names):
            writer.writerow([field_value(row, field) for field in field_names])

