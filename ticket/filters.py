from django.db.models import Q

import django_filters
from django_filters import DateFilter, CharFilter, MultipleChoiceFilter

from .models import *
from .utils import *

from access.models import *



class IncidentFilter(django_filters.FilterSet):
    #Set charfilters to search multiple fields in related models (foriegn keys)
    assignee = CharFilter(method='assignee_all_fields_filter')
    assignment_group = CharFilter(field_name='assignment_group__name', lookup_expr='icontains', label='Assignment Group')
    customer = CharFilter(method='customer_all_fields_filter')
    location = CharFilter(method='location_all_fields_filter')

    #Set choices for select fields
    status = MultipleChoiceFilter(choices=get_status_choices(id=1))
    priority = MultipleChoiceFilter(choices=get_priority_choices())

    class Meta:
        model = Incident
        fields = '__all__'
        exclude = [
            'sysID',
            'ticket_type',
            'active',
            ]

    def assignee_all_fields_filter(self, queryset, name, value):
        return Incident.objects.filter(
            Q(assignee__first_name__icontains=value) | Q(assignee__last_name__icontains=value) | Q(assignee__username__icontains=value) | Q(assignee__email__icontains=value)
        )
        

    def customer_all_fields_filter(self, queryset, name, value):
        return Incident.objects.filter(
            Q(customer__first_name__icontains=value) | Q(customer__last_name__icontains=value) | Q(customer__username__icontains=value) | Q(customer__email__icontains=value)
        )
        
    def location_all_fields_filter(self, queryset, name, value):
        return Incident.objects.filter(
            Q(location__name__icontains=value) | Q(location__address__icontains=value) | Q(location__city__icontains=value) | Q(location__state__icontains=value) | Q(location__zipcode__icontains=value)
        )