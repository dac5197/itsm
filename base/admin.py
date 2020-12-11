from django.contrib import admin
from .models import *


class SysIDAdmin(admin.ModelAdmin):
    list_display = ('sysID', 'rel_obj_model', 'rel_obj_id', 'rel_obj_name')
    list_filter = ()
    search_fields = ('rel_obj_model', 'rel_obj_name')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


# Register your models here.

admin.site.register(SysID, SysIDAdmin)
admin.site.register(Attachment)