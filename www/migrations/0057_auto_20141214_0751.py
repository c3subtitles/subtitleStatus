# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0056_auto_20141214_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='link_to_video_file',
            field=models.URLField(blank=True, max_length=400, default=''),
        ),
    ]
