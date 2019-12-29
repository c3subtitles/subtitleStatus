# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0124_subtitle_blacklisted'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='subfolder_in_sync_folder',
            field=models.CharField(max_length=100, blank=True, default=''),
        ),
    ]
