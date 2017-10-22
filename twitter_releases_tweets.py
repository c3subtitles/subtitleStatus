#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script tweets about released subtitles and about subtitels which need
# review
# It checks the "tweet" flag and if the syn_to_ftp flag is on false again to
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

# Set all finished subtitles to "tweet"
"""
my_subtitles = Subtitle.objects.filter(complete = True)
for every in my_subtitles:
    every.tweet = True
    every.save()
print(my_subtitles.count())
"""

# Get all Subtitles which are already synced to the sync folder and still might need a tweet
my_subtitles = Subtitle.objects.filter(tweet = True, needs_sync_to_sync_folder = False)

# Tweet for every subtitle synced to sync folder if the file is already on the mirror
for s in my_subtitles:
    link = "https://mirror.selfnet.de/c3subtitles/" + s.talk.event.subfolder_in_sync_folder + "/" + s.get_filename_srt()
    try:
        request = requests.head(link)
    except:
        continue
    # Only tweet it the file is on the mirror
    if request.status_code == 200:
        tweets.tweet_subtitles_update_mirror(s.id)
        s.tweet = False
        s.save()
    else:
        continue

# Tweet which talk needs an Review
my_subtitles = Subtitle.objects.filter(state_id = 7, tweet_autosync_done = True)
for s in my_subtitles:
    tweets.tweet_subtitle_needs_quality_control(s.id)
    s.tweet_autosync_done = False
    s.save()