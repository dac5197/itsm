from django.http import HttpResponse
from django.shortcuts import redirect

from .models import *
from .utils import *

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            roles = get_user_roles(request)

            if any(role in roles for role in allowed_roles):
                print(True)
                return view_func(request, *args, **kwargs)
            else:
            	return redirect('home')

            #if group in allowed_roles:
            #	
            #else:
            #	return HttpResponse('You are not authorized to view this page')

            return view_func(request, *args, **kwargs)
        return wrapper_func
    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):

        if request.user.is_staff:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('home')

    return wrapper_function