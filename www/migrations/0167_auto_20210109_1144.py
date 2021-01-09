# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0166_auto_20210108_1944'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='primary_amara_video_link',
            field=models.URLField(max_length=400, blank=True, default=''),
        ),
    ]
