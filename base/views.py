import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import *
from .utils import set_all_sysIDs_relationship_fields

from access.decorators import admin_only, allowed_users
from access.forms import GroupForm
from access.models import ITSMGroup
from access.utils import cascade_roles
from ticket.utils import set_resolved_tickets_closed
from tracking.utils import create_work_note

# Create your views here.
@login_required(login_url='/access/login')
def home(request):
    return redirect('access/homepage')

#Create a new sysid object
@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
def create_sysid(request):
    sys_id = SysID.objects.create()
    return sys_id

#Remove attachment from ticket:
@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
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

@login_required(login_url='/access/login')
@admin_only
def admin_panel(request):

    if request.method == 'POST':
        #Set all relationship fiels for SysID
        if 'set_all_sysID_rel_fields' in request.POST:
            set_all_sysIDs_relationship_fields()
            return redirect('admin-panel')

        #Cascade roles for group to all descendants
        if request.POST.get('cascade_group_roles'):
            grp = ITSMGroup.objects.get(id=request.POST['tsm_group'])
            cascade_roles(grp)
            return redirect('admin-panel')

        if request.POST.get('set_resolved_to_closed'):
            set_resolved_tickets_closed()
            return redirect('admin-panel')


    form = GroupForm()

    context = {
        'form' : form,
    }

    return render(request, 'base/admin-panel.html', context)



