from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import *
from .models import *
from .utils import *

from base.utils import set_sysID_relationship_fields
from ticket.models import Incident, PasswordReset, Request
from ticket.utils import get_status_open, get_status_resolved

# Create your views here.



def register_account(request):

    if request.method == 'POST':
        form = CreateUserForm(request.POST)

        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')

            customer = Customer.objects.filter(user=user)

            if customer:
                return redirect('login')
            else:
                return redirect(f'/access/register-profile/{user.id}')
    else:
        form = CreateUserForm(initial={'username': create_sso()})
    
    bg_img = get_random_bg_img('backgrounds')

    context = {
        'bg_img' : bg_img, 
        'form' : form
    }

    return render(request, 'access/register-account.html', context)

def register_profile(request, id):
    user = User.objects.get(id=id)

    if request.method == 'POST':
        
        #Edit request to set the User and Active fields
        request.POST._mutable = True        
        request.POST['user'] = user
        request.POST['active'] = True
        
        form = CustomerForm(request.POST)
    
        if form.is_valid():
            instance = form.save()
            
            #Set User email to match Customer email
            user.email = instance.email
            user.save()

            #Create new sysID for Customer and set the relationship fields
            instance.sysID = SysID.objects.create()
            instance.save()
            set_sysID_relationship_fields(instance)

            #Registration complete - redirect to login page
            return redirect('/access/login')
    else:
        form = CustomerForm(initial={'email':user.email})

    bg_img = get_random_bg_img('backgrounds')

    context = {
        'bg_img' : bg_img, 
        'form' : form,
    }
    
    return render(request, 'access/register-profile.html', context)


def group_tree(request):
    group_list = ITSMGroup.objects.all()
   
    group_tree = create_tree_list(qs=group_list, max_depth=5)

    context = {
        'group_tree' : group_tree
    }

    return render(request, 'access/group-tree.html', context)

def homepage(request):
    three_days_ago = timezone.now()-timezone.timedelta(days=3)
    three_days_ago = three_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

    new_inc = Incident.objects.filter(customer=request.user.customer, created__gt=three_days_ago)
    open_inc = Incident.objects.filter(customer=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(customer=request.user.customer, status=get_status_resolved(id=1))


    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
    }

    return render(request, 'access/homepage.html', context)

def homepage_assigned_to_me(request):
    three_days_ago = timezone.now()-timezone.timedelta(days=3)
    three_days_ago = three_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

    new_inc = Incident.objects.filter(assignee=request.user.customer, created__gt=three_days_ago)
    open_inc = Incident.objects.filter(assignee=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(assignee=request.user.customer, status=get_status_resolved(id=1))


    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
    }

    return render(request, 'access/homepage-assignedtome.html', context)

def homepage_assigned_to_my_groups(request):
    three_days_ago = timezone.now()-timezone.timedelta(days=3)
    three_days_ago = three_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

    new_inc = Incident.objects.filter(assignee=request.user.customer, created__gt=three_days_ago)
    open_inc = Incident.objects.filter(assignee=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(assignee=request.user.customer, status=get_status_resolved(id=1))


    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
    }

    return render(request, 'access/homepage-assignedtomygroups.html', context)