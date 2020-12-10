import os
import random

from django.contrib.auth.models import User

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

