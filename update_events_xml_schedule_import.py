#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script checks every event with an url to the farhrplan in the database
# for updates depending on the version of the fahrplan
# If the Fahrplanversion has changed everything is checked for updates
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
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start, talk_duration
    global talk_slug, talk_optout, talk_title, talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person, my_persons, my_type, my_language
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
    talk_room = ""
    talk_frab_id = -1
    talk_date = ""
    talk_start = ""
    talk_duration = ""
    talk_slug = ""
    talk_optout = False
    talk_title = ""
    talk_subtitle = ""
    talk_track = ""
    talk_type = ""
    talk_language = ""
    talk_abstract = ""
    talk_description = ""
    talk_persons = []
    talk_links = []
    my_event = ""
    my_room = ""
    my_day = ""
    my_track = ""
    my_events = ""
    my_link = ""
    my_links = ""
    my_person = ""
    my_persons = ""
    my_type = ""
    my_language = ""

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
talk_room = ""
talk_frab_id = -1
talk_date = ""
talk_start = ""
talk_duration = ""
talk_slug  = ""
talk_optout = False
talk_title = ""
talk_subtitle = ""
talk_track = ""
talk_type = ""
talk_language = ""
talk_abstract = ""
talk_description = ""
talk_persons = []
talk_links = []
my_event = ""
my_room = ""
my_day = ""
my_track = ""
my_events = ""
my_link = ""
my_links = ""
my_person = ""
my_persons = ""
my_type = ""
my_language = ""

#===============================================================================
# Read XML and save to database functions
#===============================================================================

# Main reading/writing function
def read_xml_and_save_to_database():
    global url_to_this_fahrplan
    set_vars_empty(url_to_this_fahrplan)
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start, talk_duration
    global talk_slug, talk_optout, talk_title, talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links
    global fahrplan, len_day, len_event, len_room
    global counter_event, counter_event, counter_room
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person, my_persons, my_type

    len_day = len(fahrplan)
    counter_day = 2

    # Event title
    if fahrplan[1][1].tag == "title":
        event_title = fahrplan[1][1].text
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
                talk_room = fahrplan[counter_day][counter_room].get("name")
            else:
                error("Problem with room data")
            
            # Write room data to database
            save_room_data()
            
            # Prepare for event-loop
            len_event = len(fahrplan[counter_day][counter_room])
            counter_event = 0
        
            # Loop around the event tags (talks)
            while (counter_event < len_event):
                # Read event/talk data
                # talk_frab_id
                if fahrplan[counter_day][counter_room][counter_event].tag == "event":
                    talk_frab_id = int(fahrplan[counter_day][counter_room][counter_event].get("id"))
                else:
                    error("Problem with talk_frab_id")
                
                # talk/event_date
                if fahrplan[counter_day][counter_room][counter_event][0].tag == "date":
                    talk_date = fahrplan[counter_day][counter_room][counter_event][0].text
                else:
                    error("Problem with event_date")
                
                # talk/event_start
                if fahrplan[counter_day][counter_room][counter_event][1].tag == "start":
                    talk_start = fahrplan[counter_day][counter_room][counter_event][1].text
                else:
                    error("Problem with event_start")
                
                # duration
                if fahrplan[counter_day][counter_room][counter_event][2].tag == "duration":
                    talk_duration = fahrplan[counter_day][counter_room][counter_event][2].text
                else:
                    error("Problem with duration")
                
                # slug
                if fahrplan[counter_day][counter_room][counter_event][4].tag == "slug":
                    talk_slug = fahrplan[counter_day][counter_room][counter_event][4].text
                else:
                    error("Problem with slug")
                
                # recording optout, no bool-var!
                if fahrplan[counter_day][counter_room][counter_event][5].tag == "recording":
                    talk_optout = fahrplan[counter_day][counter_room][counter_event][5][1].text
                else:
                    error("Problem with optout")
                
                # talk/event_title
                if fahrplan[counter_day][counter_room][counter_event][6].tag == "title":
                    talk_title = fahrplan[counter_day][counter_room][counter_event][6].text
                else:
                    error("Problem with event_title")
                
                # subtitle
                if fahrplan[counter_day][counter_room][counter_event][7].tag == "subtitle":
                    talk_subtitle = str(fahrplan[counter_day][counter_room][counter_event][7].text)
                else:
                    error("Problem with subtitle")
                
                # track
                if fahrplan[counter_day][counter_room][counter_event][8].tag == "track":
                    talk_track = str(fahrplan[counter_day][counter_room][counter_event][8].text)
                else:
                    error("Problem with track")
                    
                # Write track data to database
                save_track_data()
                
                # type of talk
                if fahrplan[counter_day][counter_room][counter_event][9].tag == "type":
                    talk_type = str(fahrplan[counter_day][counter_room][counter_event][9].text)
                else:
                    error("Problem with type")
                
                # Write type of data to database
                save_type_of_data()
                
                # language
                if fahrplan[counter_day][counter_room][counter_event][10].tag == "language":
                    talk_language = str(fahrplan[counter_day][counter_room][counter_event][10].text)
                else:
                    error("Problem with language")
                my_language = Language.objects.get(lang_amara_short = talk_language)
                
                # abstract
                if fahrplan[counter_day][counter_room][counter_event][11].tag == "abstract":
                    talk_abstract = str(fahrplan[counter_day][counter_room][counter_event][11].text)
                else:
                    error("Problem with abstract")
                
                # description
                if fahrplan[counter_day][counter_room][counter_event][12].tag == "description":
                    talk_description = str(fahrplan[counter_day][counter_room][counter_event][12].text)
                else:
                    error("Problem with description")
                
                # persons
                talk_persons = []
                if fahrplan[counter_day][counter_room][counter_event][13].tag == "persons":
                    # check if there is any subelement in persons
                    if len(fahrplan[counter_day][counter_room][counter_event][13]):
                        for person in fahrplan[counter_day][counter_room][counter_event][13]:
                            talk_persons.append([int(person.get("id")), person.text])
                    else:
                        talk_persons = []
                else:
                    error("Problem with persons")
                    
                # Write persons data to database
                save_persons_data()

                # links
                talk_links = []
                if fahrplan[counter_day][counter_room][counter_event][14].tag == "links":
                    if len(fahrplan[counter_day][counter_room][counter_event][14]):
                        for l in fahrplan[counter_day][counter_room][counter_event][14]:
                            talk_links.append([l.get("href"), l.text])
                    else:
                        talk_links = []
                else:
                    error("Problem with links")
                
                 
                # Write event/talk data to database
                save_talk_data()
                
                
                
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
    my_event.schedule_version = schedule_version
    my_event.acronym = acronym
    my_event.title = event_title
    my_event.start = event_start
    my_event.end = event_end
    my_event.days = event_days
    my_event.timeslot_duration = timeslot_duration
    my_event.save()

