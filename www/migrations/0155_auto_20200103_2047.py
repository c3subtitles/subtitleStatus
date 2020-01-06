# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0154_auto_20200103_1730'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='internal_comment',
            field=models.CharField(default='', blank=True, max_length=300),
        ),
    ]
