# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0102_auto_20161009_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='strokes',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='time_delta',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='words',
            field=models.IntegerField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
