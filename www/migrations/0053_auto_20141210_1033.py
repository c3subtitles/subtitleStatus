# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0052_auto_20141210_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='links',
            name='title',
            field=models.CharField(default='Link title', blank=True, max_length=100),
        ),
    ]
