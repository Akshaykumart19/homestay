# Generated by Django 5.0 on 2024-12-14 17:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_touristlocation_link_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='status',
        ),
    ]
