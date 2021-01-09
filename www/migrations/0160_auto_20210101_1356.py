# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0159_auto_20201231_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='frab_id',
            field=models.CharField(max_length=50, blank=True, default='-1'),
        ),
    ]
