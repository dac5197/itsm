from django.contrib.auth import views as auth_views
from django.urls import path

from . import views, utils


urlpatterns = [
    #path('login', views.login, name="login"),
    path('group-tree', views.group_tree, name='group-tree'),
    path('homepage', views.homepage, name='homepage'),
    path('homepage-assignedtome', views.homepage_assigned_to_me, name='homepage-assignedtome'),
    path('homepage-assignedtomygroups', views.homepage_assigned_to_my_groups, name='homepage-assignedtomygroups'),
    path('profile', views.profile, name='profile'),
    path('register-account', views.register_account, name='register-account'),
    path('register-profile/<str:id>', views.register_profile, name='register-profile'),
    path('user-detail/<str:id>', views.user_detail, name='user-detail'),
    path('user-search', views.user_search, name='user-search'),
    
    path('login', auth_views.LoginView.as_view(template_name = 'access/login.html'), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),

    path('reset-password', auth_views.PasswordResetView.as_view(template_name = 'access/password-reset.html'), name='reset_password'),
    path('reset-password-sent', auth_views.PasswordResetDoneView.as_view(template_name = 'access/password-reset-sent.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = 'access/password-reset-confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete', auth_views.PasswordResetCompleteView.as_view(template_name = 'access/password-reset-complete.html'), name='password_reset_complete'),
]