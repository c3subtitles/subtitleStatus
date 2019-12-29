# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0104_auto_20161009_1321'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics_Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('words', models.IntegerField(null=True, blank=True)),
                ('strokes', models.IntegerField(null=True, blank=True)),
                ('time_delta', models.FloatField(null=True, blank=True)),
                ('average_wpm', models.FloatField(null=True, blank=True)),
                ('average_spm', models.FloatField(null=True, blank=True)),
                ('recalculate_statistics', models.BooleanField(default=False)),
                ('event', models.ForeignKey(to='www.Event')),
                ('language', models.ForeignKey(to='www.Language')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Statistics_Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('words', models.IntegerField(null=True, blank=True)),
                ('strokes', models.IntegerField(null=True, blank=True)),
                ('time_delta', models.FloatField(null=True, blank=True)),
                ('average_wpm', models.FloatField(null=True, blank=True)),
                ('average_spm', models.FloatField(null=True, blank=True)),
                ('recalculate_statistics', models.BooleanField(default=False)),
                ('language', models.ForeignKey(to='www.Language')),
                ('speaker', models.ForeignKey(to='www.Speaker')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
