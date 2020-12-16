from django.db.models import Q
from django.forms import DateInput

import django_filters
from django_filters import BooleanFilter, ChoiceFilter, DateFilter, CharFilter, MultipleChoiceFilter, DateTimeFilter, DateTimeFromToRangeFilter, RangeFilter, DateFilter, NumberFilter
from django_filters.widgets import RangeWidget

from .models import *
from .utils import *

from access.models import *

class IncidentFilter(django_filters.FilterSet):
    #Set charfilters to search multiple fields in related models (foriegn keys)
    #assignee = CharFilter(method='assignee_all_fields_filter')
    assignment_group = CharFilter(field_name='assignment_group__name', lookup_expr='icontains', label='Assignment Group')
    #customer = CharFilter(method='customer_all_fields_filter')
    location = CharFilter(method='location_all_fields_filter')
    created = DateFilter(field_name='created', lookup_expr='icontains', label='Created', widget=DateInput(attrs={'type': 'date'}))
    created_range = DateTimeFromToRangeFilter(field_name='created', lookup_expr='icontains', label='Created Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    resolved = DateFilter(field_name='resolved', lookup_expr='icontains', label='Resolved', widget=DateInput(attrs={'type': 'date'}))
    resolved_range = DateTimeFromToRangeFilter(field_name='resolved', lookup_expr='icontains', label='Resolved Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    reopened = NumberFilter(field_name='reopened', lookup_expr='exact', label='Reopened')
    reopened_range = RangeFilter(field_name='reopened', lookup_expr='icontains', label='Reopened Range')

    #Set choices for select fields
    assignee = MultipleChoiceFilter(choices=get_all_customer_choices())
    customer = MultipleChoiceFilter(choices=get_all_customer_choices())
    priority = MultipleChoiceFilter(choices=get_priority_choices())
    status = MultipleChoiceFilter(choices=get_status_choices(id=1))

    class Meta:
        model = Incident
        fields = '__all__'
        exclude = [
            'sysID',
            'ticket_type',
            ]
        
    def location_all_fields_filter(self, queryset, name, value):
        return Incident.objects.filter(
            Q(location__name__icontains=value) | Q(location__address__icontains=value) | Q(location__city__icontains=value) | Q(location__state__icontains=value) | Q(location__zipcode__icontains=value)
        )