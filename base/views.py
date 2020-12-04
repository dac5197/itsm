import os

from django.shortcuts import render, redirect

from .models import *

# Create your views here.

def home(request):
    return render(request, 'base/home.html')

def create_sysid(request):
    sys_id = SysID.objects.create()
    return sys_id

#Remove attachment from ticket:
def remove_attachment(request, id, number):
    attachment = Attachment.objects.get(id=id)
    
    #Delete attachment from media/attachments
    if os.path.exists(attachment.document.path):
        os.remove(attachment.document.path)
    else:
        print("The file does not exist") 

    #Delete attachment object
    attachment.delete()

    #Then redirect back to ticket
    return redirect('incident-detail', number=number) 