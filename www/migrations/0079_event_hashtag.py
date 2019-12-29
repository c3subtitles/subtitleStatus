# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0078_subtitle_tweet'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='hashtag',
            field=models.CharField(blank=True, max_length=10, default=''),
            preserve_default=True,
        ),
    ]
