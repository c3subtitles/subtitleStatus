# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0144_talk_c3subtitles_youtube_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='internal_comment',
            field=models.CharField(default='', max_length=300),
        ),
    ]
