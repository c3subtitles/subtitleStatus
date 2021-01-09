# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0165_remove_talk_youtube_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='additional_amara_video_links',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='talk',
            name='primary_amara_video_link',
            field=models.TextField(blank=True, default=''),
        ),
    ]
