from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, JsonResponse

from rest_framework import generics, mixins, status, viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from ticket.models import *
from .serializers import *

# Create your views here.

class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    queryset = Incident.objects.all()
    lookup_field = 'number'
