#!/usr/bin/python3
"""This script takes a video file and converts it into audio with a black image, to upload the new video to youtube
"""
import argparse
import os
import shutil
import sys
import tempfile
import subprocess

import django
import requests
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from www.models import Subtitle, Talk
from YouTubeClient import YouTubeClient

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

django.setup()


parser = argparse.ArgumentParser(description='Upload audio-only video to youtube')
parser.add_argument('frab_id', type=str, help='FRAB ID of the talk to process')

args = parser.parse_args()


def download_video(target_dir: str, url: str) -> str:
    """Downloads a video as stream, to keep memory consumption low

    Arguments:
        target_dir {str} -- Directory to save file in
        url {str} -- URL of the video
    Returns:
        str -- Path to the downloaded file
    """
    with requests.get(url, stream=True) as req:
        with open('{}/video'.format(target_dir), 'wb') as target:
            shutil.copyfileobj(req.raw, target)

    return '{}/video'.format(target_dir)

def ffmpeg_convert(workdir: str, video_path: str, image_path: str):
    """Convert a video in a given path with ffmpeg

    Arguments:
        workdir {str} -- Directory to work in
        video_path {str} -- Path to video
        image_path {str} -- Path to image to replace actual video
    Returns:
        str -- Path to the converted video
    """
    subprocess.run(['ffmpeg', '-i', video_path, '-i', image_path, '-filter_complex', '"[1][0]scale2ref[i][v];[v][i]overlay"', '-c:a', 'copy', 'out.mp4'], shell=True, check=True, cwd=workdir)

    return '{}/out.mp4'.format(workdir)


try:
    talk = Talk.objects.get(frab_id_talk = args.frab_id)
    yc = YouTubeClient()

    # try to download original video
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = download_video(tmpdir, talk.link_to_video_file)

        converted_video_path = ffmpeg_convert(tmpdir, video_path, 'static/black.png')

        # Upload to youtube, we optain a new video id
        youtube_key = yc.upload(converted_video_path, talk.title, talk.description)

        talk.c3subtitles_youtube_key = youtube_key

        talk.save()
except:
    print("Fehler!")
