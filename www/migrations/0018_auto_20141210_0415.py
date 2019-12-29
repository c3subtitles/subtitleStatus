# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0017_auto_20141210_0344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='name',
            field=models.CharField(max_length=50, default=''),
        ),
    ]
