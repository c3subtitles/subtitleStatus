# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0155_auto_20200103_2047'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='kanboard_private_project_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='kanboard_public_project_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subtitle',
            name='kanboard_private_task_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subtitle',
            name='kanboard_public_task_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
