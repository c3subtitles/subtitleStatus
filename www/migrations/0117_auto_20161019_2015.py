# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0116_auto_20161017_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='abstract',
            field=models.TextField(blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='speaker',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=True,
        ),
    ]
