from django.contrib import admin

from .models import *

# Register your models here.

admin.site.register(FieldChange)
admin.site.register(Watcher)
admin.site.register(WorkNote)

