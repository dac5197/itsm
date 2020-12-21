import os

from django.conf import settings
from django.db import models
from django.db.models import CharField
from django.db.models.functions import Length
from django.contrib.auth.models import Group as DjangoGroup, User

from base.models import SysID
from phonenumber_field.modelfields import PhoneNumberField

#Register 'Length' transfer for Charfield to allow queryset filtering by char length
#https://stackoverflow.com/a/45260608
CharField.register_lookup(Length, 'length')

# Create your models here.


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

def get_profile_image(self, filename):
    save_dir = f'{settings.MEDIA_ROOT}/images/profile_images/{self.pk}'
    save_filename = f'{save_dir}/{"profile_image.png"}'

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    if os.path.exists(save_filename):
        print('deleting old profile image')
        os.remove(save_filename)

    return save_filename

def get_default_profile_image():
    return f'images/profile_images/default.png'

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, blank=True, null=True)
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
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image, null=True, blank=True, default=get_default_profile_image)

    def __str__(self):
        return self.display_name

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_imag).index(f'profile_images/{self.pk}/'):]

    @property
    def display_name(self):
        return str(self.last_name) + ", " + str(self.first_name) + " (" +  str(self.organization) + ")"

    @property
    def full_name(self):
        return str(self.first_name) + " " + str(self.last_name)

    @property
    def group_memberof(self):
        groups = ITSMGroup.objects.filter(members=self).order_by('name')
        return groups

    @property
    def roles(self):
        user_roles = []
        for grp in self.group_memberof:
            for role in grp.roles.all():
                if role.name not in user_roles:
                    user_roles.append(role.name)

        #Add the 'Everyone' role for base access
        user_roles.append('Everyone')
        user_roles.sort()
        return user_roles    

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

class Role(models.Model):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class ITSMGroup(DjangoGroup):
    sysID = models.OneToOneField(SysID, on_delete=models.CASCADE, default=SysID.add_new)
    manager = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='itms_group_manager')
    members = models.ManyToManyField(Customer, related_name='itsm_group_membership', blank=True)
    path = models.CharField(max_length=25, unique=True, blank=False, null=False)
    is_assignment = models.BooleanField(default=False)
    is_approval = models.BooleanField(default=False)
    is_heirarchal = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    roles = models.ManyToManyField(Role, related_name='role_membership', blank=True)
    
    def __str__(self):
        return self.name


class SidebarItem(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    path = models.CharField(max_length=25, unique=True, blank=False, null=False)
    roles = models.ManyToManyField(Role, related_name='allowed_roles', blank=True)
    url = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def has_children(self):
        children = SidebarItem.objects.filter(path__startswith=self.path, path__length=len(self.path)+1)
        children = children.exclude(path=self.path)

        if children.exists():
            return True
        else:
            return False





    