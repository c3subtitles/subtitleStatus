# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0114_auto_20161009_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='statistics_event',
            name='n_most_frequent_words',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='statistics_speaker',
            name='n_most_frequent_words',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='n_most_frequent_words',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='n_most_frequent_words_speakers',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk_persons',
            name='n_most_frequent_words',
            field=models.TextField(default=''),
            preserve_default=True,
        ),
    ]
