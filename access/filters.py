from django.db.models import Q
from django.forms import DateInput

import django_filters
from django_filters import BooleanFilter, ChoiceFilter, DateFilter, CharFilter, MultipleChoiceFilter, DateTimeFilter, DateTimeFromToRangeFilter, RangeFilter, DateFilter, NumberFilter
from django_filters.widgets import RangeWidget

from .models import *
from .utils import *

BOOLEAN_FILTER_CHOICES = [
    (True, 'True'),
    (False, 'False'),
]

class CustomerFilter(django_filters.FilterSet):
    username = CharFilter(field_name='username', label='Username', method='username_filter')
    active = ChoiceFilter(field_name='active', label='Active', choices=BOOLEAN_FILTER_CHOICES)
    created = DateFilter(field_name='created', lookup_expr='icontains', label='Created', widget=DateInput(attrs={'type': 'date'}))
    created_range = DateTimeFromToRangeFilter(field_name='created', lookup_expr='icontains', label='Created Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    updated = DateFilter(field_name='updated', lookup_expr='icontains', label='Updated', widget=DateInput(attrs={'type': 'date'}))
    updated_range = DateTimeFromToRangeFilter(field_name='updated', lookup_expr='icontains', label='Updated Range', widget=RangeWidget(attrs={'type': 'datetime-local'}))
    
    #Set choices for select fields
    location = MultipleChoiceFilter(get_all_location_choices())
    manager = MultipleChoiceFilter(get_all_customer_choices())

    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['sysID', 'profile_image',]
        
    def username_filter(self, queryset, name, value):
        return Customer.objects.filter(user__username__icontains=value)


class GroupFilter(django_filters.FilterSet):
    active = ChoiceFilter(field_name='active', label='Active', choices=BOOLEAN_FILTER_CHOICES)
    is_assignment = ChoiceFilter(field_name='is_assignment', label='Is Assignment Group?', choices=BOOLEAN_FILTER_CHOICES)
    is_approval = ChoiceFilter(field_name='is_approval', label='Is Approval Group?', choices=BOOLEAN_FILTER_CHOICES)
    is_heirarchal = ChoiceFilter(field_name='is_heirarchal', label='Is Heirarchal Group?', choices=BOOLEAN_FILTER_CHOICES)

    #Set choices for select fields
    manager = MultipleChoiceFilter(get_all_customer_choices())
    members = MultipleChoiceFilter(get_all_customer_choices())
    roles = MultipleChoiceFilter(get_all_roles_choices())

    class Meta:
        model = ITSMGroup
        fields = '__all__'
        exclude = ['sysID', 'permissions',]
