# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0125_event_subfolder_in_sync_folder'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='needs_removal_from_sync_folder',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='subtitle',
            name='needs_sync_to_sync_folder',
            field=models.BooleanField(default=False),
        ),
    ]
