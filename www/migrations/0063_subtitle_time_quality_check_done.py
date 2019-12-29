# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0062_auto_20141216_1409'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='time_quality_check_done',
            field=models.TimeField(blank=True, default='00:00'),
            preserve_default=True,
        ),
    ]
