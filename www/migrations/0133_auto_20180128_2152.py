# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import make_aware
from datetime import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0132_remove_talk_transcript_from_trint'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='amara_activity_last_checked',
            field=models.DateTimeField(default=make_aware(datetime.min), blank=True),
        ),
        migrations.AddField(
            model_name='talk',
            name='amara_complete_update_last_checked',
            field=models.DateTimeField(default=make_aware(datetime.min), blank=True),
        ),
        migrations.AddField(
            model_name='talk',
            name='amara_update_interval',
            field=models.TimeField(default='00:10', blank=True),
        ),
        migrations.AddField(
            model_name='talk',
            name='needs_complete_amara_update',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='talk',
            name='next_amara_activity_check',
            field=models.DateTimeField(default=make_aware(datetime.min), blank=True),
        ),
    ]
