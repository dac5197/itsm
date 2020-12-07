from django.shortcuts import render

from .models import *
from .utils import create_tree_list, get_random_bg_img

# Create your views here.

def login(request):
    
    bg_img = get_random_bg_img('backgrounds')

    context = {
        'bg_img' : bg_img
    }

    return render(request, 'access/login.html', context)

def group_tree(request):
    group_list = ITSMGroup.objects.all()
   
    group_tree = create_tree_list(qs=group_list, max_depth=5)

    context = {
        'group_tree' : group_tree
    }

    return render(request, 'access/group-tree.html', context)