# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0121_subtitle_yt_caption_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='blacklisted',
            field=models.BooleanField(default=False),
        ),
    ]
