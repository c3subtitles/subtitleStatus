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

from www.models import Subtitle

subtitle_id = 86

subt = Subtitle.objects.get(id = subtitle_id)
# Nur wenn der Untertitel orignal ist weiter machen und auf transcribing zurück setzen
if subt.is_original_lang:
    subt.time_processed_transcribing = "00:00:00"
    subt.time_processed_syncing = "00:00:00"
    subt.state_id = 2
    subt.blocked = False
    subt.save()