# Save the data of the days into the database
def save_day_data():
    global my_event, my_day
    global day_index, day_date, day_start, day_end
    my_day = Event_Days.objects.get_or_create(event = my_event, index = day_index)[0]
    
    my_day.day_start = day_start
    my_day.day_end = day_end
    my_day.date = day_date
    my_day.save()
    
# Save the data of the room into the database
def save_room_data():
    global talk_room, my_room
    my_room = Rooms.objects.get_or_create(room = talk_room)
    my_room = Rooms.objects.get(room = talk_room)

# Save the data of the speakers into the database
def save_persons_data ():
    global talk_persons, my_persons
    my_persons = []
    my_person = []
    for someone in talk_persons:
        my_person = Speaker.objects.get_or_create(frab_id = someone[0])[0]
        my_person.name = someone[1]
        my_person.save()
    
        # Array to acces all linked speakers for the saving of the talk
        my_persons.append(my_person)
              
# Save Tracks_of into the database (Beware, Track can be None -> as String)
def save_track_data():
    global talk_track, my_track
    my_track = Tracks.objects.get_or_create(track = talk_track)[0]
    
# Save Type_of into the database
def save_type_of_data():
    global talk_type, my_type
    my_type = Type_of.objects.get_or_create(type = talk_type)[0]

# Save language data into the database, not necessary!
def save_languages_data():
    pass

# Save the data of the event talk into the database
def save_talk_data ():
    global schedule_url, schedule_version, acronym, event_title, event_start
    global event_end, event_days, timeslot_duration, day_index, day_date
    global day_start, day_end, talk_room, talk, talk_frab_id, talk_date, talk_start, talk_duration
    global talk_slug, talk_optout, talk_title, talk_subtitle, talk_track, talk_type, talk_language, talk_abstract
    global talk_description, talk_persons, talk_links
    global my_event, my_room, my_day, my_track, my_events, my_link, my_links, my_person, my_persons, my_type, my_language
    
    my_language = Language.objects.get(lang_amara_short = talk_language)
    my_talk = []
    
    my_talk = Talk.objects.get_or_create(frab_id_talk = talk_frab_id)[0]
    my_talk.room = my_room
    my_talk.track = my_track
    my_talk.type_of = my_type
    my_talk.orig_language = my_language
    my_talk.date = talk_date
    my_talk.start = talk_start
    my_talk.duration = talk_duration
    my_talk.slug = talk_slug
    my_talk.title = talk_title
    my_talk.subtitle_talk = talk_subtitle
    my_talk.abstract = talk_abstract
    my_talk.description = talk_description
    if (talk_optout=="true"):
        my_talk.blacklisted = True
    
    my_talk.day = my_day
    my_talk.event = my_event
    
    my_talk.save()
    
    # Prepare to save links
    my_links = []
    my_link = []
    # Saving the links
    for some_link in talk_links:
        my_link = Links.objects.get_or_create(url = some_link[0], title = some_link[1], talk = my_talk)
    
    for any_person in my_persons:
        my_talk.persons.add(any_person)
        
    
    
#===============================================================================
# Main
#===============================================================================

# Get all schedule-urls from the database
my_events = Event.objects.all()
for e in my_events:
    fahrplan_link = e.schedule_xml_link
    # Only if the fahrplan field is not empty
    if fahrplan_link != "":
        url_array.append(fahrplan_link)

# For every fahrplan file
for url_to_this_fahrplan in url_array:
    response = request.urlopen(url_to_this_fahrplan) 
    tree = etree.parse(response)
    fahrplan = tree.getroot()
    
    # Compare Fahrplanversion in the database and online, break if the same:
    this_event = Event.objects.get(schedule_xml_link = url_to_this_fahrplan)
    if fahrplan[0].text == this_event.schedule_version:
        print("In ",fahrplan[1][1].text," nichts geändert! Version ist: ",fahrplan[0].text)
        continue
    else:
        print("In ",fahrplan[1][1].text," etwas geändert!\nVon Version: \"",this_event.schedule_version,"\" to \"",fahrplan[0].text,"\"")
    #print("Debug Event:",fahrplan[1][0].text)
    #print("Debug: Version in DB: ", this_event.schedule_version,"\n\n")
    
    #Funktion für Fahrplan in Datenbank schubsen
    read_xml_and_save_to_database()

print ("Durch gelaufen, Error Code: ", error_code)
print ("Fehler: ",error_string)

