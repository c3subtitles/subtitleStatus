#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script tweets about released subtitles
# It checks the "tweet" flag and if the syn_to_ftp flag is on false again to
# be sure the file is already released
#
# Currently the YT-Flags are ignored!
# Only updates on media are tweeted
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Subtitle
import tweets

my_subtitles = Subtitle.objects.filter(tweet = True, needs_sync_to_ftp = False)

for s in my_subtitles:
    tweet_subtitles_update_media(s.id)
    s.tweet = False
    s.save()