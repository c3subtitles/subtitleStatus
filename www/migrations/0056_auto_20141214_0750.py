# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0055_auto_20141214_0528'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='link_to_video_file',
            field=models.URLField(blank=True, default='', max_length=300),
        ),
    ]
