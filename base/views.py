import os

from django.shortcuts import render, redirect

from .models import *
from .utils import set_all_sysIDs_relationship_fields

from tracking.utils import create_work_note

# Create your views here.

def home(request):
    return render(request, 'access/homepage.html')

def create_sysid(request):
    sys_id = SysID.objects.create()
    return sys_id

#Remove attachment from ticket:
def remove_attachment(request, id, number, url, sysID):
    attachment = Attachment.objects.get(id=id)
    
    #Delete attachment from media/attachments
    if os.path.exists(attachment.document.path):
        os.remove(attachment.document.path)
    else:
        print("The file does not exist") 

    #Create work note
    attachment_wn_dict = {'Attachments': {'old_value': 'Remove', 'new_value': attachment.doc_name}}
    obj_sysID = SysID.objects.get(sysID=sysID)
    create_work_note(sysID=obj_sysID, changes=attachment_wn_dict, attachment=True, request=request)

    #Delete attachment object
    attachment.delete()

    #Then redirect back to ticket
    return redirect(url, number=number) 

def admin_panel(request):
    if request.GET.get('set_all_sysID_rel_fields'):
        set_all_sysIDs_relationship_fields()
        return redirect('admin-panel')

    return render(request, 'base/admin-panel.html')



