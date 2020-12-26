from django.contrib import admin

from .models import *

# Register your admin configs

class BoardAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'created', 'updated')
    list_filter = ()
    search_fields = ('number', 'name', 'created', 'updated')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class LaneAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'board', 'path', 'is_worked', 'created', 'updated')
    list_filter = ()
    search_fields = ('number', 'name', 'board', 'path', 'is_worked', 'created', 'updated')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()

class CardAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'lane', 'created', 'updated')
    list_filter = ()
    search_fields = ('number', 'name', 'lane', 'created', 'updated')
    readonly_fields = ['sysID']

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


# Register your models here.

admin.site.register(Board, BoardAdmin)
admin.site.register(Lane, LaneAdmin)
admin.site.register(Card, CardAdmin)