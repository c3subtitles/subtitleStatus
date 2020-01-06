# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0151_auto_20200102_1821'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subtitle',
            name='yt_caption_id',
        ),
    ]
