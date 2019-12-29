# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0118_speaker_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='speaker_json_link',
            field=models.URLField(blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='speaker_json_version',
            field=models.CharField(max_length=50, blank=True, default='0.0'),
            preserve_default=True,
        ),
    ]
