# Generated by Django 3.2.10 on 2024-01-18 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('www', '0184_event_use_all_webpages_urls_to_find_filenames_and_video_urls'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='lang_subst_json',
            field=models.TextField(default='{"en":"eng", "de":"deu"}'),
        ),
        migrations.AlterField(
            model_name='event',
            name='speaker_json_version',
            field=models.CharField(blank=True, default='0.0', max_length=100),
        ),
        migrations.AlterField(
            model_name='event',
            name='use_all_webpages_urls_to_find_filenames_and_video_urls',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='rooms',
            name='room',
            field=models.CharField(default='kein Raum', max_length=60),
        ),
        migrations.AlterField(
            model_name='talk',
            name='c3subtitles_youtube_key',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='talk',
            name='link_to_video_file',
            field=models.URLField(blank=True, default='', max_length=220),
        ),
    ]
