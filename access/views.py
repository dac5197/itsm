from django.shortcuts import render

from .utils import get_random_bg_img

# Create your views here.

def login(request):
    
    bg_img = get_random_bg_img('backgrounds')

    context = {
        'bg_img' : bg_img
    }

    return render(request, 'access/login.html', context)