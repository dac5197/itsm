# Generated by Django 3.1.3 on 2020-12-03 18:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_attachment_created'),
        ('tracking', '0010_auto_20201203_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worknote',
            name='foreign_sysID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.sysid'),
        ),
    ]