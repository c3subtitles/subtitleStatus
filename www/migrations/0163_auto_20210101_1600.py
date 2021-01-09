# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0162_auto_20210101_1558'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tracks',
            name='track',
            field=models.CharField(max_length=50, default=''),
        ),
        migrations.AlterField(
            model_name='type_of',
            name='type',
            field=models.CharField(max_length=80, default=''),
        ),
    ]
