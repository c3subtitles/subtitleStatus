#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# Script for dumping whatever data you want
#==============================================================================

import os
import sys
from lxml import etree
#from urllib import request
from time import strftime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States, Talk_Persons



# Für andi für media

my_complete_subtitles = Subtitle.objects.filter(complete=True).order_by("last_changed_on_amara")

for any in my_complete_subtitles:
    print(any.talk.guid+";"+ any.language.lang_code_media+";"+any.language.lang_short_srt+";"+str(any.last_changed_on_amara)+";"+"https://mirror.selfnet.de/c3subtitles/"+any.talk.event.subfolder_in_sync_folder + "/" + any.talk.filename)



"""

# Für die Laufzettel
my_complete_subtitles = Subtitle.objects.filter(complete = True, is_original_lang = True)
id_list = []
for any in my_complete_subtitles:
    id_list.append(any.talk_id)
#print(len(id_list))
my_talks = Talk.objects.filter(unlisted = False).exclude(id__in=id_list).order_by("event_id", "day__index")
#print(my_talks.count())

for any_talk in my_talks:
    # Get related speakers
    this_persons = Talk_Persons.objects.filter(talk_id = any_talk.id)
    if this_persons.count() == 1:
        persons_string = this_persons[0].speaker.name

    else:
        counter_max = this_persons.count()
        counter = 1
        persons_string = this_persons[0].speaker.name
        while counter < counter_max:
            persons_string = persons_string + ", " + this_persons[counter].speaker.name
            counter += 1
   # print(persons_string, type(persons_string))

    print(any_talk.event.acronym + ";" + any_talk.frab_id_talk + ";" + str(any_talk.id) + ";" + str(any_talk.day.index) + ";" + str(any_talk.start.strftime("%H:%M")) + ";" + str(any_talk.duration.strftime("%H:%M")) + ";" + any_talk.orig_language.language_de[0:2] + ";" + any_talk.title + ";" + persons_string )

"""

"""
    print("%s;%s;%s;%s;" + \
        str(any_talk.start.strftime("%H:%M")) + \
        ";" + str(any_talk.duration.strftime("%H:%M")) +\
        ";%s;%s;%s" % (any_talk.event.acronym,\
        any_talk.frab_id_talk, \
        str(any_talk.id), \
        str(any_talk.day.index), \
        any_talk.orig_language.language_de[0:2], \
        any_talk.title, \
        persons_string))
"""
"""
    print("%s;%s;%s;%s;" + \
        str(any_talk.start.strftime("%H:%M")) + \
        ";" + str(any_talk.duration.strftime("%H:%M")) +\
        ";%s;%s;%s" % (any_talk.event.acronym,\
        any_talk.frab_id_talk, \
        str(any_talk.id), \
        str(any_talk.day.index), \
        any_talk.orig_language.language_de[0:2], \
        any_talk.title, \
        persons_string))
"""
"""

# Für Translations!
my_talks = Talk.objects.filter(event = 5, unlisted = False).order_by("day__index","date","start","room__room")
my_talks = my_talks.order_by("day_id__index", "date", "start", "room")
#print("frab_id;title;amara_key;youtube_key;video_duration;short_amara_link")


for every_talk in my_talks:
    print("Talk ID: %s Frab_ID: %s Titel: %s" % (every_talk.id, every_talk.frab_id_talk, every_talk.title))
    print("Adminer-Link Patrick: https://adminer.c3subtitles.de/?pgsql=&username=patrick&db=subtitlestatus&ns=public&edit=www_talk&where%5Bid%5D=" + str(every_talk.id))
    print("Adminer-Link Barbara: https://adminer.c3subtitles.de/?pgsql=&username=percidae&db=subtitlestatus&ns=public&edit=www_talk&where%5Bid%5D=" + str (every_talk.id))
    print("Video Link auf Youtube: https://youtube.com/watch?v=" + every_talk.youtube_key)
    print("Video Link auf c3subtitles: https://c3subtitles.de/talk/" + str(every_talk.id))
    if every_talk.duration == every_talk.video_duration:
        print("[] Talk-Länge eingetragen")
    else:
        print("[x] Talk-Länge eingetragen")
    print("[] Amara Link ist der selbe Talk wie auf c3subtitles")
    print("[] Erste Übersetzung auf Amara hinzugefügt (wenn existent)")
    print("[] Zweite Übersetzung auf Amara hinzugefügt (wenn existent)")
    print("[] Original Sprache Youtube Link in der DB stimmt")
    print("[] Erste Übersetzung youtube Link in der DB stimmt")
    print("[] Zweite Übersetzung youtube Link in der DB stimmt")
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
"""
