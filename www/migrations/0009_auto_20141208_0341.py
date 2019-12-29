# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0008_auto_20141207_2058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateField(default='1970-01-01'),
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateField(default='1970-01-01'),
        ),
    ]
