from django.db.models import Q
from django.forms import DateInput

import django_filters
from django_filters import BooleanFilter, ChoiceFilter, DateFilter, CharFilter, MultipleChoiceFilter, DateTimeFilter, DateTimeFromToRangeFilter, RangeFilter, DateFilter, NumberFilter
from django_filters.widgets import RangeWidget

from .models import *
from .utils import *

from access.models import *
from access.utils import get_all_customer_choices, get_all_location_choices

class IncidentFilter(django_filters.FilterSet):
    created = DateFilter(field_name='created', lookup_expr='icontains', label='Created', widget=DateInput(attrs={'type': 'date'}))
    created_range = DateTimeFromToRangeFilter(field_name='created', lookup_expr='icontains', label='Created Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    resolved = DateFilter(field_name='resolved', lookup_expr='icontains', label='Resolved', widget=DateInput(attrs={'type': 'date'}))
    resolved_range = DateTimeFromToRangeFilter(field_name='resolved', lookup_expr='icontains', label='Resolved Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    reopened = NumberFilter(field_name='reopened', lookup_expr='exact', label='Reopened Count')
    reopened_range = RangeFilter(field_name='reopened', lookup_expr='icontains', label='Reopened Count Range')

    #Set choices for select fields
    assignee = MultipleChoiceFilter(choices=get_all_customer_choices())
    assignment_group = MultipleChoiceFilter(choices=get_assignment_group_choices())
    customer = MultipleChoiceFilter(choices=get_all_customer_choices())
    location = MultipleChoiceFilter(choices=get_all_location_choices())
    priority = MultipleChoiceFilter(choices=get_priority_choices())
    status = MultipleChoiceFilter(choices = get_status_choices(ticket_type=TicketType.objects.get(name='Incident')))

    class Meta:
        model = Incident
        fields = '__all__'
        exclude = [
            'sysID',
            'ticket_type',
            ]


class RequestFilter(django_filters.FilterSet):
    created = DateFilter(field_name='created', lookup_expr='icontains', label='Created', widget=DateInput(attrs={'type': 'date'}))
    created_range = DateTimeFromToRangeFilter(field_name='created', lookup_expr='icontains', label='Created Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    fulfilled = DateFilter(field_name='fulfilled', lookup_expr='icontains', label='Fulfilled', widget=DateInput(attrs={'type': 'date'}))
    fulfilled_range = DateTimeFromToRangeFilter(field_name='fulfilled', lookup_expr='icontains', label='Fulfilled Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    reopened = NumberFilter(field_name='reopened', lookup_expr='exact', label='Reopened Count')
    reopened_range = RangeFilter(field_name='reopened', lookup_expr='icontains', label='Reopened Count Range')

    #Set choices for select fields
    assignee = MultipleChoiceFilter(choices=get_all_customer_choices())
    assignment_group = MultipleChoiceFilter(choices=get_assignment_group_choices())
    customer = MultipleChoiceFilter(choices=get_all_customer_choices())
    location = MultipleChoiceFilter(choices=get_all_location_choices())
    priority = MultipleChoiceFilter(choices=get_priority_choices())
    status = MultipleChoiceFilter(choices=get_status_choices(ticket_type=TicketType.objects.get(name='Request')))

    class Meta:
        model = Request
        fields = '__all__'
        exclude = [
            'sysID',
            'ticket_type',
            ]
