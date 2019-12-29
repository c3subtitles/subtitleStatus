# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0107_auto_20161009_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics_raw',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('start', models.TimeField(null=True, blank=True)),
                ('end', models.TimeField(null=True, blank=True)),
                ('time_delta', models.FloatField(null=True, blank=True)),
                ('words', models.IntegerField(null=True, blank=True)),
                ('strokes', models.IntegerField(null=True, blank=True)),
                ('recalculate_statistics', models.BooleanField(default=False)),
                ('speaker', models.ForeignKey(to='www.Speaker')),
                ('talk', models.ForeignKey(to='www.Talk')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.SeparateDatabaseAndState(
            None,
            [
                migrations.CreateModel(
                    name='Talk_Persons',
                    fields=[
                        ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                        ('speaker', models.ForeignKey(to='www.Speaker')),
                        ('talk', models.ForeignKey(to='www.Talk')),
                    ],
                    options={
                        'abstract': False,
                    },
                    bases=(models.Model,),
                ),
                migrations.AddField(
                    model_name='talk',
                    name='persons_new',
                    field=models.ManyToManyField(to='www.Speaker', through='www.Talk_Persons', default=None, blank=True),
                ),
                migrations.RemoveField(
                    model_name='talk',
                    name='persons',
                ),
                migrations.RenameField(
                    model_name='talk',
                    old_name='persons_new',
                    new_name='persons'
                ),
            ],
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='touched',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='average_spm',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='average_wpm',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='recalculate_statistics',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='strokes',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='time_delta',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='Talk_Persons',
            name='words',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='statistics_raw_data',
            name='speaker',
        ),
        migrations.RemoveField(
            model_name='statistics_raw_data',
            name='talk',
        ),
        migrations.DeleteModel(
            name='Statistics_Raw_Data',
        ),
        migrations.AddField(
            model_name='talk',
            name='recalculate_speakers_statistics',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='talk',
            old_name='recalculate_statistics',
            new_name='recalculate_talk_statistics',
        ),
        migrations.AddField(
            model_name='talk',
            name='speakers_strokes',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='speakers_time_delta',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='talk',
            name='speakers_words',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
