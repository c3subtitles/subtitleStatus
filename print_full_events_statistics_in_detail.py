#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts prints some statistics about every event for comparison purposes
#==============================================================================

import os
#import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle, Event
from www.statistics_helper import calculate_seconds_from_time

import time
import datetime



def calculate_time(input):
    return_dict = {}
    return_dict["sum_seconds"] = int(input)
    return_dict["hours"] = int(input // 3600)
    input = input - return_dict["hours"] * 3600
    return_dict["minutes"] = int(input // 60)
    input = input - return_dict["minutes"] * 60
    return_dict["seconds"] = int(input)
    return return_dict

# Do this for any event
# Infos to print:
# How much hours:minutes has a event
# How much of that time has a transcript, is timed or is done for that event
my_events = Event.objects.all().exclude(id = 3)

timestamp = time.time()
time_now = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
#print(time_now)

csv_array = []


csv_title = ["Timestamp",
    "Eventname",
    "Anzahl Talks",
    "Sekunden Talk-Zeit",
    "Talk-Zeit",
    "Anzahl fertige Untertitel",
    "Sekunden fertige Untertitel",
    "Talk-Zeit mit fertigen Untertiteln",
    "Anzahl fertige Untertitel in der Vortragssprache",
    "Sekunden fertige Untertitel in der Vortragssprache",
    "Talk-Zeit fertige Untertitel in der Vortragssprache",
    "Anzahl übersetzte Untertitel",
    "Sekunden übersetzte Untertitel",
    "Talk-Zeit mit übersetzten Untertiteln",
    "Sekunden transkribierte Talk-Zeit",
    "Transkribierte Talk-Zeit",
    "Prozent Transkribiert",
    "Sekunden getimte Talk-Zeit",
    "Getimte Talk-Zeit",
    "Prozent Getimt",
    "Sekunden kontrollierte Talk-Zeit",
    "Kontrollierte Talk-Zeit",
    "Prozent kontrolliert"]

for any_event in my_events:
    csv_array.append(str(datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')))
    #print(any_event.acronym)
    csv_array.append(any_event.acronym)
    my_talks = any_event.talk_set.all().exclude(unlisted = True)
    full_seconds = 0
    for any_talk in my_talks:
        full_seconds += calculate_seconds_from_time(any_talk.video_duration)
    #print("%s Talks ohne optout" % (my_talks.count()))
    csv_array.append(str(my_talks.count()))
    #print("%s Sekunden Talk-Zeit" % (full_seconds))
    csv_array.append(str(full_seconds))
    talk_time = calculate_time(full_seconds)
    #print("%sh %smin %ssec Talk-Zeit" % (talk_time["hours"], talk_time["minutes"], talk_time["seconds"]))
    csv_array.append("%s:%s:%s" % (talk_time["hours"], talk_time["minutes"], talk_time["seconds"]))
    my_subtitles = Subtitle.objects.filter(talk__event = any_event, complete = True)
    full_subtitles_seconds = 0
    for any_subt in my_subtitles:
        full_subtitles_seconds += calculate_seconds_from_time(any_subt.talk.video_duration)
    full_time_subtitles = calculate_time(full_subtitles_seconds)
    #print("\n%s zugehörige fertige Untertitel" % (my_subtitles.count()))
    csv_array.append(str(my_subtitles.count()))
    #print("%s Sekunden fertige Untertitel" % (full_time_subtitles["sum_seconds"]))
    csv_array.append(str((full_time_subtitles["sum_seconds"])))
    #print("%sh %smin %ssec Talk-Zeit fertige Untertitel" % (full_time_subtitles["hours"], full_time_subtitles["minutes"], full_time_subtitles["seconds"]))
    csv_array.append(str("%s:%s:%s" % (full_time_subtitles["hours"], full_time_subtitles["minutes"], full_time_subtitles["seconds"])))
    
    full_subtitles_seconds_original = 0
    for any_subt in my_subtitles.filter(is_original_lang = True):
        full_subtitles_seconds_original += calculate_seconds_from_time(any_subt.talk.video_duration)
    full_time_subtitles_original = calculate_time(full_subtitles_seconds_original)
    #print("\n%s Untertitel in Vortragssprache" % (my_subtitles.filter(is_original_lang = True).count()))
    csv_array.append(str("%s" % (my_subtitles.filter(is_original_lang = True).count())))
    #print("%s Sekunden in Vortragssprache" % (full_time_subtitles_original["sum_seconds"]))
    csv_array.append(str("%s" % (full_time_subtitles_original["sum_seconds"])))
    #print("%sh %smin %ssec Talk-Zeit fertige Untertitel in Vortragssprache" % (full_time_subtitles_original["hours"], full_time_subtitles_original["minutes"], full_time_subtitles_original["seconds"]))
    csv_array.append(str("%s:%s:%s" % (full_time_subtitles_original["hours"], full_time_subtitles_original["minutes"], full_time_subtitles_original["seconds"])))
    
    full_subtitles_seconds_not_original = 0
    for any_subt in my_subtitles.filter(is_original_lang = False):
        full_subtitles_seconds_not_original += calculate_seconds_from_time(any_subt.talk.video_duration)
    full_time_subtitles_not_original = calculate_time(full_subtitles_seconds_not_original)
    #print("\n%s Übersetzte Untertitel" %(my_subtitles.filter(is_original_lang = False).count()))
    csv_array.append(str("%s" %(my_subtitles.filter(is_original_lang = False).count())))
    #print("%s Sekunden übersetzte Untertitel" %(full_time_subtitles_not_original["sum_seconds"]))
    csv_array.append(str("%s" %(full_time_subtitles_not_original["sum_seconds"])))
    #print("%sh %smin %ssec Talk-Zeit fertige Untertitelübersetzungen" % (full_time_subtitles_not_original["hours"], full_time_subtitles_not_original["minutes"], full_time_subtitles_not_original["seconds"]))
    csv_array.append(str("%s:%s:%s" % (full_time_subtitles_not_original["hours"], full_time_subtitles_not_original["minutes"], full_time_subtitles_not_original["seconds"])))

    my_subtitles = Subtitle.objects.filter(talk__event = any_event, is_original_lang = True)
    # Prozent / Zeit Transkribiert
    full_time_seconds_subtitles_transcribed = 0
    for any_subt in my_subtitles:
        full_time_seconds_subtitles_transcribed += calculate_seconds_from_time(any_subt.time_processed_transcribing)
    full_time_subtitles_transcribed = calculate_time(full_time_seconds_subtitles_transcribed)
    #print("\n%s Sekunden Transkribiert" % (full_time_subtitles_transcribed["sum_seconds"]))
    csv_array.append("%s" % (full_time_subtitles_transcribed["sum_seconds"]))
    #print("%sh %smin %ssec Zeit fertig transkribiert" % (full_time_subtitles_transcribed["hours"], full_time_subtitles_transcribed["minutes"], full_time_subtitles_transcribed["seconds"]))
    csv_array.append("%s:%s:%s" % (full_time_subtitles_transcribed["hours"], full_time_subtitles_transcribed["minutes"], full_time_subtitles_transcribed["seconds"]))
    if full_seconds != 0:
        #print("%.2f%% Transkribiert" % (full_time_subtitles_transcribed["sum_seconds"]/full_seconds * 100))
        csv_array.append(str("%.2f" % (full_time_subtitles_transcribed["sum_seconds"]/full_seconds * 100)))
    else:
        #print("0.00% Transkribiert")
        csv_array.append("0.00")

    # Prozent / Zeit getimt
    full_time_seconds_subtitles_timed = 0
    for any_subt in my_subtitles:
        full_time_seconds_subtitles_timed += calculate_seconds_from_time(any_subt.time_processed_syncing)
    full_time_subtitles_timed = calculate_time(full_time_seconds_subtitles_timed)
    #print("\n%s Sekunden fertig getimt" % (full_time_subtitles_timed["sum_seconds"]))
    csv_array.append(str("%s" % (full_time_subtitles_timed["sum_seconds"])))
    #print("%sh %smin %ssec Zeit fertig getimt" % (full_time_subtitles_timed["hours"], full_time_subtitles_timed["minutes"], full_time_subtitles_timed["seconds"]))
    csv_array.append(str("%2.0f:%s:%s" % (full_time_subtitles_timed["hours"], full_time_subtitles_timed["minutes"], full_time_subtitles_timed["seconds"])))
    if full_seconds != 0:
        #print("%.2f%% fertig getimt" % (full_time_subtitles_timed["sum_seconds"]/full_seconds * 100))
        csv_array.append(str("%.2f" % (full_time_subtitles_timed["sum_seconds"]/full_seconds * 100)))
        
    else:
        #print("0.00% fertig getimt")
        csv_array.append("0.00")


        # Prozent / Zeit Qualitätskontrolle
    full_time_seconds_quality_control_done = 0
    for any_subt in my_subtitles:
        full_time_seconds_quality_control_done += calculate_seconds_from_time(any_subt.time_quality_check_done)
    full_time_quality_control_done = calculate_time(full_time_seconds_quality_control_done)
    #print("\n%s Sekunden Qualitätskontrolle erledigt" % (full_time_quality_control_done["sum_seconds"]))
    csv_array.append(str("%s" % (full_time_quality_control_done["sum_seconds"])))
    #print("%sh %smin %ssec Zeit Qualitätskontrolle erledigt" % (full_time_quality_control_done["hours"], full_time_quality_control_done["minutes"], full_time_quality_control_done["seconds"]))
    csv_array.append(str("%s:%s:%s" % (full_time_quality_control_done["hours"], full_time_quality_control_done["minutes"], full_time_quality_control_done["seconds"])))
    if full_seconds != 0:
        #print("%.2f%% Qualitätskontrolle erledigt" % (full_time_quality_control_done["sum_seconds"]/full_seconds * 100))
        csv_array.append(str("%.2f" % (full_time_quality_control_done["sum_seconds"]/full_seconds * 100)))
    else:
        #print("0.00% Qualitätskontrolle erledigt")
        csv_array.append("0.00")

    #print(csv_array)
    max = len(csv_array)
    counter = 0
    output_string = ""
    while counter < max:
        if counter != max -1:
            output_string += csv_array[counter]
            output_string += ";"
            #print(csv_array[counter] + ";")
        else:
            #print(csv_array[counter])        
            output_string += csv_array[counter]
        counter += 1
    print(output_string)
    csv_array = []
    #print("\n\n")