# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0051_auto_20141210_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='links',
            name='talk',
            field=models.ForeignKey(to='www.Talk', blank=True, on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='links',
            name='title',
            field=models.CharField(max_length=50, default='Link title', blank=True),
        ),
        migrations.AlterField(
            model_name='links',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]
