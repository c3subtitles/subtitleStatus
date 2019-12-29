# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0054_auto_20141210_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtitle',
            name='state',
            field=models.ForeignKey(blank=True, to='www.States', default=1),
        ),
    ]
