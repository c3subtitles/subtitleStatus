#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts does the calculations in the statistics model
# It is meant to be run as cronjob
#
# It calculates the time delta, words and strokes during the entered
# time span and for one speaker only
# 
# Goal is to calculate average wpm for different speaker and different talks
# The average wpm during a talk can be a sum of the different speakers and
# their timeslots added together
# A talk and a speaker can be represented by several lines in the statistics
# table
#==============================================================================

import os
import sys
import urllib
import re
import datetime
import copy

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()

from django.db.models import Q
from www.models import Talk, Language, Subtitle, Statistics

"""
# Create Test-Data new:
test_statistics = Statistics.objects.get(id = 4)
test_statistics.start = "00:01:04.100000"
test_statistics.end = "01:02:37.100555"
test_statistics.time_delta = None
test_statistics.words = None
test_statistics.strokes = None
test_statistics.save()
print("Test-Data set")
print("Alter Start: ")
print(test_statistics.start)
print("Altes Ende: ")
print(test_statistics.end)
"""

# Check which entries in Statistics do not have a timedelta, words or strokes entry
my_statistics = Statistics.objects.filter(Q(time_delta = None) | Q(words = None) | Q(strokes = None))
print(my_statistics.count())
  
# For every non finnished statistics entry:  
for this_st in my_statistics:
  
    # Check if the subtitle is complete an not a translation
    if not this_st.subtitle.complete:
        continue
    if not this_st.subtitle.is_original_lang:
        continue
    # Check if the speaker in Statistics is really a speaker in the talk according to the Fahrplan
    if not this_st.speaker in this_st.subtitle.talk.persons.all():
        continue
        
    # Get the Amara-Key and create the URL
    amara_key = this_st.subtitle.talk.amara_key
    language = this_st.subtitle.language.lang_amara_short
    url = "https://www.amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=sbv"
    print(url)
    
    # sbv-File herunter laden
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    file_content = response.read()
    # Convert from bytes object to string object
    file_content = str(file_content, encoding = "UTF-8")
    
    # Split in single lines:
    text_content = file_content.splitlines()
    # Count lines of the sbv-file
    lines_in_sbv_file = len(text_content)
    #print(lines_in_sbv_file)
    counter = 0
    # Flags to only once set the start time and end time, to avoid moving of
    # the times becauese of subtitles with the same start and end time
    start_is_set = False
    end_is_set = False
    # Save the start and end lines with subtitle-text and use it later
    line_counter_start = 0
    line_counter_end = 0
    # Convert all start and stop times in the sbv file into datetime.time objects
    while (counter < lines_in_sbv_file):
        temp_array = []
        # Split the String into the two seperate timestamps
        temp_array = text_content[counter].split(',')
        temp_array_2 = []
        for any in temp_array:
            # Conversion from Milli- to Microseconds
            any += "000"
            # Conversion to a datetime.time object
            any = datetime.datetime.strptime(any, "%H:%M:%S.%f").time()
            # Append to the second temporary array
            temp_array_2.append(any)
            
        # Change the String in the sbv-file to an array of datetime.time objects
        text_content[counter] = []
        text_content[counter] = copy.deepcopy(temp_array_2)

        # Find the startpoint
        # If the start-timestamp is in a subtitle-line set it to the start of this line
        if not start_is_set and \
            this_st.start >= text_content[counter][0] and \
            this_st.start <= text_content[counter][1]:
            # Dirty workaround substracting/adding one millisecond to avoid "jumping"
            # of the timestamps when the script is executed several times and
            # calculates the times new, this is caused by two subtitles one#
            # having the starttimestamp and one the same timestamp es endtimestamp
            delta = datetime.timedelta(microseconds = 1)            
            this_st.start = (datetime.datetime.combine(datetime.datetime.today(),text_content[counter][0]) + delta).time()
            this_st.save()
            print("Neuer Start: ")
            print(this_st.start)
            # Set the start-counter to the first line with text which is included in the timespan
            line_counter_start = counter + 1
            start_is_set = True
            
        # If the entered start time is in between two subtitles from the sbv File (the one looking at right now and the previous one), than use the following ones start time as start
        if counter >= 3 and \
            not start_is_set and \
            this_st.start > text_content[counter-3][1] and \
            this_st.start < text_content[counter][0]:
            delta = datetime.timedelta(microseconds = 1)            
            this_st.start = (datetime.datetime.combine(datetime.datetime.today(),text_content[counter][0]) + delta).time()
            this_st.save()
            print("Neuer Start: ")
            print(this_st.start)
            line_counter_start = counter + 1
            start_is_set = True
                
        # Find the endoint
        # If the entered end time is in a subtitles from the sbv file use the end of the subtitle as new end
        if not end_is_set and \
            this_st.end >= text_content[counter][0] and \
            this_st.end <= text_content[counter][1]:
            # Use the end of this subtitle
            delta = datetime.timedelta(microseconds = 1)
            this_st.end = (datetime.datetime.combine(datetime.datetime.today(),text_content[counter][1]) - delta).time()
            this_st.end = temp_array_2[1]
            print("Neues Ende: ")
            print(this_st.end)
            this_st.save()
            # Set the end-counter to the last line with text which is included in the timespan
            line_counter_end = counter + 1
            end_is_set = True
            
        # If the entered end time is in between two subtitles from the sbv File (the one looking at right now and the previous one), than use the first ones end time as end
        if counter >= 3 and \
            not end_is_set and \
            this_st.end > text_content[counter - 3][1] and \
            this_st.end < text_content[counter][0]:
            # Use the end of the previous subtitle timestamp
            delta = datetime.timedelta(microseconds = 1)            
            this_st.end = (datetime.datetime.combine(datetime.datetime.today(),text_content[counter-3][1]) - delta).time()
            this_st.save()
            print("Neues Ende: ")
            print(this_st.end)
            # Set the end-counter to the last line with text from the previous subtitle
            line_counter_end = counter -2
            end_is_set = True
        
        # Stop the while loop if start and end have been set
        if start_is_set and end_is_set:
            break
        
        # Jump 3 lines because a sbv-File looks like this:
        """
        0:00:19.350,0:00:25.000
        She will be talking about reasonably[br]trustworthy x86 systems.

        0:00:25.000,0:00:30.150
        She’s the founder and leader[br]of the Invisible Things Lab

        0:00:30.150,0:00:37.149
        and also – that’s also something you all[br]probably use – the Qubes OS project.
        """
        counter += 3
    
    # calculate the time_delta
    this_st.calculate_time_delta()
    
    # Build one big string with all lines, replace "[br]" with " ", double
    # spaces are not relevant
    # Use this big string to count the strokes as its length and the words by splitting it
    counter = line_counter_start
    big_string = ""
    while counter <= line_counter_end:
        big_string += " "
        big_string += text_content[counter]
        counter += 3
    # sbv-Files use "[br]" as break line, this is replaced with spaces
    big_string = re.sub("\[br\]"," ",big_string)
    # The strokes are the length of the string
    this_st.strokes = len(big_string)
    # The words is the length of the array if it is splitted at spaces
    this_st.words = len(big_string.split())
    this_st.save()

    print("Done!")

