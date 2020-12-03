# Generated by Django 3.1.3 on 2020-12-03 18:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_attachment'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]