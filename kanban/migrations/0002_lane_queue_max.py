# Generated by Django 3.1.3 on 2020-12-26 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kanban', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lane',
            name='queue_max',
            field=models.IntegerField(default=3),
        ),
    ]
