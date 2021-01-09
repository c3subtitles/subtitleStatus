# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0037_auto_20141210_0800'),
    ]

    operations = [
        migrations.AlterField(
            model_name='talk',
            name='abstract',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='amara_key',
            field=models.CharField(max_length=20, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='date',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='day',
            field=models.ForeignKey(blank=True, to='www.Event_Days', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='duration',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='event',
            field=models.ForeignKey(blank=True, to='www.Event', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='link_to_logo',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='link_to_readable_pad',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='link_to_video_file',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='link_to_writable_pad',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='orig_language',
            field=models.ForeignKey(blank=True, to='www.Language', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='pad_id',
            field=models.CharField(max_length=30, blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='talk',
            name='persons',
            field=models.ManyToManyField(blank=True, default=None, to='www.Speaker'),
        ),
        migrations.AlterField(
            model_name='talk',
            name='room',
            field=models.ForeignKey(blank=True, to='www.Rooms', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='slug',
            field=models.SlugField(default='', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='start',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='subtitle_talk',
            field=models.CharField(max_length=100, blank=True, default=' '),
        ),
        migrations.AlterField(
            model_name='talk',
            name='title',
            field=models.CharField(max_length=50, blank=True, default='ohne Titel'),
        ),
        migrations.AlterField(
            model_name='talk',
            name='track',
            field=models.ForeignKey(blank=True, to='www.Tracks', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='type_of',
            field=models.ForeignKey(blank=True, to='www.Type_of', on_delete=models.PROTECT),
        ),
        migrations.AlterField(
            model_name='talk',
            name='video_duration',
            field=models.TimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='talk',
            name='youtube_key',
            field=models.CharField(max_length=20, blank=True),
        ),
    ]
