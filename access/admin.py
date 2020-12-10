from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

#Customize Admin panel view

class AccountAdmin(UserAdmin):
    list_display = ('email', 'username', 'date_joined', 'last_login', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('id', 'date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

# Register your models here.

#admin.site.register(Account, AccountAdmin)

admin.site.register(Location)
admin.site.register(Customer)
admin.site.register(Group)
admin.site.register(ITSMGroup)

