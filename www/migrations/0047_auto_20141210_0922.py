# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0046_auto_20141210_0846'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='title',
            field=models.CharField(default='ohne Titel', blank=True, max_length=100),
        ),
    ]
