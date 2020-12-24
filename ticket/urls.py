from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path('incident', views.incident, name='incident'),
    path('incident-create', views.incident_create, name='incident-create'),
    path('incident-detail/<str:number>', views.incident_detail, name='incident-detail'),
    path('incident-search/', views.incident_search, name='incident-search'),
    path('request-create', views.request_create, name='request-create'),
    path('request-detail/<str:number>', views.request_detail, name='request-detail'),
    path('export-csv/', views.export_csv, name='export-csv'),
    path('load-assignees/', views.load_assignees, name='load-assignees'),
]