# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0077_auto_20151211_0145'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='tweet',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
