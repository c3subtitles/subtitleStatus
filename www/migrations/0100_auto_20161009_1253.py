# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0099_auto_20160626_2100'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics_raw',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('start', models.TimeField(blank=True, null=True)),
                ('end', models.TimeField(blank=True, null=True)),
                ('time_delta', models.FloatField(blank=True, null=True)),
                ('words', models.IntegerField(blank=True, null=True)),
                ('strokes', models.IntegerField(blank=True, null=True)),
                ('speaker', models.ForeignKey(to='www.Speaker')),
                ('talk', models.ForeignKey(to='www.Talk')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='speaker',
        ),
        migrations.RemoveField(
            model_name='statistics',
            name='talk',
        ),
        migrations.DeleteModel(
            name='Statistics',
        ),
    ]
