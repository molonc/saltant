# Generated by Django 2.0.6 on 2018-07-05 23:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0026_auto_20180705_2253'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TaskScheduler',
        ),
    ]
