#!/usr/bin/python3
# -*- coding: utf-8 -*-

#import os
#import sys
from lxml import etree

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

#from django.core.management.base import BaseCommand, CommandError
#from django.db import transaction

#import www.models as models

# Code um Array mit allen XML-URLS aus dem Fahrplan zu bauen============

url_array = []

# Workaround ohne Links in Datenbank
file = "30c3_schedule.xml"
tree = etree.parse(file)
fahrplan = tree.getroot()

# Array-Length depending on depth
len_day = 0
len_room = 0
len_event = 0

# Counter for every level in depth
counter_day = 0
counter_room = 0
counter_event = 0

# Error-Counter
error_code = 0

# Reset everything =============================================================
def set_vars_empty():
    global schedule_url
    schedule_url = ""
    global schedule_version
    schedule_version = ""
    global acronym
    acronym = ""
    global event_title
    event_title = ""
    global event_start
    event_start = ""
    global event_end
    event_end = ""
    global event_days
    event_days = ""
    global timeslot_duration
    timeslot_duration = ""
    global day_index
    day_index = ""
    global day_date
    day_date = ""
    global day_start
    day_start = ""
    global day_end
    day_end = ""
    global room
    room = ""
    global talk
    talk =  ""
    global talk_frab_id
    talk_frab_id = -1
    global date
    date = ""
    global start
    start = ""
    global duration
    duration = ""
    global slug
    slug = ""
    global optout
    optout = False
    global title
    title = ""
    global subtitle
    subtitle = ""
    global track
    track = ""
    global type
    type = ""
    global language
    language = ""
    global abstract
    abstract = ""
    global description
    description = ""
    global persons
    persons = []
    global links
    links = []

# Function to save a talk with all corresponding information ===================
def save_talk_to_database():
    pass
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
# Main
#===============================================================================

# Fahrplanversion
if fahrplan[0].tag == "version":
    version = fahrplan[0].text
else:
    error_code += 1

# Code um Fahrplanversion mit der in der Datenbank zu vergleichen und abzubrechen

len_day = len(fahrplan)
counter_day = 2

# Event title
if fahrplan[1][1].tag == "title":
    title = fahrplan[1][1].text
else:
    error_code += 1

# Event acronym
if fahrplan[1][0].tag == "acronym":
    event_title = fahrplan[1][0].text
else:
    error_code += 1

# Event start
if fahrplan[1][2].tag == "start":
    event_start = fahrplan[1][2].text
else:
    error_code += 1

# Event end
if fahrplan[1][3].tag == "end":
    event_end = fahrplan[1][3].text
else:
    error_code += 1
    
# Event days
if fahrplan[1][4].tag == "days":
    event_days = int(fahrplan[1][4].text)
else:
    error_code += 1

# Event timeslot_duration
if fahrplan[1][5].tag == "timeslot_duration":
    event_days = fahrplan[1][5].text
else:
    error_code += 1

# Loop around the day tags
while (counter_day < len_day):
    # Read day data
    if fahrplan[counter_day].tag == "day":
        day_index = fahrplan[counter_day].get("index")
        day_date =  fahrplan[counter_day].get("date")
        day_start =  fahrplan[counter_day].get("start")
        day_end =  fahrplan[counter_day].get("end")
    else:
        error_code += 1
    
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
            error_code += 1    
        
        # Write room data to database
        
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
                error_code += 1
            
            # event_date
            if fahrplan[counter_day][counter_room][counter_event][0].tag == "date":
                event_date = fahrplan[counter_day][counter_room][counter_event][0].text
            else:
                error_code += 1
            
            # event_start
            if fahrplan[counter_day][counter_room][counter_event][1].tag == "start":
                event_start = fahrplan[counter_day][counter_room][counter_event][1].text
            else:
                error_code += 1
            
            # duration
            if fahrplan[counter_day][counter_room][counter_event][2].tag == "duration":
                duration = fahrplan[counter_day][counter_room][counter_event][2].text
            else:
                error_code += 1
            
            # slug
            if fahrplan[counter_day][counter_room][counter_event][4].tag == "slug":
                slug = fahrplan[counter_day][counter_room][counter_event][4].text
            else:
                error_code += 1
            
            # recording optout
            if fahrplan[counter_day][counter_room][counter_event][5].tag == "recording":
                optout = bool(fahrplan[counter_day][counter_room][counter_event][5][1].text)
            else:
                error_code += 1
            
            # event_title
            if fahrplan[counter_day][counter_room][counter_event][6].tag == "title":
                event_title = fahrplan[counter_day][counter_room][counter_event][6].text
            else:
                error_code += 1
            
            # subtitle
            if fahrplan[counter_day][counter_room][counter_event][7].tag == "subtitle":
                subtitle = fahrplan[counter_day][counter_room][counter_event][7].text
            else:
                error_code += 1
            
            # track
            if fahrplan[counter_day][counter_room][counter_event][8].tag == "track":
                track = fahrplan[counter_day][counter_room][counter_event][8].text
            else:
                error_code += 1
            
            # type
            if fahrplan[counter_day][counter_room][counter_event][9].tag == "type":
                type = fahrplan[counter_day][counter_room][counter_event][9].text
            else:
                error_code += 1
            
            # language
            if fahrplan[counter_day][counter_room][counter_event][10].tag == "language":
                language_date = fahrplan[counter_day][counter_room][counter_event][10].text
            else:
                error_code += 1
                
            # abstract
            if fahrplan[counter_day][counter_room][counter_event][11].tag == "abstract":
                abstract = fahrplan[counter_day][counter_room][counter_event][11].text
            else:
                error_code += 1
            
            # description
            if fahrplan[counter_day][counter_room][counter_event][12].tag == "description":
                description = fahrplan[counter_day][counter_room][counter_event][12].text
            else:
                error_code += 1
            
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
                error_code += 1
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
                error_code += 1
            #print(len(links), links)
            
            # Write event/talk data to database
            
            counter_event += 1
        counter_room +=1
    counter_day += 1


print ("Durch gelaufen, Error Code: ", error_code)
