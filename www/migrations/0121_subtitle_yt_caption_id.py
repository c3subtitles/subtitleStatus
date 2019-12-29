# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0120_auto_20161019_2037'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='yt_caption_id',
            field=models.CharField(default='', blank=True, max_length=50),
            preserve_default=True,
        ),
    ]
