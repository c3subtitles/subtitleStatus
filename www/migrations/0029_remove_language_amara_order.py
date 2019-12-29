# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0020_convert_subtitle_language_to_language_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='amara_order',
        ),
    ]
