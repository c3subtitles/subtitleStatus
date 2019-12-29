# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0084_language_lang_code_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='lang_code_iso_639_1',
            field=models.CharField(blank=True, default='', max_length=10),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='language',
            name='lang_short_2',
        ),
    ]
