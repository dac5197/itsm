# Generated by Django 3.1.3 on 2020-11-10 22:11

import base.models
from django.db import migrations, models
import django.db.models.deletion
import ticket.models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_auto_20201110_1323'),
        ('ticket', '0004_auto_20201110_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='resolution',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incident',
            name='resolved',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='incident',
            name='number',
            field=models.CharField(default=ticket.models.increment_inc_number, editable=False, max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='priority',
            name='sysID',
            field=models.OneToOneField(default=base.models.SysID.add_new, editable=False, on_delete=django.db.models.deletion.CASCADE, to='base.sysid'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='sysID',
            field=models.OneToOneField(default=base.models.SysID.add_new, editable=False, on_delete=django.db.models.deletion.CASCADE, to='base.sysid'),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100, unique=True)),
                ('sysID', models.OneToOneField(default=base.models.SysID.add_new, editable=False, on_delete=django.db.models.deletion.CASCADE, to='base.sysid')),
                ('ticket_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ticket.tickettype')),
            ],
            options={
                'verbose_name_plural': 'Statuses',
            },
        ),
    ]
