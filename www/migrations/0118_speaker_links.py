# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0117_auto_20161019_2015'),
    ]

    operations = [
        migrations.CreateModel(
            name='Speaker_Links',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200, blank=True, default='')),
                ('url', models.URLField(blank=True)),
                ('speaker', models.ForeignKey(to='www.Speaker', blank=True, on_delete=models.PROTECT)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
