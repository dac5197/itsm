from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router_inc = DefaultRouter()
router_inc.register('incident', views.IncidentViewSet, basename='incient')

urlpatterns = [
    path('viewset/', include(router_inc.urls)),
    #path('viewset/<int:pk>/', include(router_inc.urls)),
    path('viewset/<str:number>/', include(router_inc.urls)),
]