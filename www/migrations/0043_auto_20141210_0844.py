# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0042_auto_20141210_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='duration',
            field=models.TimeField(default='00:45', blank=True),
        ),
    ]
