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

class RequestAdmin(admin.ModelAdmin):
    list_display = ('number', 'status', 'created', 'updated', 'fulfilled')
    list_filter = ()
    search_fields = ('number', 'status', 'created', 'updated', 'fulfilled')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class StatusAdmin(admin.ModelAdmin):
    list_display = ('value', 'ticket_type', 'order_value', 'default_value', 'resolved_value', 'closed_value')
    list_filter = ()
    search_fields = ('value', 'ticket_type', 'order_value', 'default_value', 'resolved_value', 'closed_value')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'prefix', 'active')
    list_filter = ()
    search_fields = ('id', 'name', 'prefix', 'active')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.

admin.site.register(Priority)
admin.site.register(TicketType, TicketTypeAdmin)
admin.site.register(Status, StatusAdmin)
admin.site.register(Ticket)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(PasswordReset)
admin.site.register(Request, RequestAdmin)
admin.site.register(Outage)