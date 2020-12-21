import os

from django.apps import apps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.shortcuts import render, redirect
from django.utils import timezone

from .decorators import *
from .forms import *
from .models import *
from .utils import *

from base.utils import set_sysID_relationship_fields
from ticket.models import Incident, PasswordReset, Request, TicketType
from ticket.utils import disable_form_fields, get_status_open, get_status_resolved

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

@login_required(login_url='/access/login')
def group_tree(request):
    group_list = ITSMGroup.objects.all()
   
    group_tree = create_tree_list(qs=group_list, max_depth=5)

    context = {
        'group_tree' : group_tree
    }

    return render(request, 'access/group-tree.html', context)

#Display homepage of logged in user's tickets
@login_required(login_url='/access/login')
def homepage(request):
    new_start_date = get_new_ticket_start_date()

    #Get tickets for the logged in user
    #New tickets are entered after the start date (3 days ago)
    #Open tickets are not in 'resoled' or 'closed' status
    #Resolved tickets are in 'resolved' status
    new_inc = Incident.objects.filter(customer=request.user.customer, created__gt=new_start_date)
    open_inc = Incident.objects.filter(customer=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(customer=request.user.customer, status__in=get_status_resolved(id=1, return_qs=True))

    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
    }

    return render(request, 'access/homepage.html', context)

#Display homepage of tickets assigned to logged in user
@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
def homepage_assigned_to_me(request):

    new_start_date = get_new_ticket_start_date()

    #Get tickets assigned to the logged in user
    new_inc = Incident.objects.filter(assignee=request.user.customer, created__gt=new_start_date)
    open_inc = Incident.objects.filter(assignee=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(assignee=request.user.customer, status__in=get_status_resolved(id=1, return_qs=True))

    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
    }

    return render(request, 'access/homepage-assignedtome.html', context)

