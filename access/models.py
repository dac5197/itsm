from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from base.models import SysID
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

#class User(AbstractBaseUser):
class Location(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    address = models.CharField(max_length=100, unique=True, null=False, blank=False)
    city = models.CharField(max_length=100, unique=True, null=False, blank=False)
    state = models.CharField(max_length=100, unique=True, null=False, blank=False)
    zipcode = models.CharField(max_length=100, unique=True, null=False, blank=False)
    x_coord = models.FloatField(null=True, blank=True)
    y_coord = models.FloatField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)    
    
    def __str__(self):
        return self.name

class Customer(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    username = models.CharField(max_length=10, unique=True, null=False, blank=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=200, unique=True, null=False, blank=False)
    phone = models.CharField(max_length=20, null=True, blank=True)
    manager = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    #role

    def __str__(self):
        return self.display_name
    @property
    def full_name(self):
        return str(self.first_name) + " " + str(self.last_name)

    @property
    def display_name(self):
        return str(self.last_name) + ", " + str(self.first_name) + " (" +  str(self.organization) + ")"

class Group(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    parent = models.ForeignKey('Group', on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='group_manager')
    members = models.ManyToManyField(Customer, related_name='group_membership', blank=True)
    is_assignment = models.BooleanField(default=False)
    is_approval = models.BooleanField(default=False)
    is_heirarchal = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

