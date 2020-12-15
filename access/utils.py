import os
import random

from django.contrib.auth.models import User
from django.utils import timezone

from .models import *

#Display random background image on page load 
#Image must be in static\images directory or subdirectory
def get_random_bg_img(img_dir):
    bg_dir = 'static\images\\'+img_dir
    random_file=random.choice(os.listdir(bg_dir))
    static_bg_path = 'images/backgrounds/'
    bg_img = static_bg_path+random_file
    return bg_img

#Generate tree list from queryset using Materialized Path Tree (MPT)
#Object must have Path field and follow MPT structure
#MPT: https://youtu.be/CRxjoklS8v0?t=428
def create_tree_list(qs, max_depth, depth=1, leaf=None):
    #Declare list
    tree_list = []
    
    #Filter queryset based on path level (length) and starting characters from the parent
    if leaf:
        result = qs.filter(path__length=depth, path__startswith=leaf)
    else:
        result = qs.filter(path__length=depth)

    #Increment depth 
    depth += 1

    #For each result:
    #   Add to list
    #   Recursive call this function to get children
    for r in result:
 
        tree_list.append(r)
 
        if depth <= max_depth:
            tree_list.append(create_tree_list(qs=qs, max_depth=max_depth, depth=depth, leaf=r.path))

    return tree_list

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
