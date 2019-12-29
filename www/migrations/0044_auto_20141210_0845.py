# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0043_auto_20141210_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='video_duration',
            field=models.TimeField(default='00:00', blank=True),
        ),
    ]
