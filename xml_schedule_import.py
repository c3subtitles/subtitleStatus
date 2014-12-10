#!/usr/bin/python3
# -*- coding: utf-8 -*-

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

from www.models import Talk, Links, Tracks, Type_of, Speaker, Event, Event_Days, Rooms, Language, Subtitle, States


# Var for all urls in the database in the Event-model
url_array = []

# Array-Length depending on depth
len_day = 0
len_room = 0
len_event = 0

# Counter for every level in depth
counter_day = 0
counter_room = 0
counter_event = 0

# Error-Counter und String
error_code = 0
error_string = []

# Error Function
def error(message=""):
    global error_code, error_string
    error_code +=1
    error_string += message

# Reset everything =============================================================
def set_vars_empty(url = ""):
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_curation, day_index, day_date
    global day_start, day_end, room, talk, talk_frab_id, date, start, duration
    global slug, optout, title, subtitle, track, type, language, abstract
    global description, persons, links
    schedule_url = url
    schedule_version = ""
    acronym = ""
    event_title = ""
    event_start = ""
    event_end = ""
    event_days = ""
    timeslot_duration = ""
    day_index = ""
    day_date = ""
    day_start = ""
    day_end = ""
    room = ""
    talk =  ""
    talk_frab_id = -1
    date = ""
    start = ""
    duration = ""
    slug = ""
    optout = False
    title = ""
    subtitle = ""
    track = ""
    type = ""
    language = ""
    abstract = ""
    description = ""
    persons = []
    links = []

# Vars for temporary saving ====================================================
schedule_version = ""
acronym = ""
event_title = ""
event_start = ""
event_end = ""
event_days = ""
timeslot_duration = ""
day_index = ""
day_date = ""
day_start = ""
day_end = ""
room = ""
talk = ""
talk_frab_id = -1
date = ""
start = ""
duration = ""
slug  = ""
optout = False
title = ""
subtitle = ""
track = ""
type = ""
language = ""
abstract = ""
description = ""
persons = []
links = []

#===============================================================================
# Read XML and safe to database functions
#===============================================================================

