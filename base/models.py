from django.db import models
from .utils import get_random_alphanumeric_string

# Create your models here.


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