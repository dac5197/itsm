import csv
from crispy_forms.helper import FormHelper

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
def get_status_choices(id=None, ticket_type=None):
    if id and not ticket_type:
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

#Create object based on the app and model
def create_tsm_object(customer, obj_app, obj_model, copy_obj_id=None):
    #Create new object
    model = apps.get_model(obj_app, obj_model)
    obj = model.objects.create()

    #Set default values not in model
    if obj_app == 'ticket':
        ticket_type = TicketType.objects.get(name__iexact=obj_model)
        obj.status = get_status_default(id=ticket_type.id)
        obj.priority = get_priority_default()
        obj.ticket_type = ticket_type

    #If new object is a copy, then loop through the field list and set the initial values for the new object
    if copy_obj_id:
        copy_obj = model.objects.get(id=copy_obj_id)
        for field in CopyList.objects.get(name__iexact=obj_model).fields:
            setattr(obj, field, getattr(copy_obj, field))

    #Save new incident
    obj.save()
    
    #Set the relationship fields on the matching sysID
    set_sysID_relationship_fields(obj)

    #Create work note
    if copy_obj_id:
        work_note = create_work_note(sysID=obj.sysID, newly_created=True, customer=customer, copied_ticket=copy_obj)
    else:
        work_note = create_work_note(sysID=obj.sysID, newly_created=True, customer=customer)

    return obj


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
    EXCLUDE_FIELDS = ['id', 'sysID', 'ticket_ptr', 'profile_image', 'group_ptr',]
    EXCLUDE_FIELD_NAMES = ['id', 'sysID_id', 'ticket_ptr_id', 'profile_image', 'group_ptr_id']

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
        writer.writerow(value_list, )

    return response

#Set form widget attributes
def set_ticket_form_widgets(completion_field_name):
    widget_dict = {
         #Set fields to readonly (disabled)
            'number' : forms.TextInput(attrs={'readonly':'readonly'}),
            'closed' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'created' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'created_by' : forms.TextInput(attrs={'readonly':'readonly'}),
            'reopened' : forms.TextInput(attrs={'readonly':'readonly'}),
            f'{completion_field_name}' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            'updated' : forms.DateTimeInput(attrs={'readonly':'readonly'}, format='%m/%d/%Y %H:%M'),
            
            #Set 'active' boolean to a readonly textbox
            'active' : forms.TextInput(attrs={'readonly':'readonly'}),    
    }

    return widget_dict

#Set form field labels, select choices, and required attribute
def set_ticket_form_defaults(form, ticket_type_id):
    form.helper = FormHelper()
    form.helper.form_method = 'POST'

    #Change form label names
    form.fields['desc_short'].label = 'Short Description'
    form.fields['desc_long'].label = 'Detailed Description'
    form.fields['reopened'].label = 'Reopened Count'

    #Set values for status select fields from database
    form.fields['status'].choices = get_status_choices(id=ticket_type_id)
    form.fields['priority'].choices = get_priority_choices()
    form.fields['assignment_group'].choices = get_assignment_group_choices()

    #Set required fields
    form.fields['customer'].required = True
    form.fields['status'].required = True
    form.fields['priority'].required = True
    form.fields['assignment_group'].required = True

    #Set not required fields
    form.fields['assignee'].required = False

    #Remove select default (empty label) option
    form.fields['priority'].empty_label = None


    #Clear values for the assignee select
    form.fields['assignee'].queryset = Customer.objects.none()

    #Set values for the assignee select:
    #   If POST, get assignment group ID from request data
    #   Else, get assignment group ID from form instance
    #Get group membership and populated assignee select
    #https://simpleisbetterthancomplex.com/tutorial/2018/01/29/how-to-implement-dependent-or-chained-dropdown-list-with-django.html
    if 'assignment_group' in form.data:
        try:
            assignment_group_id = int(form.data.get('assignment_group'))
            grp = ITSMGroup.objects.get(id=assignment_group_id)
            form.fields['assignee'].queryset = Customer.objects.filter(itsm_group_membership=grp).order_by('last_name')
        except (ValueError, TypeError):
            pass  # invalid input from the client; ignore and fallback to empty City queryset
    elif form.instance.pk:
        assignment_group = form.instance.assignment_group
        if assignment_group:
            grp = ITSMGroup.objects.get(id=assignment_group.id)
            form.fields['assignee'].queryset = Customer.objects.filter(itsm_group_membership=grp).order_by('last_name')
        else:
            form.fields['assignment_group'].initial = '---------'

    return form

#Throw error if ticket will be in resolved status and completion_field has not data
def validate_completion_notes(form, cleaned_data, completion_field, ticket_type_id):
    
    status = cleaned_data.get('status')
    completion_field_value = cleaned_data.get(f'{completion_field}')

    resolved_status = get_status_resolved(id=ticket_type_id)

    if status == resolved_status and  completion_field_value == '':
        msg = "This field is required when resolving an incident."
        form.add_error(f'{completion_field}', msg)

    return form
