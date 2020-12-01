from django.shortcuts import render
from .models import SysID

# Create your views here.

def home(request):
    return render(request, 'base/home.html')

def create_sysid(request):
    sys_id = SysID.objects.create()
    return sys_id