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
    global event_end, event_days, timeslot_duration, day_index, day_date
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
my_event = ""
my_room = ""

#===============================================================================
# Read XML and safe to database functions
#===============================================================================

# Main reading/writing function
def read_xml_and_save_to_database():
    global url_to_this_fahrplan
    set_vars_empty(url_to_this_fahrplan)
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date
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
    
    # Event schedule version
    if fahrplan[0].tag == "version":
        schedule_version = fahrplan[0].text
    else:
        error("Problem with schedule_version")

    # Event acronym
    if fahrplan[1][0].tag == "acronym":
        acronym = fahrplan[1][0].text
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
        timeslot_duration = fahrplan[1][5].text
    else:
        error("Problem with timeslot_duration")

    # Write event data to database
    save_event_data()    
        
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
        save_day_data()
        
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
                    track = str(fahrplan[counter_day][counter_room][counter_event][8].text)
                else:
                    error("Problem with track")
                    
                # Write track data to database
                save_track_data()
                
                # type of
                if fahrplan[counter_day][counter_room][counter_event][9].tag == "type":
                    type = str(fahrplan[counter_day][counter_room][counter_event][9].text)
                else:
                    error("Problem with type")
                
                # Write type of data to database
                save_type_of_data()
                
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
                    
                # Write persons data to database
                save_persons_data()

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
    global url_to_this_fahrplan, my_event
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration

    schedule_url = url_to_this_fahrplan
    
    my_event = Event.objects.get(schedule_xml_link = schedule_url)
    #my_event.schedule_version = schedule_version
    my_event.acronym = acronym
    my_event.title = title
    my_event.start = event_start
    my_event.end = event_end
    my_event.days = event_days
    my_event.timeslot_duration = timeslot_duration
    my_event.save()

# Save the data of the days into the database
def save_day_data():
    global my_event
    global day_index, day_date, day_start, day_end
    try:
        my_day = Event_Days.objects.get(index = day_index, event = my_event)
        my_day.day_start = day_start
        my_day.day_end = day_end
        my_day.index = day_index
        my_day.date = day_date
        my_day.save()
    except ObjectDoesNotExist:
        my_day = Event_Days.objects.create(event = my_event, index = day_index,
            date = day_date, day_start = day_start, day_end = day_end)
    
# Save the data of the room into the database
def save_room_data():
    global room, my_room
    my_room = Rooms.objects.get_or_create(room = room)

# Save the data of the speakers into the database
def save_persons_data ():
    global persons, my_persons
    my_persons = []
    my_person = []
    for someone in persons:
        try:
            my_person = Speaker.objects.get(frab_id = someone[0])
            my_person.name = someone[1]
            my_person.save()
        except ObjectDoesNotExist:
            my_person = Speaker.objects.create(frab_id = someone[0], name = someone[1])
    
        # Array to acces all linked speakers for the saving of the talk
        my_persons.append(my_person)
        
# Save the data of the link of a talk into the database
def save_links_data ():
    global links, my_links
    my_links = []
    my_link = []
    
    for any_link in links:
        my_link = Links.objects.get_or_create(url = any_link[0], title = any_link[1])
        
        # Array to acces all links for the saving of the talk
        my_links.append(my_link)

# Save Tracks_of into the database (Beware, Track can be None -> as String)
def save_track_data():
    global track, my_track
    my_track = Tracks.objects.get_or_create(track = track)
        
# Save Type_of into the database
def save_type_of_data():
    global type, my_type
    my_type = Type_of.objects.get_or_create(type = type)

# Save language data into the database
def save_languages_data():
    pass

# Save the data of the event talk into the database
def save_talk_data ():
    global my_event, my_room, my_day
    global talk, talk_frab_id
    pass
    
#===============================================================================
# Main
#===============================================================================

# Get all schedule-urls from the database
my_events = Event.objects.all()
for e in my_events:
    url_array.append(e.schedule_xml_link)

# For every fahrplan file
for url_to_this_fahrplan in url_array:
    response = request.urlopen(url_to_this_fahrplan) 
    tree = etree.parse(response)
    fahrplan = tree.getroot()
    
    # Compare Fahrplanversion in the database and online, break if the same:
    this_event = Event.objects.get(schedule_xml_link = url_to_this_fahrplan)
    if fahrplan[0].text == this_event.schedule_version:
        print("In ",fahrplan[1][1].text," nichts geändert!")
        break
    print("Debug Event:",fahrplan[1][0].text)
    print("Debug: Version in DB: ", this_event.schedule_version,"\n\n")
    
    #Funktion für Fahrplan in Datenbank schubsen
    read_xml_and_save_to_database()

print ("Durch gelaufen, Error Code: ", error_code)
print ("Fehler: ",error_string)
