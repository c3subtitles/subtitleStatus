# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0039_auto_20141210_0814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
