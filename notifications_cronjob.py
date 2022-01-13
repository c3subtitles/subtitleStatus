#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks all the notifications-flags and executes the
# notification functions
#
# Run this script as cronjob!
#
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

from www.models import Subtitle, Talk

# Check for "Transcript is available" and notify
my_talks = Talk.objects.filter(notify_transcript_available = True)
for t in my_talks:
    t.do_notify_transcript_available()

# Check for "Subtitle needs autotiming" and notify
my_subtitles = Subtitle.objects.filter(notify_subtitle_needs_timing = True)
for s in my_subtitles:
    s.do_notify_subtitle_needs_timing()

# Check for "Subtitle is ready for quality control" and notify
my_subtitles = Subtitle.objects.filter(notify_subtitle_ready_for_quality_control = True)
for s in my_subtitles:
    s.do_notify_subtitle_ready_for_quality_control()

# Check for "Subtitle is released" and notify
# Get all Subtitles which are already synced to the sync folder and still might need a notification
my_subtitles = Subtitle.objects.filter(notify_subtitle_released = True, needs_sync_to_sync_folder = False)
for s in my_subtitles:
    s.do_notify_subtitle_released()
