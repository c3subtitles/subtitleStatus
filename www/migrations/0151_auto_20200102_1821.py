# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0150_auto_20200102_1759'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtitle',
            name='needs_removal_from_YT',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='needs_removal_from_ftp',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='needs_sync_to_YT',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='needs_sync_to_ftp',
        ),
    ]
