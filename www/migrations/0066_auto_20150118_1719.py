# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0065_subtitle_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='building',
            field=models.CharField(blank=True, max_length=30, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='city',
            field=models.CharField(blank=True, max_length=30, default=''),
            preserve_default=True,
        ),
    ]
