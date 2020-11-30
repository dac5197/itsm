from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path('incident', views.incident, name='incident'),
    path('incident-create', views.incident_create, name='incident-create'),
    path('incident-detail/<str:number>', views.incident_detail, name='incident-detail'),
]