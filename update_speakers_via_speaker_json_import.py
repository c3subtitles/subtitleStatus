#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks the speaker.json file in every event for new versions
# and imports the data
# 
# In the database you can mark urls to ignore with a "#" at the beginning
#
# This script can be run as cronjob via an event but it is not necessary
#==============================================================================

import os
import sys
import json
from urllib import request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.exceptions import ObjectDoesNotExist

from www.models import Event, Speaker, Speaker_Links

# Check all events, start always with the oldest
my_events = Event.objects.all().exclude(id = 3).order_by("start")

#all_urls = ["https://events.ccc.de/congress/2015/Fahrplan/speakers.json"]

# Check all events
for event in my_events:
    print(event.title)
    any_url = event.speaker_json_link
    event.save_speaker_json_file()
    # Stop here if the url starts with a '#' and start over with the next event
    if any_url[0:1] == "#":
        print("No active link, remove '#' to allow an update\n")
        continue
    response = request.urlopen(any_url)
    result = response.read()
    result = result.decode("utf8")
    result = json.loads(result)
    # Print Version
    print(result["schedule_speakers"]["version"])
    # if the version is the same than the one in the database, stop here
    if event.speaker_json_version == result["schedule_speakers"]["version"]:
        print("Not doing anything here, there is no new version available!\n")
        continue
    # Iterate over any speaker
    for any_speaker in result["schedule_speakers"]["speakers"]:
        #print(any_speaker["id"])
        #print(any_speaker["full_public_name"])
        #print(any_speaker["abstract"])
        #print(any_speaker["description"])
        #for any_link in any_speaker["links"]:
            #print(any_link["title"])
            #print(any_link["url"])
        # Get or create a speaker with the same frab id
        my_speaker, created = Speaker.objects.get_or_create(frab_id = any_speaker["id"])
        # Only alter the entry if the name has changed
        if my_speaker.name != any_speaker["full_public_name"]:
            my_speaker.name = any_speaker["full_public_name"]
            my_speaker.save()
        # Only alter the entry if the abstract has changed
        if my_speaker.abstract != any_speaker["abstract"]:
            my_speaker.abstract = any_speaker["abstract"]
            my_speaker.save()
        # Only alter the entry if the description has changed
        if my_speaker.description != any_speaker["description"]:
            my_speaker.description = any_speaker["description"]
            my_speaker.save()
        # Save Link data form this speaker into the database
        for any_link in any_speaker["links"]:
            my_speaker_link, created = Speaker_Links.objects.get_or_create(speaker = my_speaker, title = any_link["title"], url = any_link["url"])
            if created:
                my_speaker_link.save()
                
    event.speaker_json_version = result["schedule_speakers"]["version"]
    event.save()
    
        