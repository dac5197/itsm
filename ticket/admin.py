from django.contrib import admin
from .models import *


class IncidentAdmin(admin.ModelAdmin):
    list_display = ('number', 'status', 'created', 'updated', 'resolved')
    list_filter = ()
    search_fields = ('number', 'status', 'created', 'updated', 'resolved')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.

admin.site.register(Priority)
admin.site.register(TicketType)
admin.site.register(Status)
admin.site.register(Ticket)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(PasswordReset)
admin.site.register(Request)
admin.site.register(Outage)