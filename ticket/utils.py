import csv

from django.utils import timezone
from django.utils.dateformat import format


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
    #Insert null value
    choices.insert(0,('', '---------'))
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
def get_status_resolved(id, return_qs=False):
    ticket_type = TicketType.objects.get(id=id)
    #Return queryset if true, else return status object
    if return_qs:
        status = Status.objects.filter(ticket_type=ticket_type, resolved_value=True)
    else:
        status = Status.objects.get(ticket_type=ticket_type, resolved_value=True)
    return status

#Return the closed status for a ticket type
def get_status_closed(id, return_qs=False):
    ticket_type = TicketType.objects.get(id=id)
    if return_qs:
        status = Status.objects.filter(ticket_type=ticket_type, closed_value=True)
    else:
        status = Status.objects.get(ticket_type=ticket_type, closed_value=True)
    return status

#Return the open statuses for a ticket type
#Open status is any status that is not resolved or closed
def get_status_open(id):
    ticket_type = TicketType.objects.get(id=id)
    statuses = Status.objects.filter(ticket_type=ticket_type, closed_value=False, resolved_value=False)
    return statuses

#Set all fields in a form as disabled
def disable_form_fields(form):
    for field, field_type in form.fields.items():
        form.fields[field].widget.attrs['disabled'] = True
    
    return form

def close_ticket(ticket, ticket_type):
    #Create dictionary of initial field values
    wn_initial = get_object_notes(obj=ticket, id=ticket_type.id)
    
    #Change ticket to closed and active to false
    ticket.status = get_status_closed(id=ticket_type.id)
    ticket.active = False
    ticket.save()

    #Create dictionary of changed field values
    wn_changed = get_object_notes(obj=ticket, id=ticket_type.id)
    #Compare dictionaries and return the changes
    changes = compare_field_changes(wn_initial, wn_changed)
    #Create work note of the changes as user: TSM_System
    work_note = create_work_note(sysID=ticket.sysID, changes=changes, customer=Customer.objects.get(email='TSM_System@dacme.com'))

    return ticket

#Set all resolved tickets to cloed with resolved date older than 3 days
def set_resolved_tickets_closed():
    #Get resolved status
    resolved_statuses = status = Status.objects.filter(resolved_value=True)
    #Get all ticket types
    ticket_types = TicketType.objects.all()

    #Set the resolved min date
    DAYS = 3
    ticket_resolved_min_date = timezone.now()-timezone.timedelta(days=DAYS)
    ticket_resolved_min_date = ticket_resolved_min_date.replace(hour=0, minute=0, second=0, microsecond=0)

    #For each tickt type:
    #   Get all tickets for that type
    #   For each of those tickets:
    #   If status is resolved and resolved date is olded than the resolved min date, then:
    #       Set status to closed and active to false
    for ticket_type in ticket_types:
        tickets = (apps.get_model('ticket', ticket_type.name)).objects.all()

        for ticket in tickets:
            if ticket.__class__.__name__ == 'Request':
                if ticket.status in resolved_statuses and ticket.fulfilled < ticket_resolved_min_date:
                        ticket = close_ticket(ticket=ticket, ticket_type=ticket_type)
                        print(f'Ticket {ticket.number} set to closed')
            else:
                if ticket.status in resolved_statuses and ticket.resolved < ticket_resolved_min_date:
                    ticket = close_ticket(ticket=ticket, ticket_type=ticket_type)
                    print(f'Ticket {ticket.number} set to closed')