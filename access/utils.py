import os
import random

from django.contrib.auth.models import User
from django.utils import timezone

from .models import *
from .mpt_utils import create_tree_list

#Display random background image on page load 
#Image must be in static\images directory or subdirectory
def get_random_bg_img(img_dir):
    bg_dir = 'static\images\\'+img_dir
    random_file=random.choice(os.listdir(bg_dir))
    static_bg_path = 'images/backgrounds/'
    bg_img = static_bg_path+random_file
    return bg_img

#Get only the children of a group one level down
def get_group_direct_descendants(grp):
    grp_direct_descendants = ITSMGroup.objects.filter(path__startswith=grp.path, path__length=len(grp.path)+1)
    grp_direct_descendants = grp_direct_descendants.exclude(path=grp.path)
    return grp_direct_descendants

#Get all descendants of a group
def get_group_all_descendants(grp):
    grp_all_descendants = ITSMGroup.objects.filter(path__startswith=grp.path)
    grp_all_descendants = grp_all_descendants.exclude(path=grp.path)
    return grp_all_descendants

#Cascade the roles in parent group to all descandents
def cascade_roles(grp):
    descendants = get_group_all_descendants(grp)
    print(grp.name)
    roles = grp.roles.all()
    for descendant in descendants:
        if roles:
            for role in roles:
                descendant.roles.add(role.id)
        else:
            return False

        print(descendant.name)
    
    return True

#Create SSO for username
def create_sso():
    INITIAL_SSO_VALUE = 100000000

    try:
        last_user_id = User.objects.all().order_by('id').last().id
        last_user_id += 1
    except:
        last_user_id = 1

    sso = INITIAL_SSO_VALUE + last_user_id

    existing_ssos =  User.objects.values_list('username', flat=True)
    
    if sso in existing_ssos:
        sso = create_sso()

    return sso

#Get the start date for "new" tickets
#Start date is today minues DAYS then truncated to midnight for that date
def get_new_ticket_start_date():
    DAYS = 1

    new_ticket_start_date = timezone.now()-timezone.timedelta(days=DAYS)
    new_ticket_start_date = new_ticket_start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return new_ticket_start_date

#Format a queryset for a GET url
def format_queryset_to_get_url(qs):
    url_str = ''
    for obj in qs:
        url_str += f'&{obj.__class__.__name__.lower()}={obj.id}'
    
    return url_str

#Get all roles for groups user is a member of
def get_user_roles(request=None, customer=None):
    if customer:
        user_groups = ITSMGroup.objects.filter(members=customer)
    elif request:
        user_groups = ITSMGroup.objects.filter(members=request.user.customer)
    
    roles = []
    for grp in user_groups:
        for role in grp.roles.all():
            if role.name not in roles:
                roles.append(role.name)

    #Add the 'Everyone' role for base access
    roles.append('Everyone')

    return roles

#Get sidebar items (links) based of customer's roles
def get_sidebar_items(customer):
    #Get roles
    customer_roles = get_user_roles(customer=customer)
    #Get sidebar items that match the roles
    sidebar_items = SidebarItem.objects.filter(roles__name__in=customer_roles).order_by('path')
    #Create nested list of the items based on MP tree
    sidebar_items_tree_list = create_tree_list(qs=sidebar_items, max_depth=2)
    
    return sidebar_items_tree_list

#Return all customers in list for select dropdown menu
def get_all_customer_choices():
    customers = Customer.objects.all().order_by('last_name')
    choices = [(customer.id, customer.__str__()) for customer in customers]
    return choices

#Return all locations in list for select dropdown menu
def get_all_location_choices():
    locations = Location.objects.all().order_by('name')
    choices = [(loc.id, loc.__str__()) for loc in  locations]
    return choices

#Return all roles in list for select dropdown menu
def get_all_role_choices():
    roles = Role.objects.all().order_by('name')
    choices = [(role.id, role.__str__()) for role in  roles]
    return choices

#Return all groups in list for select dropdown menu
def get_all_group_choices():
    groups = ITSMGroup.objects.all().order_by('name')
    choices = [(group.id, group.__str__()) for group in  groups]
    return choices