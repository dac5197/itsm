# Generated by Django 3.1.3 on 2020-12-18 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0013_sidebaritem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sidebaritem',
            name='order',
        ),
    ]
