# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0091_speaker_doppelgaenger_of'),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('start', models.TimeField(blank=True)),
                ('end', models.TimeField(blank=True)),
                ('time_delta', models.TimeField(blank=True)),
                ('words', models.IntegerField(blank=True)),
                ('strokes', models.IntegerField(blank=True)),
                ('speaker', models.ForeignKey(to='www.Speaker', on_delete=models.PROTECT)),
                ('subtitle', models.ForeignKey(to='www.Subtitle', on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
