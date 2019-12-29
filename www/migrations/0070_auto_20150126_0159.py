# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0069_auto_20150126_0040'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folders_Extensions',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('subfolder', models.CharField(max_length=10, blank=True, default='')),
                ('file_extension', models.CharField(max_length=10, blank=True, default='')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='ftp_startfolder',
            field=models.CharField(max_length=100, blank=True, default=''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='ftp_subfolders_extensions',
            field=models.ManyToManyField(to='www.Folders_Extensions', blank=True, default=None),
            preserve_default=True,
        ),
    ]
