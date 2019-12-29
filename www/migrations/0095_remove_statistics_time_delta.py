# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0094_auto_20160623_0045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='statistics',
            name='time_delta',
        ),
    ]
