# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0085_auto_20160510_1834'),
    ]

    operations = [
        migrations.AddField(
            model_name='talk',
            name='file_name',
            field=models.SlugField(max_length=200, default='', blank=True),
            preserve_default=True,
        ),
    ]
