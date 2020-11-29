from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path('incident', views.incident, name='incident'),
    path('incident-create', views.incident_create, name='incident-create'),
    path('incident-crispy-detail/<str:number>', views.IncidentDetail.as_view(), name='incident-crispy-detail'),
    path('incident-detail/<str:number>', views.incident_detail, name='incident-detail'),
    path('incident-update', views.incident_update, name='incident-update'),
]