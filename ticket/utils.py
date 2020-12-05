import csv

from django.utils import timezone
from django.utils.dateformat import format

from .filters import *
from .models import *

from base.forms import *
from base.models import *  
from tracking.utils import *

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


def add_attachment(request, obj):
    attachment_form = AttachmentForm(request.POST, request.FILES)

    if attachment_form.is_valid():
        attachment_instance = attachment_form.save(commit=False)
        Attachment.objects.create(foreign_sysID=obj.sysID, document=attachment_instance.document)
        attachment_wn_dict = {'Attachments': {'old_value': 'Add', 'new_value': attachment_instance}}
        create_work_note(sysID=obj.sysID, changes=attachment_wn_dict, attachment=True)

