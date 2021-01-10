# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import make_aware
from datetime import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0081_subtitle_tweet_autosync_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='last_changed_on_amara',
            field=models.DateTimeField(default=make_aware(datetime.min), blank=True),
            preserve_default=True,
        ),
    ]
