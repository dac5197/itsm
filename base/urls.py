from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('remove-attachment/<int:id>/<str:number>/<str:url>/', views.remove_attachment, name="remove-attachment"),
]
