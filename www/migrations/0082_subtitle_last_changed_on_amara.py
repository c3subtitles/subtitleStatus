# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0081_subtitle_tweet_autosync_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='last_changed_on_amara',
            field=models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0), blank=True),
            preserve_default=True,
        ),
    ]
