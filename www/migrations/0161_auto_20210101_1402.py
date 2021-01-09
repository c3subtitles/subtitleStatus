# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0160_auto_20210101_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='title',
            field=models.CharField(max_length=200, blank=True, default='ohne Titel'),
        ),
    ]
