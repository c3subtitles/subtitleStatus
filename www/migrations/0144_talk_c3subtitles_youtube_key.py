# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0143_auto_20191227_1406'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='c3subtitles_youtube_key',
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
