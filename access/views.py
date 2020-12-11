from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .forms import *
from .models import *
from .utils import *

from base.utils import set_sysID_relationship_fields

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