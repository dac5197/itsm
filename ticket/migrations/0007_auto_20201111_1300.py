# Generated by Django 3.1.3 on 2020-11-11 18:00

from django.db import migrations, models
import django.db.models.deletion
import ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ('ticket', '0006_ticket_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordReset',
            fields=[
                ('ticket_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='ticket.ticket')),
                ('number', models.CharField(default=ticket.models.increment_pwrst_number, editable=False, max_length=20, unique=True)),
                ('resolved', models.DateTimeField(blank=True, null=True)),
            ],
            bases=('ticket.ticket',),
        ),
        migrations.AlterField(
            model_name='status',
            name='value',
            field=models.CharField(max_length=100),
        ),
    ]
