from django.contrib import admin

from .models import *

#Customize Admin panel view

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'email', 'user','active')
    list_filter = ('active',)
    search_fields = ('first_name', 'last_name', 'email',)
    readonly_fields = ('created', 'updated')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.

#admin.site.register(Account, AccountAdmin)

admin.site.register(Location)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(Group)
admin.site.register(ITSMGroup)

