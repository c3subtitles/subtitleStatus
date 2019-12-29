# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0061_auto_20141216_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='orig_language',
            field=models.ForeignKey(default=287, to='www.Language', blank=True),
        ),
    ]
