# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0067_auto_20150125_2224'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='needs_delete_from_ftp',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subtitle',
            name='needs_sync_to_ftp',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
