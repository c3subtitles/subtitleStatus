# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0011_auto_20141208_0343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='event',
            name='start',
            field=models.DateField(),
        ),
    ]
