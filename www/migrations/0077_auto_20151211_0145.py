# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0076_auto_20151211_0137'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='title',
            field=models.CharField(blank=True, default='ohne Titel', max_length=150),
        ),
    ]
