# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0122_event_blacklisted'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='cdn_subtitles_root_folder',
            field=models.URLField(default='', blank=True),
        ),
    ]