#Display homepage of tickets assigned to logged in user's assignment groups
@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
def homepage_assigned_to_my_groups(request):

    new_start_date = get_new_ticket_start_date()

    #Get all groups logged in user is a member of
    user_groups = ITSMGroup.objects.filter(members=request.user.customer)
    #Get all ticket types
    ticket_types = TicketType.objects.all()
    #Get tickets assigned to logged in user's assignment groups
    new_inc = Incident.objects.filter(assignment_group__in=user_groups, created__gt=new_start_date)
    open_inc = Incident.objects.filter(assignment_group__in=user_groups, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(assignment_group__in=user_groups, status__in=get_status_resolved(id=1, return_qs=True))
    

    #Create a dictionary go groups, users, , ticket types, and ticket counts
    #Dictionary format:
    #   group_assignee_dict = {
    #       'group' : {
    #            'tickettype' : {
    #               'new' : count,
    #               'new_url' : url,
    #               'open' : count,
    #               'open_url' : url,
    #               'resolved' : count,
    #               'resolved_url' : url,
    #           },   
    #       },
    #   }
    #
    #   group_assignee_dict = {
    #       'group' : {
    #           'assignee' : {
    #                'tickettype' : {
    #                   'new' : count,
    #                   'new_url' : url,
    #                   'open' : count,
    #                   'open_url' : url,
    #                   'resolved' : count,
    #                   'resolved_url' : url, 
    #               },
    #           },
    #       },
    #   }

    #Declare dictionaries
    group_dict = {}
    group_assignee_dict = {}

    #GET argument to collapse search filter on page load
    collapse_filter = f'collapse_filter={True}'

    #Populate the group dictionary
    group_dict = {
        g.name : {
            t.name : {
                'new': (apps.get_model('ticket', t.name)).objects.annotate(n_assignment_group=Count('assignment_group')).filter(assignment_group=g, created__gt=new_start_date).count(),
                'new_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignment_group={g.name}&created_range_min={new_start_date.isoformat()}',
                'open': (apps.get_model('ticket', t.name)).objects.annotate(n_assignment_group=Count('assignment_group')).filter(assignment_group=g, status__in=get_status_open(id=t.id)).count(),
                'open_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignment_group={g.name}&{format_queryset_to_get_url(get_status_open(id=t.id))}',
                'resolved': (apps.get_model('ticket', t.name)).objects.annotate(n_assignment_group=Count('assignment_group')).filter(assignment_group=g, status__in=get_status_resolved(id=t.id, return_qs=True)).count(),
                'resolved_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignment_group={g.name}&{format_queryset_to_get_url(get_status_resolved(id=t.id, return_qs=True))}',
            } for t in ticket_types
        } for g in user_groups
    }

    #Populate group assignee dictionary
    group_assignee_dict = {
        g.name : {
            u.full_name : {
                t.name : {
                    'new': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=u, assignment_group=g, created__gt=new_start_date).count(),
                    'new_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee={u.id}&assignment_group={g.name}&created_range_min={new_start_date.isoformat()}',
                    'open': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=u, assignment_group=g, status__in=get_status_open(id=t.id)).count(),
                    'open_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee={u.id}&assignment_group={g.name}&{format_queryset_to_get_url(get_status_open(id=t.id))}',
                    'resolved': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=u, assignment_group=g, status__in=get_status_resolved(id=t.id, return_qs=True)).count(),
                    'resolved_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee={u.id}&assignment_group={g.name}&{format_queryset_to_get_url(get_status_resolved(id=t.id, return_qs=True))}',
                } for t in ticket_types
            } for u in Customer.objects.filter(itsm_group_membership=g)
        } for g in user_groups
    }

    #Loop through dictionary and:
    #   Add UNASSIGNED user and:
    #       Sum counts for tickets assigned to group but with assignee = none
    #       Set url to search results where assigne isnull
    #   Remove any user where sum of ticket counts for all ticket types is 0
    for k1, v1 in group_assignee_dict.copy().items():
        group_assignee_dict[k1]['_UNASSIGNED'] = {
                        t.name : {
                            'new': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=None, assignment_group__name=k1, created__gt=new_start_date).count(),
                            'new_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee_isnull=true&assignment_group={k1}&created_range_min={new_start_date.isoformat()}',
                            'open': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=None, assignment_group__name=k1, status__in=get_status_open(id=t.id)).count(),
                            'open_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee_isnull=true&assignment_group={k1}&{format_queryset_to_get_url(get_status_open(id=t.id))}',
                            'resolved': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=None, assignment_group__name=k1, status__in=get_status_resolved(id=t.id, return_qs=True)).count(),
                            'resolved_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee_isnull=true&assignment_group={k1}&{format_queryset_to_get_url(get_status_resolved(id=t.id, return_qs=True))}',
                        } for t in ticket_types
                    }
                    
        for k2, v2 in v1.copy().items():
            ticket_sum=0
            
            for k3, v3 in v2.items():
                ticket_sum += sum(v4 for k4, v4 in v3.items() if isinstance(v4, int))
            
            if k2 =='_UNASSIGNED':
                group_assignee_dict[k1][k2]['id'] =  ''
            else:
                name = k2.split(' ')
                c_lp = Customer.objects.get(first_name=name[0], last_name=name[1])
                group_assignee_dict[k1][k2]['id'] =  c_lp.id
            

            if ticket_sum == 0:
                group_assignee_dict[k1].pop(k2, None)

    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
        'user_groups' : user_groups,
        'group_dict' : group_dict,
        'group_assignee_dict' : group_assignee_dict,
        'new_start_date' : new_start_date,
    }

    return render(request, 'access/homepage-assignedtomygroups.html', context)

#Display customer form for logged in user to change data
@login_required(login_url='/access/login')
def profile(request):

    customer = request.user.customer
    form = CustomerForm(instance=customer)
    
    #Get the last modified timestamp of the profile image
    #This is used to force the browser to refresh and not use cache when the image changes
    profile_image_modtimestamp = os.stat(customer.profile_image.path).st_mtime
    
    if request.method == 'POST':

        form = CustomerForm(request.POST, request.FILES, instance=customer)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.active = customer.active
            instance.save()

    else:
        form = CustomerForm(instance=customer)

    context = {
        'form' : form,
        'profile_image_modtimestamp' : profile_image_modtimestamp,
    }

    return render(request, 'access/profile.html', context)

@login_required(login_url='/access/login')
def user_detail(request, id):

    customer = Customer.objects.get(id=id)
    form = CustomerForm(instance=customer)

    if request.method == 'POST':

        form = CustomerForm(request.POST, request.FILES, instance=customer)

        if form.is_valid():
            form.save()

    else:
        form = CustomerForm(instance=customer)

    if 'TSM Admin' not in request.user.customer.roles:
        form = disable_form_fields(form)

    context = {
        'form' : form,
        'customer' : customer,
    }

    return render(request, 'access/user-detail.html', context)
