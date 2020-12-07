from django.urls import path
from . import views


urlpatterns = [
    path('login', views.login, name="login"),
    path('group-tree', views.group_tree, name="group-tree"),
]