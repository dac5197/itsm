import os

from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail, BadHeaderError
from django.db.models import Count
from django.shortcuts import render, redirect
from django.utils import timezone

from .decorators import *
from .filters import *
from .forms import *
from .models import *
from .utils import *

from base.utils import set_sysID_relationship_fields
from ticket.models import Incident, PasswordReset, Request, TicketType
from ticket.utils import disable_form_fields, get_status_open, get_status_resolved
from ticket.views import export_csv

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

    context = {
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
        
        form = CustomerRegisterForm(request.POST)
    
        if form.is_valid():
            instance = form.save()
            
            #Set User email to match Customer email
            user.email = instance.email
            user.save()

            #Create new sysID for Customer and set the relationship fields
            instance.sysID = SysID.objects.create()
            instance.save()
            set_sysID_relationship_fields(instance)

            #Send email notification of new account
            subject = f'New Account Created for {instance.full_name}'
            #Create string for email body
            email_body = f'''
            New Account Created
            Username: {user.username}
            Name: {instance.full_name}
            Email: {instance.email}
            Instance: {settings.BASE_DIR}
            '''
            #Send email
            try:
                send_mail(subject=subject, message=email_body, from_email=settings.EMAIL_HOST_USER, recipient_list=['dac5197@live.com'])
            except BadHeaderError:
                pass
            
            #Registration complete - redirect to login page
            return redirect('/access/login')
    else:
        form = CustomerRegisterForm()

    context = {
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
    #   New tickets are entered after the start date (3 days ago)
    #   Open tickets are not in 'resoled' or 'closed' status
    #   Resolved tickets are in 'resolved' status
    #Incidents
    new_inc = Incident.objects.filter(customer=request.user.customer, created__gt=new_start_date)
    open_inc = Incident.objects.filter(customer=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(customer=request.user.customer, status__in=get_status_resolved(id=1, return_qs=True))
    #Requests
    new_req = Request.objects.filter(customer=request.user.customer, created__gt=new_start_date)
    open_req = Request.objects.filter(customer=request.user.customer, status__in=get_status_open(id=2))
    resolved_req = Request.objects.filter(customer=request.user.customer, status__in=get_status_resolved(id=2, return_qs=True))

    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
        'new_req' : new_req,
        'open_req' : open_req,
        'resolved_req' : resolved_req,
    }

    return render(request, 'access/homepage.html', context)

#Display homepage of tickets assigned to logged in user
@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM User'])
def homepage_assigned_to_me(request):

    new_start_date = get_new_ticket_start_date()

    #Get tickets assigned to the logged in user
    #Incidents
    new_inc = Incident.objects.filter(assignee=request.user.customer, created__gt=new_start_date)
    open_inc = Incident.objects.filter(assignee=request.user.customer, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(assignee=request.user.customer, status__in=get_status_resolved(id=1, return_qs=True))
    #Requests
    new_req = Request.objects.filter(assignee=request.user.customer, created__gt=new_start_date)
    open_req = Request.objects.filter(assignee=request.user.customer, status__in=get_status_open(id=2))
    resolved_req = Request.objects.filter(assignee=request.user.customer, status__in=get_status_resolved(id=2, return_qs=True))

    context = {
        'new_inc' : new_inc,
        'open_inc' : open_inc,
        'resolved_inc' : resolved_inc,
        'new_req' : new_req,
        'open_req' : open_req,
        'resolved_req' : resolved_req,
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
    ticket_types = TicketType.objects.filter(name='Incident') | TicketType.objects.filter(name='Request')
    #Get tickets assigned to logged in user's assignment groups
    #Incidents
    new_inc = Incident.objects.filter(assignment_group__in=user_groups, created__gt=new_start_date)
    open_inc = Incident.objects.filter(assignment_group__in=user_groups, status__in=get_status_open(id=1))
    resolved_inc = Incident.objects.filter(assignment_group__in=user_groups, status__in=get_status_resolved(id=1, return_qs=True))
    #Requests
    new_req = Request.objects.filter(assignment_group__in=user_groups, created__gt=new_start_date)
    open_req = Request.objects.filter(assignment_group__in=user_groups, status__in=get_status_open(id=2))
    resolved_req = Request.objects.filter(assignment_group__in=user_groups, status__in=get_status_resolved(id=2, return_qs=True))
    

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
                'new_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignment_group={g.id}&created_range_min={new_start_date.isoformat()}',
                'open': (apps.get_model('ticket', t.name)).objects.annotate(n_assignment_group=Count('assignment_group')).filter(assignment_group=g, status__in=get_status_open(id=t.id)).count(),
                'open_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignment_group={g.id}{format_queryset_to_get_url(get_status_open(id=t.id))}',
                'resolved': (apps.get_model('ticket', t.name)).objects.annotate(n_assignment_group=Count('assignment_group')).filter(assignment_group=g, status__in=get_status_resolved(id=t.id, return_qs=True)).count(),
                'resolved_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignment_group={g.id}{format_queryset_to_get_url(get_status_resolved(id=t.id, return_qs=True))}',
            } for t in ticket_types
        } for g in user_groups
    }

    #Populate group assignee dictionary
    group_assignee_dict = {
        g.name : {
            u.full_name : {
                t.name : {
                    'new': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=u, assignment_group=g, created__gt=new_start_date).count(),
                    'new_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee={u.id}&assignment_group={g.id}&created_range_min={new_start_date.isoformat()}',
                    'open': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=u, assignment_group=g, status__in=get_status_open(id=t.id)).count(),
                    'open_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee={u.id}&assignment_group={g.id}{format_queryset_to_get_url(get_status_open(id=t.id))}',
                    'resolved': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=u, assignment_group=g, status__in=get_status_resolved(id=t.id, return_qs=True)).count(),
                    'resolved_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee={u.id}&assignment_group={g.id}{format_queryset_to_get_url(get_status_resolved(id=t.id, return_qs=True))}',
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
                            'new_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee_isnull=true&assignment_group={ITSMGroup.objects.get(name=k1).id}&created_range_min={new_start_date.isoformat()}',
                            'open': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=None, assignment_group__name=k1, status__in=get_status_open(id=t.id)).count(),
                            'open_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee_isnull=true&assignment_group={ITSMGroup.objects.get(name=k1).id}{format_queryset_to_get_url(get_status_open(id=t.id))}',
                            'resolved': (apps.get_model('ticket', t.name)).objects.annotate(n_assignee=Count('assignee')).filter(assignee=None, assignment_group__name=k1, status__in=get_status_resolved(id=t.id, return_qs=True)).count(),
                            'resolved_url' : f'{t.name.lower()}-search/?{collapse_filter}&assignee_isnull=true&assignment_group={ITSMGroup.objects.get(name=k1).id}{format_queryset_to_get_url(get_status_resolved(id=t.id, return_qs=True))}',
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
        'new_req' : new_req,
        'open_req' : open_req,
        'resolved_req' : resolved_req,
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
            instance.updated = timezone.now()
            instance.save()
            return redirect('/access/profile')

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
            customer.updated = timezone.now()
            customer.save()
            return redirect('user-detail', id=customer.id)

    else:
        form = CustomerForm(instance=customer)

    if 'TSM Admin' not in request.user.customer.roles:
        form = disable_form_fields(form)

    context = {
        'form' : form,
        'customer' : customer,
    }

    return render(request, 'access/user-detail.html', context)

@login_required(login_url='/access/login')
def user_search(request):
    customers = Customer.objects.all()
    customer_filter = CustomerFilter(request.GET, queryset=customers)
    collapse_filter = False

    #Set search results to filter queryset if search args passed in GET
    #Else set queryset to blank
    if request.GET:
        customers = customer_filter.qs

        #If collapse_filter, then set to GET parameter
        #Set to True will set the Search Filters accordion to collapse on page load
        collapse_filter = request.GET.get('collapse_filter')

    else:
        customers = ''

    #If export button -> export data to csv
    if 'export' in request.GET:
        return export_csv(queryset=customers, obj_type='customer')

    context = {
        'filter' : customer_filter,
        'customers' : customers,
        'collapse_filter' : collapse_filter,
    }

    return render(request, 'access/user-search.html', context)

#Display itsmgroup details
@login_required(login_url='/access/login')
def group_detail(request, id):
    group = ITSMGroup.objects.get(id=id)
    form = GroupForm(instance=group)

    #Show the update membership button if user is group manager or TSM Admin
    #Else hide the button
    if 'TSM Admin' in request.user.customer.roles or request.user.customer == group.manager:
        can_edit_members = True
    else:
        can_edit_members = False
    
    context = {
        'form' : form,
        'group' : group,
        'can_edit_members' : can_edit_members,
    }

    return render(request, 'access/group-detail.html', context)

#Updated itsmgroup membership
#Accessible for the group's manager and TSM Admins
@login_required(login_url='/access/login')
def group_members_update(request, id):
    group = ITSMGroup.objects.get(id=id)
    form = GroupForm(instance=group)

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)

        if form.is_valid():
            form.save()
            group.updated = timezone.now()
            group.save()
            return redirect('group-detail', id=group.id)

    else:
        form = GroupForm(instance=group)

    #Disable all form fields if user is not group manager or TSM Admin
    if not ('TSM Admin' in request.user.customer.roles or request.user.customer == group.manager):
        form = disable_form_fields(form)

    context = {
        'form' : form,
        'group' : group,
    }

    return render(request, 'access/group-members-update.html', context)

