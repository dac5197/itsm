# Generated by Django 3.1.3 on 2020-11-30 13:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tracking', '0008_fieldchange'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worknote',
            name='changed_json',
        ),
        migrations.AlterField(
            model_name='fieldchange',
            name='work_note_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tracking.worknote'),
        ),
    ]
