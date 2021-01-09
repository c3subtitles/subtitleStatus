# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0161_auto_20210101_1402'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracks',
            name='track',
            field=models.CharField(max_length=80, default=''),
        ),
    ]
