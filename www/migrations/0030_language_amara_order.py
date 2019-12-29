# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0029_remove_language_amara_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='language',
            name='amara_order',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
