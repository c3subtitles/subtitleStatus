# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0103_auto_20161009_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics_raw',
            name='recalculate_statistics',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='recalculate_statistics',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
