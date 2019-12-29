# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0080_auto_20160109_0222'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='tweet_autosync_done',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
