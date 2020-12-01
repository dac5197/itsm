# Generated by Django 3.1.3 on 2020-11-16 18:54

from django.db import migrations, models
import ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0008_auto_20201111_1333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordreset',
            name='number',
            field=models.CharField(default=ticket.models.increment_pwrst_number, max_length=20, unique=True),
        ),
    ]
