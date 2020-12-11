from .forms import AttachmentForm
from .models import Attachment, SysID

from tracking.utils import create_work_note

#Add attachment and create worknote
def add_attachment(request, obj):
    attachment_form = AttachmentForm(request.POST, request.FILES)

    if attachment_form.is_valid():
        attachment_instance = attachment_form.save(commit=False)
        attachment = Attachment.objects.create(foreign_sysID=obj.sysID, document=attachment_instance.document)
        attachment_wn_dict = {'Attachments': {'old_value': 'Add', 'new_value': attachment_instance}}
        create_work_note(sysID=obj.sysID, changes=attachment_wn_dict, attachment=True, request=request)

#Set the relationship fields (id, name) on an object's sysID
def set_sysID_relationship_fields(obj):
    sysID = obj.sysID
    sysID.rel_obj_id = obj.id
    sysID.rel_obj_model = obj.__class__.__name__
    sysID.rel_obj_name = obj.__str__()
    sysID.save()