#Update itsm group fields
#Accessible for TSM Admins
@login_required(login_url='/access/login')
@allowed_users(allowed_roles=['TSM Admin'])
def group_admin_update(request, id):
    group = ITSMGroup.objects.get(id=id)
    form = GroupAdminForm(instance=group)

    if request.method == 'POST':
        form = GroupAdminForm(request.POST, instance=group)

        if form.is_valid():
            form.save()
            group.updated = timezone.now()
            group.save()
            return redirect('group-detail', id=group.id)

    else:
        form = GroupAdminForm(instance=group)

    #Disable all form fields if user is not TSM Admin
    if not ('TSM Admin' in request.user.customer.roles):
        form = disable_form_fields(form)

    context = {
        'form' : form,
        'group' : group,
    }

    return render(request, 'access/group-admin-update.html', context)

@login_required(login_url='/access/login')
def group_search(request):
    groups = ITSMGroup.objects.all()
    group_filter = GroupFilter(request.GET, queryset=groups)
    collapse_filter = False

    #Set search results to filter queryset if search args passed in GET
    #Else set queryset to blank
    if request.GET:
        groups = group_filter.qs

        #If collapse_filter, then set to GET parameter
        #Set to True will set the Search Filters accordion to collapse on page load
        collapse_filter = request.GET.get('collapse_filter')

    else:
        groups = ''

    #If export button -> export data to csv
    if 'export' in request.GET:
        return export_csv(queryset=groups, obj_type='itsmgroup')

    context = {
        'filter' : group_filter,
        'groups' : groups,
        'collapse_filter' : collapse_filter,
    }

    return render(request, 'access/group-search.html', context)