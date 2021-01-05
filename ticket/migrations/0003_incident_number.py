# Generated by Django 3.1.3 on 2020-11-10 18:13

from django.db import migrations, models
import ticket.models

class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0002_auto_20201110_1017'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='number',
            field=models.CharField(default=ticket.models.increment_inc_number, max_length=20),
        ),
    ]
