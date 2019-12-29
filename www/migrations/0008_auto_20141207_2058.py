# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0007_auto_20141207_1535'),
    ]

    operations = [
        migrations.RenameField(
            model_name='speaker',
            old_name='frab_id_speaker',
            new_name='frab_id',
        ),
        migrations.AddField(
            model_name='talk',
            name='slug',
            field=models.SlugField(default='', max_length=200),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='type_of',
            old_name='type_of_talk',
            new_name='type',
        ),
    ]
