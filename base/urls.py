from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('admin-panel', views.admin_panel, name="admin-panel"),
    path('remove-attachment/<int:id>/<str:number>/<str:url>/<str:sysID>/', views.remove_attachment, name="remove-attachment"),
]
