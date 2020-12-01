from django.db import models
from django.apps import AppConfig, apps
from django.utils import timezone

from base.models import SysID
from access.models import Customer, Group, Location

#Increment ticket numbers when object is created
def increment_ticket_number(prefix, id):
    number = prefix + str(id).zfill(7)
    return number

def increment_inc_number():
    try:
        last_inc_id = Incident.objects.all().order_by('id').last().id
        last_inc_id += 1
    except:
        last_inc_id = 1
    return increment_ticket_number('INC', last_inc_id)  

def increment_pwrst_number():
    try:
        last_pwrst_id = PasswordReset.objects.all().order_by('id').last().id
        last_pwrst_id += 1
    except:
        last_pwrst_id = 1
    return increment_ticket_number('PWRST', last_pwrst_id)  

def increment_req_number():
    try:
        last_id = Request.objects.all().order_by('id').last().id
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('REQ', last_id)  

def increment_out_number():
    try:
        last_id = Outage.objects.all().order_by('id').last().id
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('OUT', last_id)  

# Create your models here.

class Priority(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new, editable=False)
    value = models.IntegerField(unique=True, null=False, blank=False)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    default_value = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    @property
    def priority(self):
        return str(self.value) + " - " + str(self.name)
    
    class Meta:
        verbose_name_plural = "Priorities"

    def __str__(self):
        return self.priority

class TicketType(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    prefix = models.CharField(max_length=10, unique=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Status(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new, editable=False)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.CharField(max_length=100, null=False, blank=False)
    order_value = models.PositiveIntegerField(null=True, blank=True)
    default_value = models.BooleanField(default=False)
    resolved_value = models.BooleanField(default=False)
    closed_value = models.BooleanField(default=False)
    system_value = models.BooleanField(default=False)

    @property
    def detailed_value(self):
        return str(self.ticket_type.name) + " - " + str(self.value)

    def __str__(self):
        return self.value

    class Meta:
        verbose_name_plural = "Statuses"

class Ticket(models.Model):
    sysID = models.ForeignKey(SysID, on_delete=models.CASCADE, default=SysID.add_new, editable=False)
    ticket_type = models.ForeignKey(TicketType, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    #delegates = 
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    desc_short = models.CharField(max_length=100, null=False, blank=False)
    desc_long = models.TextField(null=True, blank=True)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, default= 4, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    assignment_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    assignee = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='assignee')
    closed = models.DateTimeField(null=True, blank=True) 
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)
    updated = models.DateTimeField(default=timezone.now, null=False, blank=False)
    active = models.BooleanField(default=True)
    reopened = models.IntegerField(default=0)


class Incident(Ticket):
    #number = models.CharField(max_length=20, default=increment_inc_number, unique=True, editable=False)
    number = models.CharField(max_length=20, default=increment_inc_number, unique=True)
    resolved = models.DateTimeField(null=True, blank=True) 
    resolution = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.number

class PasswordReset(Ticket):
    #number = models.CharField(max_length=20, default=increment_pwrst_number, unique=True, editable=False)
    number = models.CharField(max_length=20, default=increment_pwrst_number, unique=True)
    resolved = models.DateTimeField(null=True, blank=True)
    res_reset_pw = models.BooleanField(default=False)
    res_unlock_account = models.BooleanField(default=False)
    
    def __str__(self):
        return self.number

class Request(Ticket):
    number = models.CharField(max_length=20, default=increment_req_number, unique=True, editable=False)
    fulfilled = models.DateTimeField(null=True, blank=True) 
    fullfillment_notes = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.number

class Outage(Ticket):
    number = models.CharField(max_length=20, default=increment_out_number, unique=True, editable=False)
    incidents = models.ManyToManyField(Incident, blank=False)
    severity = models.IntegerField(null=False, blank=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    resolved = models.DateTimeField(null=True, blank=True) 
    resolution = models.TextField(null=True, blank=True)
    root_cause_set = models.DateTimeField(null=True, blank=True) 
    root_cause_desc = models.TextField(null=True, blank=True)
    root_cause_group = models.ForeignKey(Group, on_delete=models.SET_NULL, related_name="root_cause_group", null=True, blank=True)
    root_cause_assignee = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="root_cause_assignee", null=True, blank=True)

    def __str__(self):
        return self.number


    
