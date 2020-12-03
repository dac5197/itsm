from django.contrib.postgres.fields import ArrayField, HStoreField
from django.contrib.postgres.forms.jsonb import JSONField
from django.db import models
from django.utils import timezone

from base.models import SysID
from ticket.models import TicketType
from access.models import Customer, Group, Location

# Create your models here.

class WorkNote(models.Model):
    foreign_sysID = models.ForeignKey(SysID, on_delete=models.CASCADE, null=False, blank=False)
    notes = models.TextField(null=True, blank=True)
    customer_visible = models.BooleanField(default=False)
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)
    changed_data = models.TextField(null=True, blank=True)

class FieldChange(models.Model):
    work_note_id = models.ForeignKey(WorkNote, on_delete=models.CASCADE, null=True, blank=True)
    field = models.CharField(max_length=25, null=True, blank=True)
    old_value = models.CharField(max_length=100, null=True, blank=True)
    new_value = models.CharField(max_length=100, null=True, blank=True)

class Watcher(models.Model):
    ticket_type = models.ForeignKey(TicketType, on_delete=models.SET_NULL, null=True, blank=True)
    watch_fields = ArrayField(models.CharField(max_length=25, default=[], blank=True))

    def __str__(self):
        return f"Watcher - {self.ticket_type}"

class History(models.Model):
    pass