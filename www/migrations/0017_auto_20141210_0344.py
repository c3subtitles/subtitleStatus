# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0016_auto_20141208_0416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracks',
            name='track',
            field=models.CharField(max_length=50, default=''),
        ),
    ]
