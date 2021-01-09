# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0100_auto_20161009_1253'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('start', models.TimeField(blank=True, null=True)),
                ('end', models.TimeField(blank=True, null=True)),
                ('time_delta', models.FloatField(blank=True, null=True)),
                ('words', models.IntegerField(blank=True, null=True)),
                ('strokes', models.IntegerField(blank=True, null=True)),
                ('speaker', models.ForeignKey(to='www.Speaker', on_delete=models.PROTECT)),
                ('talk', models.ForeignKey(to='www.Talk', on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='statistics_raw',
            name='speaker',
        ),
        migrations.RemoveField(
            model_name='statistics_raw',
            name='talk',
        ),
        migrations.DeleteModel(
            name='Statistics_raw',
        ),
    ]
