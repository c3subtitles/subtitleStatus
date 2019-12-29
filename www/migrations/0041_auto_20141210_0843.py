# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0040_auto_20141210_0843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='date',
            field=models.DateTimeField(blank=True, default='1970-01-01'),
        ),
    ]
