#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script reads a json file which contains amara and youtube keys for
# talks identified by their frab id and puts the youtube_key and amara_key
# into the database
#==============================================================================

import os
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk

file = "/opt/subtitleStatus/barbara-temp/32c3-amara-videos_2.json"

with open(file, "r") as json_content:
    # Convert from string to usable sth
    content = json.load(json_content)
    
    # For every Talk in the json file
    for everything in content:
        # Filter associated talk
        my_talk = Talk.objects.get(frab_id_talk = everything['fahrplan_id'])
        print(str(my_talk.frab_id_talk) + ": "+my_talk.title)
        # Check if Amara-Keys are the same
        if my_talk.amara_key == everything['amara_id']:
            print("Gleicher Amara Key!")
        else:
            print("Nicht gleicher Amara Key!")
            my_talk.amara_key = everything['amara_id']
            my_talk.save()            
            print("Amara Key upgedated")
        print(str(my_talk.youtube_key))
        this_string = everything['youtube_url']
        #print(this_string)
        yt_key = this_string[-11:]
        print(yt_key)
        
        # Check if YT-Keys are the same
        if my_talk.youtube_key == yt_key:
            print("Gleicher YT Key!")
        else:
            print("Nicht gleicher YT Key!")
            my_talk.youtube_key = yt_key
            my_talk.save()
            print("YT-Key upgedated")
        print(" ")