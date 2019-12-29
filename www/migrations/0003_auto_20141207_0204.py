# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0002_subtitle_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('touched', models.DateTimeField(auto_now=True)),
                ('sth', models.CharField(max_length=50, default='0.0')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='event_days',
            name='event',
        ),
        migrations.RemoveField(
            model_name='links',
            name='talk',
        ),
        migrations.DeleteModel(
            name='Links',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='language',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='state',
        ),
        migrations.DeleteModel(
            name='States',
        ),
        migrations.RemoveField(
            model_name='subtitle',
            name='talk',
        ),
        migrations.DeleteModel(
            name='Subtitle',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='day',
        ),
        migrations.DeleteModel(
            name='Event_Days',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='event',
        ),
        migrations.DeleteModel(
            name='Event',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='orig_language',
        ),
        migrations.DeleteModel(
            name='Language',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='persons',
        ),
        migrations.DeleteModel(
            name='Speaker',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='room',
        ),
        migrations.DeleteModel(
            name='Rooms',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='track',
        ),
        migrations.RemoveField(
            model_name='talk',
            name='type_of',
        ),
        migrations.DeleteModel(
            name='Talk',
        ),
        migrations.DeleteModel(
            name='Tracks',
        ),
        migrations.DeleteModel(
            name='Type_of',
        ),
    ]
