from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Priority)
admin.site.register(TicketType)
admin.site.register(Status)
admin.site.register(Ticket)
admin.site.register(Incident)
admin.site.register(PasswordReset)
admin.site.register(Request)
admin.site.register(Outage)