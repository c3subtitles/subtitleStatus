# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0119_auto_20161019_2033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='speaker',
            name='abstract',
            field=models.TextField(blank=True, null=True, default=''),
        ),
        migrations.AlterField(
            model_name='speaker',
            name='description',
            field=models.TextField(blank=True, null=True, default=''),
        ),
    ]
