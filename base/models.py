import os
import random
import string

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone

from .validators import validate_file_size

#Generate random string for sysID
def get_random_alphanumeric_string(length=32):
    print('new sysid')
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    if result_str in SysID.objects.values_list('sysID', flat=True):
        result_str = get_random_alphanumeric_string()

    return result_str

class SysID(models.Model):
    id = models.AutoField(primary_key=True)
    sysID = models.CharField(max_length=32, unique=True, default=get_random_alphanumeric_string, editable=False)
    rel_obj_id = models.IntegerField(null=True, blank=True)
    rel_obj_model = models.CharField(max_length=100, null=True, blank=True) 
    rel_obj_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.sysID}"

    @classmethod
    def add_new(cls):
        return cls.objects.create().id


def get_attachment_file(self, filename):
    save_dir = f'{settings.MEDIA_ROOT}/attachments/{self.foreign_sysID.rel_obj_name}'
    save_filename = f'{save_dir}/{filename}'

    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    if os.path.exists(save_filename):
        os.remove(save_filename)

    return save_filename

class Attachment(models.Model):
    foreign_sysID = models.ForeignKey(SysID, on_delete=models.CASCADE, null=True, blank=True)
    document = models.FileField(upload_to=get_attachment_file, validators=[validate_file_size])
    created = models.DateTimeField(default=timezone.now, null=False, blank=False)

    @property
    def doc_name(self):
        return os.path.basename(self.document.name)

    @property
    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def __str__(self):
        return self.doc_name

    @property
    def filename(self):
        return os.path.basename(self.document.name)


class CopyList(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    fields = ArrayField(models.CharField(max_length=20), null=True, blank=True)

    def __str__(self):
        return self.name