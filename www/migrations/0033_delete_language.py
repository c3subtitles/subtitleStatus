# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0032_auto_20141210_0621'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Language',
        ),
    ]
