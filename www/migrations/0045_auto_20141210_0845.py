# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0044_auto_20141210_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='day',
            field=models.ForeignKey(blank=True, default=1, to='www.Event_Days'),
        ),
    ]
