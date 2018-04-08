#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script resets a talk from blocked to quality control in progress
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Subtitle, Talk

if len(sys.argv) != 2:
    sys.exit("Too many or less arguments, one is needed!")

subtitle_id = sys.argv[1]

try:
    subt = Subtitle.objects.get(id = subtitle_id)
    # Nur wenn der Untertitel orignal ist weiter machen und auf quality control setzen
    if subt.is_original_lang:
        my_talk = Talk.objects.get(id = subt.talk_id)
        subt.time_processed_transcribing = my_talk.video_duration
        subt.time_processed_syncing = my_talk.video_duration
        subt.needs_automatic_syncing = False
        subt.blocked = False
        subt.state_id = 7 # Quality control done until
        subt.tweet_autosync_done = True
        subt.save()
        # Let the related statistics be calculated
        subt.talk.reset_related_statistics_data()
        print("Done")
except:
    print("Fehler!")
