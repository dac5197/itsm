# Generated by Django 3.1.3 on 2020-11-17 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0011_ticket_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
