# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0033_delete_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('language_en', models.CharField(default='', max_length=40)),
                ('language_de', models.CharField(default='', max_length=40)),
                ('lang_short_2', models.CharField(default='', max_length=3)),
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
        migrations.AddField(
            model_name='subtitle',
            name='language',
            field=models.ForeignKey(default=1, to='www.Language'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='is_original_lang',
        ),
    ]
