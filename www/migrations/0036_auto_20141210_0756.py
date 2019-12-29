# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0035_auto_20141210_0625'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='acronym',
            field=models.CharField(default='', blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(default='No title yet', blank=True, max_length=100),
        ),
    ]
