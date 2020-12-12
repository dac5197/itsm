from django.contrib.auth.views import LoginView
from django.urls import path

from . import views, utils


urlpatterns = [
    #path('login', views.login, name="login"),
    path('group-tree', views.group_tree, name='group-tree'),
    path('homepage', views.homepage, name='homepage'),
    path('register-account', views.register_account, name='register-account'),
    path('register-profile/<str:id>', views.register_profile, name='register-profile'),
    path('login', LoginView.as_view(
            template_name = 'access/login.html',
            extra_context = {
                'bg_img' : utils.get_random_bg_img('backgrounds'),
            },
        )
    ),

]