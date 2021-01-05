from django.contrib import admin

from .models import *

#Customize Admin panel view

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'email', 'user','active', 'sysID')
    list_filter = ('active',)
    search_fields = ('first_name', 'last_name', 'email',)
    readonly_fields = ('created', 'updated')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class SidebarItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'path','url')
    list_filter = ('name', 'path', 'roles','url')
    search_fields = ('name', 'path', 'roles','url')
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class ITSMGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'path','manager', 'active','is_assignment', 'is_approval')
    list_filter = ('name', 'path','manager', 'active','is_assignment', 'is_approval')
    search_fields = ('name', 'path','manager', 'active','is_assignment', 'is_approval')
    readonly_fields = ()

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.

#admin.site.register(Account, AccountAdmin)

admin.site.register(Location)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(ITSMGroup, ITSMGroupAdmin)
admin.site.register(Role)
admin.site.register(SidebarItem, SidebarItemAdmin)
