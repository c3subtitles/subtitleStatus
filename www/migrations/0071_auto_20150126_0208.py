# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0070_auto_20150126_0159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folders_extensions',
            name='subfolder',
            field=models.CharField(blank=True, max_length=20, default=''),
        ),
    ]
