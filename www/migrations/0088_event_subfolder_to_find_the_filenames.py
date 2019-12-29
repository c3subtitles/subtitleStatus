# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0087_auto_20160512_1845'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='subfolder_to_find_the_filenames',
            field=models.CharField(blank=True, default='', max_length=20),
            preserve_default=True,
        ),
    ]
