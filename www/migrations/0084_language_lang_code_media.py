# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0083_talk_guid'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='lang_code_media',
            field=models.CharField(blank=True, max_length=3, default=''),
            preserve_default=True,
        ),
    ]
