# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0071_auto_20150126_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='folders_extensions',
            name='subfolder',
            field=models.CharField(default='', max_length=10, blank=True),
        ),
    ]
