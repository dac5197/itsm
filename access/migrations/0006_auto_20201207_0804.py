# Generated by Django 3.1.3 on 2020-12-07 13:04

import base.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20201203_1659'),
        ('access', '0005_auto_20201109_1655'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='sysID',
            field=models.OneToOneField(default=base.models.SysID.add_new, on_delete=django.db.models.deletion.CASCADE, to='base.sysid'),
        ),
    ]