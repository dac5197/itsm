import os

from django.shortcuts import render, redirect

from .models import *

from tracking.utils import create_work_note

# Create your views here.

def home(request):
    return render(request, 'base/home.html')

def create_sysid(request):
    sys_id = SysID.objects.create()
    return sys_id

#Remove attachment from ticket:
def remove_attachment(request, id, number, url):
    attachment = Attachment.objects.get(id=id)
    
    #Delete attachment from media/attachments
    if os.path.exists(attachment.document.path):
        os.remove(attachment.document.path)
    else:
        print("The file does not exist") 

    #Create work note
    #attachment_wn_dict = {'Attachments': {'old_value': 'Remove', 'new_value': attachment.doc_name}}
    #create_work_note(obj=obj, changes=attachment_wn_dict, attachment=True)

    #Delete attachment object
    attachment.delete()

    #Then redirect back to ticket
    return redirect(url, number=number) 

