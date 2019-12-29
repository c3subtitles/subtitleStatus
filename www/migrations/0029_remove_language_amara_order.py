# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0028_subtitle_language'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='language',
            name='amara_order',
        ),
    ]
