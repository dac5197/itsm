from django.db.models import Q

import django_filters
from django_filters import DateFilter, CharFilter

from .models import *

from access.models import *



class IncidentFilter(django_filters.FilterSet):
    customer = CharFilter(method='customer_all_fields_filter')

    class Meta:
        model = Incident
        fields = '__all__'
        exclude =['sysID','ticket_type','active', 'customer']

    def customer_all_fields_filter(self, queryset, name, value):
        return Incident.objects.filter(
            Q(customer__first_name__icontains=value) | Q(customer__last_name__icontains=value) | Q(customer__username__icontains=value) | Q(customer__email__icontains=value)
        )
        