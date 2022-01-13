#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# DEPRECATED this moved into class functions
# the cronjob is done via notifications_cronjob.py
#
# This script notifies about released subtitles and about subtitles which need
# review
# It checks the "notify_subtitle_released" flag and if the syn_to_ftp flag is on false again to
# be sure the file is already released
#
# Currently the YT-Flags are ignored!
# Only updates on media are tweeted
#==============================================================================

import os
import sys
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Subtitle
import tweets

# Set all finished subtitles to "notify_subtitle_released"
"""
my_subtitles = Subtitle.objects.filter(complete = True)
for every in my_subtitles:
    every.notify_subtitle_released = True
    every.save()
print(my_subtitles.count())
"""

# Get all Subtitles which are already synced to the sync folder and still might need a notification
my_subtitles = Subtitle.objects.filter(notify_subtitle_released = True, needs_sync_to_sync_folder = False)

# Notify for every subtitle synced to sync folder if the file is already on the mirror
for s in my_subtitles:
    link = "https://mirror.selfnet.de/c3subtitles/" + s.talk.event.subfolder_in_sync_folder + "/" + s.get_filename_srt()
    try:
        request = requests.head(link)
    except:
        continue
    # Only notify if the file is on the mirror
    if request.status_code == 200:
        tweets.tweet_subtitles_update_mirror(s.id)
        s.refresh_from_db()
        s.notify_subtitle_released = False
        s.save()
    else:
        continue

# Notify which talk needs an Review
my_subtitles = Subtitle.objects.filter(state_id = 7, notify_subtitle_ready_for_quality_control = True)
for s in my_subtitles:
    tweets.tweet_subtitle_needs_quality_control(s.id)
    s.refresh_from_db()
    s.notify_subtitle_ready_for_quality_control = False
    s.save()