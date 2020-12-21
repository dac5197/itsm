import csv

from django.apps import apps
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateformat import format


from .models import *

from access.models import *
from base.forms import *
from base.models import *  
from base.utils import set_sysID_relationship_fields
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

#Close ticket
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
    print(timezone.now())
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

#Create incident
def create_incident(customer, copy_inc_id=None):
    #Create new incident
    incident = Incident.objects.create()

    #Set default values not in model
    incident.status = get_status_default(id=1)
    incident.priority = get_priority_default()
    incident.ticket_type = TicketType.objects.get(id=1)

    if copy_inc_id:
        copy_inc = Incident.objects.get(id=copy_inc_id)
        incident.customer = copy_inc.customer
        incident.phone = copy_inc.phone
        incident.location = copy_inc.location
        incident.priority = copy_inc.priority
        incident.assignment_group = copy_inc.assignment_group
        incident.assignee = copy_inc.assignee
        incident.desc_short = copy_inc.desc_short
        incident.desc_long = copy_inc.desc_long
        incident.resolution = copy_inc.resolution

    #Save new incident
    incident.save()
    
    #Set the relationship fields on the matching sysID
    set_sysID_relationship_fields(incident)

    #Create work note
    if copy_inc_id:
        work_note = create_work_note(sysID=incident.sysID, newly_created=True, customer=customer, copied_ticket=copy_inc)
    else:
        work_note = create_work_note(sysID=incident.sysID, newly_created=True, customer=customer)

    return incident


def export_csv(queryset, obj_type):
    #Dictionary of 'model name : app name'
    #Used for apps.get_model function
    MODEL_APP_DICT = {
		'tickettype' : 'ticket',
		'customer' : 'access',
		'location' : 'access',
		'priority' : 'ticket', 
		'status' : 'ticket',
		'itsmgroup' : 'access',
        'user' : 'auth',
	}

    #Ignore these fields in queryset
    EXCLUDE_FIELDS = ['id','sysID','ticket_ptr', 'profile_image']
    EXCLUDE_FIELD_NAMES = ['id','sysID_id','ticket_ptr_id', 'profile_image']

    #For forieign keys and fields where the name is different than the model or field
    FK_REPLACE_FIELD_NAMES = {
        'assignment_group' : 'itsmgroup',
        'assignee' : 'customer',
        'created_by' : 'customer',
        'manager' : 'customer',
        'ticket_type' : 'tickettype',
    }

    #Replace any field names in the header row of the export with a different name
    HEADER_ROW_REPLACE_FIELD_NAMES ={
        'user' : 'username',
    }

    #Set export filename
    timestamp = format(timezone.now(), 'U')
    file_name = f"{obj_type}-{timestamp}.csv"
    
    #Get field names
    #Ignore field names in EXCLUDE_FIELDS list
    field_names = [field.name for field in queryset.model._meta.fields if not (field.name in EXCLUDE_FIELDS)]
    print(field_names)

    #Replace header row field names with names from dictionary HEADER_ROW_REPLACE_FIELD_NAMES
    field_names = [field.replace(field, HEADER_ROW_REPLACE_FIELD_NAMES[field]) if field in HEADER_ROW_REPLACE_FIELD_NAMES else field for field in field_names ]

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
                        #f_name = f_name.replace('_', '')
                        model = apps.get_model(MODEL_APP_DICT[f_name], f_name)
                        obj = model.objects.get(id=value)
                        value = obj

                #Add value to list (row)
                value_list.append(value)
            
        #Write row
        writer.writerow(value_list)

    return response