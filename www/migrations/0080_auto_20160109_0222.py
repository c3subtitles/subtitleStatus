# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0079_event_hashtag'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='needs_removal_from_YT',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subtitle',
            name='needs_sync_to_YT',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='youtube_key_t_1',
            field=models.CharField(max_length=20, default='', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='youtube_key_t_2',
            field=models.CharField(max_length=20, default='', blank=True),
            preserve_default=True,
        ),
    ]
