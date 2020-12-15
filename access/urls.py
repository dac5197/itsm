from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views, utils


urlpatterns = [
    #path('login', views.login, name="login"),
    path('group-tree', views.group_tree, name='group-tree'),
    path('homepage', views.homepage, name='homepage'),
    path('homepage-assignedtome', views.homepage_assigned_to_me, name='homepage-assignedtome'),
    path('homepage-assignedtomygroups', views.homepage_assigned_to_my_groups, name='homepage-assignedtomygroups'),
    path('register-account', views.register_account, name='register-account'),
    path('register-profile/<str:id>', views.register_profile, name='register-profile'),
    path('login', LoginView.as_view(
            template_name = 'access/login.html',
            extra_context = {
                'bg_img' : utils.get_random_bg_img('backgrounds'),
            },
        )
    ),
    path("logout", LogoutView.as_view(), name="logout"),

]