# Main reading/writing function
def read_xml_and_save_to_database():
    set_vars_empty(url_this_fahrplan)
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_curation, day_index, day_date
    global day_start, day_end, room, talk, talk_frab_id, date, start, duration
    global slug, optout, title, subtitle, track, type, language, abstract
    global description, persons, links
    global fahrplan, len_day, len_event, len_room
    global counter_event, counter_event, counter_room

    len_day = len(fahrplan)
    counter_day = 2

    # Event title
    if fahrplan[1][1].tag == "title":
        title = fahrplan[1][1].text
    else:
        error("Problem with title")

    # Event acronym
    if fahrplan[1][0].tag == "acronym":
        event_title = fahrplan[1][0].text
    else:
        error("Problem with acronym")

    # Event start
    if fahrplan[1][2].tag == "start":
        event_start = fahrplan[1][2].text
    else:
        error("Problem with event start")

    # Event end
    if fahrplan[1][3].tag == "end":
        event_end = fahrplan[1][3].text
    else:
        error("Problem with event end")
        
    # Event days
    if fahrplan[1][4].tag == "days":
        event_days = int(fahrplan[1][4].text)
    else:
        error("Problem with event days")

    # Event timeslot_duration
    if fahrplan[1][5].tag == "timeslot_duration":
        event_days = fahrplan[1][5].text
    else:
        error("Problem with timeslot_duration")

    # Loop around the day tags
    while (counter_day < len_day):
        # Read day data
        if fahrplan[counter_day].tag == "day":
            day_index = fahrplan[counter_day].get("index")
            day_date =  fahrplan[counter_day].get("date")
            day_start =  fahrplan[counter_day].get("start")
            day_end =  fahrplan[counter_day].get("end")
        else:
            error("Problem with day data")
        
        # Write day data to database    
        
        # Prepare for room-loop
        len_room = len(fahrplan[counter_day])
        counter_room = 0
        
        # Loop around the room tags
        while (counter_room < len_room):
            # Read rooom data
            if fahrplan[counter_day][counter_room].tag == "room":
                room = fahrplan[counter_day][counter_room].get("name")
            else:
                error("Problem with room data")
            
            # Write room data to database
            save_room_data()
            
            # Prepare for event-loop
            len_event = len(fahrplan[counter_day][counter_room])
            counter_event = 0
        
            # Loop around the event tags
            while (counter_event < len_event):
                # Read event/talk data
                # talk_frab_id
                if fahrplan[counter_day][counter_room][counter_event].tag == "event":
                    talk_frab_id = int(fahrplan[counter_day][counter_room][counter_event].get("id"))
                else:
                    error("Problem with talk_frab_id")
                
                # event_date
                if fahrplan[counter_day][counter_room][counter_event][0].tag == "date":
                    event_date = fahrplan[counter_day][counter_room][counter_event][0].text
                else:
                    error("Problem with event_date")
                
                # event_start
                if fahrplan[counter_day][counter_room][counter_event][1].tag == "start":
                    event_start = fahrplan[counter_day][counter_room][counter_event][1].text
                else:
                    error("Problem with event_start")
                
                # duration
                if fahrplan[counter_day][counter_room][counter_event][2].tag == "duration":
                    duration = fahrplan[counter_day][counter_room][counter_event][2].text
                else:
                    error("Problem with duration")
                
                # slug
                if fahrplan[counter_day][counter_room][counter_event][4].tag == "slug":
                    slug = fahrplan[counter_day][counter_room][counter_event][4].text
                else:
                    error("Problem with slug")
                
                # recording optout
                if fahrplan[counter_day][counter_room][counter_event][5].tag == "recording":
                    optout = bool(fahrplan[counter_day][counter_room][counter_event][5][1].text)
                else:
                    error("Problem with optout")
                
                # event_title
                if fahrplan[counter_day][counter_room][counter_event][6].tag == "title":
                    event_title = fahrplan[counter_day][counter_room][counter_event][6].text
                else:
                    error("Problem with event_title")
                
                # subtitle
                if fahrplan[counter_day][counter_room][counter_event][7].tag == "subtitle":
                    subtitle = fahrplan[counter_day][counter_room][counter_event][7].text
                else:
                    error("Problem with subtitle")
                
                # track
                if fahrplan[counter_day][counter_room][counter_event][8].tag == "track":
                    track = fahrplan[counter_day][counter_room][counter_event][8].text
                else:
                    error("Problem with track")
                
                # type
                if fahrplan[counter_day][counter_room][counter_event][9].tag == "type":
                    type = fahrplan[counter_day][counter_room][counter_event][9].text
                else:
                    error("Problem with type")
                
                # language
                if fahrplan[counter_day][counter_room][counter_event][10].tag == "language":
                    language_date = fahrplan[counter_day][counter_room][counter_event][10].text
                else:
                    error("Problem with language")
                    
                # abstract
                if fahrplan[counter_day][counter_room][counter_event][11].tag == "abstract":
                    abstract = fahrplan[counter_day][counter_room][counter_event][11].text
                else:
                    error("Problem with abstract")
                
                # description
                if fahrplan[counter_day][counter_room][counter_event][12].tag == "description":
                    description = fahrplan[counter_day][counter_room][counter_event][12].text
                else:
                    error("Problem with description")
                
                # persons
                persons = []
                if fahrplan[counter_day][counter_room][counter_event][13].tag == "persons":
                    # check if there is any subelement in persons
                    if len(fahrplan[counter_day][counter_room][counter_event][13]):
                        for person in fahrplan[counter_day][counter_room][counter_event][13]:
                            persons.append([int(person.get("id")), person.text])
                    else:
                        persons = []
                else:
                    error("Problem with persons")
                #print(persons)

                # links
                links = []
                if fahrplan[counter_day][counter_room][counter_event][14].tag == "links":
                    if len(fahrplan[counter_day][counter_room][counter_event][14]):
                        for l in fahrplan[counter_day][counter_room][counter_event][14]:
                            links.append([l.get("href"), l.text])
                    else:
                        links = []
                else:
                    error("Problem with links")
                
                # Write event/talk data to database
                
                counter_event += 1
            counter_room +=1
        counter_day += 1

# Save the data of the event into the database
def save_event_data():
    pass

# Save the data of the event-day into the databas
def save_event_day_data():
    pass

# Save the data of the event into the database
def save_day_data():
    pass

# Save the data of the room into the database
def save_room_data():
    global room
    my_room = Rooms.objects.get_or_create(room = room)
    #my_room.objects.save()

# Save the data of the event talk into the database
def save_talk_data ():
    pass
    
    
#===============================================================================
# Main
#===============================================================================

# Get all schedule-urls from the database
my_events = Event.objects.all()
for e in my_events:
    url_array.append(e.schedule_xml_link)

# For every fahrplan file
for url_this_fahrplan in url_array:
    response = request.urlopen(url_this_fahrplan) 
    tree = etree.parse(response)
    fahrplan = tree.getroot()
    
    # Compare Fahrplanversion in the database and online, break if the same:
    this_event = Event.objects.get(schedule_xml_link = url_this_fahrplan)
    if fahrplan[0].text == this_event.schedule_version:
        break
    print("Debug Event:",fahrplan[1][0].text)
    print("Debug: Version in DB: ", this_event.schedule_version,"\n\n")
    
    #Funktion für Fahrplan in Datenbank schubsen
    read_xml_and_save_to_database()

print ("Durch gelaufen, Error Code: ", error_code)
print ("Fehler: ",error_string)
