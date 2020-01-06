# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0147_remove_event_cdn_subtitles_root_folder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='ftp_subfolders_extensions',
        ),
        migrations.DeleteModel(
            name='Folders_Extensions',
        ),
    ]
