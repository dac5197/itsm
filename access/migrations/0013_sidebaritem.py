# Generated by Django 3.1.3 on 2020-12-18 22:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('access', '0012_itsmgroup_roles'),
    ]

    operations = [
        migrations.CreateModel(
            name='SidebarItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('path', models.CharField(max_length=25, unique=True)),
                ('order', models.IntegerField(blank=True, null=True)),
                ('url', models.CharField(blank=True, max_length=200, null=True)),
                ('roles', models.ManyToManyField(blank=True, related_name='allowed_roles', to='access.Role')),
            ],
        ),
    ]