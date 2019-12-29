# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0018_auto_20141210_0415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='language',
            name='lang_short_2',
            field=models.CharField(max_length=3, default=''),
        ),
        #migrations.AlterField(
        #    model_name='talk',
        #    name='orig_language',
        #    field=models.ForeignKey(to='www.Language'),
        #),
    ]
