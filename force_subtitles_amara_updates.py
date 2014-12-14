#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script removes all revisions from every subtitle in the database
# which causes the amara_import script to recheck every subtitle in the
# database
#==============================================================================

import os
import sys
from lxml import etree
from urllib import request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Subtitle

all_subtitles = Subtitle.objects.all()

for every_subtitle in all_subtitles:
    every_subtitle.revision = 0
    every_subtitle.save()

print("Alle Subtitles-Datensätze zurück gesetzt!")


