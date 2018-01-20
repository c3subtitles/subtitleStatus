#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# Script for dumping whatever data you want
#==============================================================================

import os
import sys
from lxml import etree
#from urllib import request

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States
"""
# Für Translations!
my_talks = Talk.objects.filter(event = 4, blacklisted = False).order_by("day__index","date","start","room__room")
my_talks = my_talks.order_by("day_id__index", "date", "start", "room")
#print("frab_id;title;amara_key;youtube_key;video_duration;short_amara_link")

for every_talk in my_talks:
    print(str(every_talk.start)[0:-3]+" +"+str(every_talk.duration)[0:-3]+", "+every_talk.room.room+", "+every_talk.orig_language.lang_amara_short)
    print("https://events.ccc.de/congress/2015/Fahrplan/events/"+str(every_talk.frab_id_talk)+".html")
    print(every_talk.type_of.type+": "+every_talk.title)
    speaker = ""
    all_speaker = every_talk.persons.all()
    for every_speaker in all_speaker:
        speaker += every_speaker.name
        speaker += ", "
    print("speaker: "+str(speaker[0:-2]))
    print("translators: ")
    print("\n")
"""
"""
    print(every_talk.frab_id_talk,";",every_talk.title,";",every_talk.amara_key,";",every_talk.youtube_key,";",every_talk.video_duration,";")
"""

"""
# Nur Übersetzt
my_subtitles = Subtitle.objects.filter(complete = True, is_original_lang = False)

for every in my_subtitles:
    every.time_processed_translating =  every.time_quality_check_done = every.talk.video_duration
    print(every.time_processed_translating)
    every.save()
"""


# Subtitles which have no change date yet (for Patrick)
my_subtitles = Subtitle.objects.filter(last_changed_on_amara = "0001-01-01 00:00:00.000000").order_by("talk_id")
print(my_subtitles.count())

for this_subtitle in my_subtitles:
    my_string = "Amara: https://www.amara.org/de/videos/"
    my_string += this_subtitle.talk.amara_key
    my_string += "/"
    my_string += this_subtitle.language.lang_amara_short
    my_string += "/ \nAdminer: https://subtitles.media.ccc.de/adminer/?pgsql=&username=patrick&db=subtitlestatus&ns=public&edit=www_subtitle&where%5Bid%5D="
    my_string += str(this_subtitle.id)
    my_string += " \nCheck: "
    my_string += "https://subtitles.media.ccc.de/talk/"
    my_string += str(this_subtitle.talk.id)
    my_string += "\n"
    #print(this_subtitle.last_changed_on_amara)
    print(my_string)
