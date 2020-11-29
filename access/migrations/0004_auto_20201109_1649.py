# Generated by Django 3.1.3 on 2020-11-09 21:49

import base.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_auto_20201109_0931'),
        ('access', '0003_auto_20201109_1327'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('address', models.CharField(max_length=100, unique=True)),
                ('city', models.CharField(max_length=100, unique=True)),
                ('state', models.CharField(max_length=100, unique=True)),
                ('zipcode', models.CharField(max_length=100, unique=True)),
                ('x_coord', models.FloatField(blank=True, null=True)),
                ('y_coord', models.FloatField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('sysID', models.OneToOneField(default=base.models.SysID.add_new, on_delete=django.db.models.deletion.CASCADE, to='base.sysid')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('is_assignment', models.BooleanField(default=False)),
                ('is_approval', models.BooleanField(default=False)),
                ('is_heirarchal', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now_add=True)),
                ('active', models.BooleanField(default=True)),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='group_manager', to='access.customer')),
                ('members', models.ManyToManyField(related_name='group_membership', to='access.Customer')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.group')),
                ('sysID', models.OneToOneField(default=base.models.SysID.add_new, on_delete=django.db.models.deletion.CASCADE, to='base.sysid')),
            ],
        ),
        migrations.AddField(
            model_name='customer',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='access.location'),
        ),
    ]
