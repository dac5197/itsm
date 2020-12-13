import csv

from django.utils import timezone
from django.utils.dateformat import format

from .filters import *
from .models import *

from access.models import *
from base.forms import *
from base.models import *  
from tracking.utils import *

#Return status objects for a ticket type
def get_status_choices(id):
    ticket_type = TicketType.objects.get(id=id)
    statuses = Status.objects.filter(ticket_type=ticket_type).order_by('order_value')
    choices = [(status.id, status.value) for status in statuses]
    return choices

#Return priority objects 
def get_priority_choices():
    priorities = Priority.objects.all().order_by('value')
    choices = [(priority.id, priority.name) for priority in priorities]
    return choices

#Return groups where assignment = True
def get_assignment_group_choices():
    assignment_groups = ITSMGroup.objects.filter(is_assignment=True).order_by('name')
    choices = [(group.id, group.name) for group in  assignment_groups]
    return choices

def get_all_customer_choices():
    customers = Customer.objects.all()
    choices = [(customer.id, customer.__str__()) for customer in  customers]
    return choices

#Return the default status set for a ticket type
def get_status_default(id):
    ticket_type = TicketType.objects.get(id=id)
    status = Status.objects.get(ticket_type=ticket_type, default_value=True)
    return status

#Return the default priority (Medium)
def get_priority_default():
    priority = Priority.objects.get(default_value=True)
    return priority

#Return the resolved status for a ticket type
def get_status_resolved(id):
    ticket_type = TicketType.objects.get(id=id)
    status = Status.objects.filter(ticket_type=ticket_type, resolved_value=True)
    return status

#Return the closed status for a ticket type
def get_status_closed(id):
    ticket_type = TicketType.objects.get(id=id)
    status = Status.objects.filter(ticket_type=ticket_type, closed_value=True)
    return status

#Return the open statuses for a ticket type
#Open status is any status that is not resolved or closed
def get_status_open(id):
    ticket_type = TicketType.objects.get(id=id)
    statuses = Status.objects.filter(ticket_type=ticket_type, closed_value=False, resolved_value=False)
    return statuses

