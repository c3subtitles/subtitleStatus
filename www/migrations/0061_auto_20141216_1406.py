# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0060_auto_20141216_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='track',
            field=models.ForeignKey(to='www.Tracks', blank=True, default=40, on_delete=models.SET_DEFAULT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='type_of',
            field=models.ForeignKey(to='www.Type_of', blank=True, default=6, on_delete=models.SET_DEFAULT),
        ),
    ]
