# Generated by Django 3.1.3 on 2020-11-24 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0020_auto_20201124_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='status',
            name='closed_value',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='status',
            name='resolved_value',
            field=models.BooleanField(default=False),
        ),
    ]
