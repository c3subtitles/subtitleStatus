# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0059_auto_20141215_2340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='room',
            field=models.ForeignKey(to='www.Rooms', default=15, on_delete=models.SET_DEFAULT),
        ),
    ]
