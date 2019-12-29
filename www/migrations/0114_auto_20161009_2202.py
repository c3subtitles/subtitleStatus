# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0113_auto_20161009_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='speakers_average_spm',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='speakers_average_wpm',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
