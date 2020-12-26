from django.db import models
from django.utils import timezone

from base.models import SysID
from ticket.models import Priority

#Increment ticket numbers when object is created
def increment_ticket_number(prefix, id):
    number = prefix + str(id).zfill(7)
    return number

def increment_board_number():
    try:
        number = Board.objects.all().order_by('number').last().number
        last_id = int(number[-7:])
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('BRD', last_id)

def increment_lane_number():
    try:
        number = Lane.objects.all().order_by('number').last().number
        last_id = int(number[-7:])
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('LANE', last_id)

def increment_card_number():
    try:
        number = Card.objects.all().order_by('number').last().number
        last_id = int(number[-7:])
        last_id += 1
    except:
        last_id = 1
    return increment_ticket_number('CRD', last_id)


# Create your models here.

class Board(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    number = models.CharField(max_length=20, default=increment_board_number, unique=True)
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)
    updated = models.DateTimeField(default=timezone.now, null=False, blank=False)

    def __str__(self):
        return self.number

class Lane(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, null=False, blank=False)
    number = models.CharField(max_length=20, default=increment_lane_number, unique=True)
    board = models.ForeignKey(Board, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=25, blank=False, null=False)
    is_worked = models.BooleanField(default=False)
    queue_max = models.IntegerField(default=3,null=False, blank=False)
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)
    updated = models.DateTimeField(default=timezone.now, null=False, blank=False)

    def __str__(self):
        return self.number

class Card(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, null=False, blank=False)
    number = models.CharField(max_length=20, default=increment_card_number, unique=True)
    description = models.TextField(null=True, blank=True)
    lane = models.ForeignKey(Lane, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, default= 4, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)
    updated = models.DateTimeField(default=timezone.now, null=False, blank=False)

    def __str__(self):
        return self.number