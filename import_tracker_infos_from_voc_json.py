#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script imports the infos from the voc tracker with all the
# youtube keys and amara keys for talks
# Test-File: https://dl.jeising.net/misc/amara-videos.json
# There are no datafields for the second and third youtube link yet!
#==============================================================================

import os
import urllib
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk

url = "https://dl.jeising.net/misc/amara-videos.json"

request = urllib.request.Request(url)
response = urllib.request.urlopen(request)
encoding = response.info().get_param('charset', 'utf8')
key_file = json.loads(response.read().decode(encoding))

#print(key_file)

for any in key_file:
    print(any["fahrplan_guid"])
    try:
        this_talk = Talk.objects.get(frab_id_talk = any["fahrplan_id"], guid = any["fahrplan_guid"])
        this_talk.amara_key = any["amara_id"]
        this_talk.youtube_key = any["youtube_url"][-11:]
        this_talk.link_to_video_file = any["youtube_url"]
        #this_talk.save()
    except:
        print("Entry with guid %s and frab_id %s failed!" % (any["fahrplan_guid"], any["fahrplan_id"]) )
