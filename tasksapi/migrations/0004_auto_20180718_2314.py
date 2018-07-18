# Generated by Django 2.0.6 on 2018-07-18 23:14

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasksapi', '0003_auto_20180718_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='tasktype',
            name='environment_variables',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=list, help_text="A JSON array of environment variables to consume from the Celery worker's environment"),
        ),
        migrations.AlterField(
            model_name='taskqueue',
            name='user',
            field=models.ForeignKey(help_text='The creator of the queue', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]
