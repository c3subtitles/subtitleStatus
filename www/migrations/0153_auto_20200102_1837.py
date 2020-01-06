# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0152_remove_subtitle_yt_caption_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='talk',
            name='youtube_key_t_1',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='youtube_key_t_2',
        ),
    ]
