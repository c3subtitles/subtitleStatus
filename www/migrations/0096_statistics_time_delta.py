# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0095_remove_statistics_time_delta'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics',
            name='time_delta',
            field=models.FloatField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
