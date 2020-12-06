import os
import random
import string

from django.db import models
from django.utils import timezone


#Generate random string for sysID
def get_random_alphanumeric_string(length=32):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


class SysID(models.Model):
    id = models.AutoField(primary_key=True)
    sysID = models.CharField(max_length=32, unique=True, default=get_random_alphanumeric_string, editable=False)

    def __str__(self):
        return self.sysID

    @classmethod
    def add_new(cls):
        return cls.objects.create().id

class Attachment(models.Model):
    foreign_sysID = models.ForeignKey(SysID, on_delete=models.CASCADE, null=True, blank=True)
    document = models.FileField(upload_to='attachments/')
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
