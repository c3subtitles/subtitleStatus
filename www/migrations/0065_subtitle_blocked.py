# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0064_auto_20141222_1818'),
    ]

    operations = [
        migrations.AddField(
            model_name='subtitle',
            name='blocked',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
