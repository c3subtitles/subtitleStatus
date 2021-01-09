# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0163_auto_20210101_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtitle',
            name='kanboard_private_task_id',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='kanboard_public_task_id',
        ),
        migrations.AddField(
            model_name='subtitle',
            name='draft_needs_removal_from_sync_folder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subtitle',
            name='draft_needs_sync_to_sync_folder',
            field=models.BooleanField(default=False),
        ),
    ]
