# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0146_remove_event_ftp_startfolder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='cdn_subtitles_root_folder',
        ),
    ]
