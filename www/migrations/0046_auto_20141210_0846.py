# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0045_auto_20141210_0845'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='event',
            field=models.ForeignKey(blank=True, to='www.Event', default='0', on_delete=models.SET_DEFAULT),
        ),
    ]
