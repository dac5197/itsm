from django.apps import apps

from .forms import AttachmentForm
from .models import Attachment, SysID

from access.models import *
from ticket.models import *
from tracking.utils import create_work_note

#Add attachment and create worknote
def add_attachment(request, obj):
    attachment_form = AttachmentForm(request.POST, request.FILES)

    if attachment_form.is_valid():
        attachment_instance = attachment_form.save(commit=False)
        attachment = Attachment.objects.create(foreign_sysID=obj.sysID, document=attachment_instance.document)
        attachment_wn_dict = {'Attachments': {'old_value': 'Add', 'new_value': attachment_instance}}
        create_work_note(sysID=obj.sysID, changes=attachment_wn_dict, attachment=True, request=request)
       

    return attachment_form

#Set the relationship fields (id, name) on an object's sysID
def set_sysID_relationship_fields(obj):
    sysID = obj.sysID
    sysID.rel_obj_id = obj.id
    sysID.rel_obj_model = obj.__class__.__name__
    sysID.rel_obj_name = obj.__str__()
    sysID.save()

#Set the relationship fields for all models with a one-to-one relationship
def set_all_sysIDs_relationship_fields():

    #Dictionary of model : app 
    APP_MODEL_DICT = {
        'customer' : 'access',
        'itsmgroup' : 'access',
        'location' : 'access',
        'role' : 'access',
        'priority' : 'ticket',
		'tickettype' : 'ticket',
        'status' : 'ticket',
        'incident' : 'ticket',
        'passwordreset' : 'ticket',
        'request' : 'ticket',
        'outage' : 'ticket',
        'board' : 'kanban',
        'lane' : 'kanban',
        'card' : 'kanban',
	}

    #For each model, app in dict, get the model and then get a queryset of all objects
    for m, a in APP_MODEL_DICT.items():
        print(f'app: {a} / model: {m}')
        model = apps.get_model(a, m)
        all_obj = model.objects.all()

        #For each object, set the sysID relationship fields
        for obj in all_obj:
            print(f'obj: {obj.id} - {obj.__str__()}')

            #If object does not have a sysID, then create one
            if not obj.sysID:
                print('SysID not found - creating new one...')
                obj.sysID = SysID.objects.create()
                obj.save()

            set_sysID_relationship_fields(obj)


    #Complete
    print('complete')
