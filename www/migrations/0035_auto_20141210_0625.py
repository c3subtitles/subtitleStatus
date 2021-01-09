# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0034_auto_20141210_0624'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='is_original_lang',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='orig_language',
            field=models.ForeignKey(default=1, to='www.Language', on_delete=models.SET_DEFAULT),
            preserve_default=False,
        ),
    ]
