# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0097_auto_20160626_1613'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
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
    ]
