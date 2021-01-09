# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0003_auto_20141207_0204'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('schedule_version', models.CharField(default='0.0', max_length=50)),
                ('acronym', models.CharField(default='', max_length=20)),
                ('title', models.CharField(default='No title yet', max_length=100)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('timeslot_duration', models.TimeField()),
                ('days', models.PositiveSmallIntegerField(default=1)),
                ('schedule_xml_link', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Event_Days',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('index', models.PositiveSmallIntegerField(default=0)),
                ('date', models.DateField()),
                ('day_start', models.DateTimeField()),
                ('day_end', models.DateTimeField()),
                ('event', models.ForeignKey(to='www.Event', on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('language_en', models.CharField(default='', max_length=40)),
                ('language_de', models.CharField(default='', max_length=40)),
                ('lang_short_2', models.CharField(unique=True, default='', max_length=3)),
                ('lang_amara_short', models.CharField(unique=True, default='', max_length=15)),
                ('lang_short_srt', models.CharField(default='', max_length=15)),
                ('language_native', models.CharField(default='', max_length=40)),
                ('amara_order', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Links',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('url', models.URLField()),
                ('title', models.CharField(default='Link title', max_length=50)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rooms',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('room', models.CharField(default='kein Raum', max_length=30)),
                ('building', models.CharField(default='', max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('frab_id_speaker', models.PositiveSmallIntegerField(default=-1)),
                ('name', models.CharField(default='', max_length=30)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='States',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('state_de', models.CharField(max_length=100)),
                ('state_en', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subtitle',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('is_original_lang', models.BooleanField(default=False)),
                ('revision', models.PositiveSmallIntegerField(default=0)),
                ('complete', models.BooleanField(default=False)),
                ('time_processed_transcribing', models.TimeField(default='00:00')),
                ('time_processed_syncing', models.TimeField(default='00:00')),
                ('time_processed_translating', models.TimeField(default='00:00')),
                ('comment', models.TextField(default='')),
                ('language', models.ForeignKey(to='www.Language', to_field='lang_amara_short', on_delete=models.PROTECT)),
                ('state', models.ForeignKey(to='www.States', on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Talk',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('frab_id_talk', models.PositiveSmallIntegerField(default=-1)),
                ('blacklisted', models.BooleanField(default=False)),
                ('link_to_logo', models.URLField(default='')),
                ('date', models.DateTimeField()),
                ('start', models.TimeField()),
                ('duration', models.TimeField()),
                ('title', models.CharField(default='ohne Titel', max_length=50)),
                ('subtitle_talk', models.CharField(default=' ', max_length=100)),
                ('abstract', models.TextField(default='')),
                ('description', models.TextField(default='')),
                ('pad_id', models.CharField(default='', max_length=30)),
                ('link_to_writable_pad', models.URLField(default='')),
                ('link_to_readable_pad', models.URLField(default='')),
                ('link_to_video_file', models.URLField(default='')),
                ('amara_key', models.CharField(default='', max_length=20)),
                ('youtube_key', models.CharField(default='', max_length=20)),
                ('video_duration', models.TimeField(default='00:00')),
                ('day', models.ForeignKey(to='www.Event_Days', on_delete=models.PROTECT)),
                ('event', models.ForeignKey(to='www.Event', on_delete=models.PROTECT)),
                ('orig_language', models.ForeignKey(to='www.Language', to_field='lang_short_2', on_delete=models.PROTECT)),
                ('persons', models.ManyToManyField(default=None, to='www.Speaker')),
                ('room', models.ForeignKey(to='www.Rooms', on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='subtitle',
            name='talk',
            field=models.ForeignKey(to='www.Talk', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='links',
            name='talk',
            field=models.ForeignKey(to='www.Talk', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Tracks',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('track', models.CharField(default='', max_length=20)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='talk',
            name='track',
            field=models.ForeignKey(to='www.Tracks', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Type_of',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('type_of_talk', models.CharField(default='', max_length=20)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='talk',
            name='type_of',
            field=models.ForeignKey(to='www.Type_of', on_delete=models.PROTECT),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='Test',
        ),
    ]
