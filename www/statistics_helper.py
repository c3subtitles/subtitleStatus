#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# statistics_helper.py
# This file includes helper functions to create all the statistic values
# It is mainly used in models.py 
#
# Functions included:
# calculate_seconds_from_time(time)
# calculate_time_delta(start, end)
# calculate_per_minute(number, time_delta_seconds)
# calculate_subtitle(amara_key, lang_amara_short, start = None, end = None)
#==============================================================================

import urllib
import re
from datetime import datetime
import copy

    
# Calculate seconds from time element of a models
def calculate_seconds_from_time(time):
    return time.hour * 3600 + time.minute * 60 + time.second + time.microsecond/1000000.0

# Function to calculate the delta time of a start and end time
def calculate_time_delta(start, end):
    end_in_seconds = calculate_seconds_from_time(end)
    start_in_seconds = calculate_seconds_from_time(start)
    return end_in_seconds - start_in_seconds
   
# Calculate average wpm or spm   
def calculate_per_minute(number, time_delta_seconds):
    return number * 60.0 / time_delta_seconds

# Functions calculates the words and strokes of a whole subtitle file or a slice of items
# The language code must be the amara version
# It returns a dictionary with words and strokes and - in the case of a slice
# - also the real time_delta
def calculate_subtitle(talk, start = None, end = None):
    from .models import Subtitle
    this_subtitle = Subtitle.objects.filter(talk = talk, is_original_lang = True)
    # Stop if there are more than one orignal language subtitles
    if this_subtitle.count() != 1:
        return None
    
    # Get the Amara-Key and create the URL
    amara_key = talk.amara_key
    language = this_subtitle[0].language.lang_amara_short
    url = "https://www.amara.org/api2/partners/videos/"+amara_key+"/languages/"+language+"/subtitles/?format=sbv"
    print(url)
    
    # Download sbv-File
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
    
    # Calculate the whole file not only a slice
    if start is None or end is None:
        counter = 1
        big_string = ""
        while counter <= lines_in_sbv_file:
            big_string += " "
            big_string += text_content[counter]
            counter += 3
        
        # sbv-Files use "[br]" as break line, this is replaced with spaces
        big_string = re.sub("\[br\]"," ",big_string)
        # The strokes are the length of the string
        strokes = len(big_string)
        # The words is the length of the array if it is splitted at spaces
        words = len(big_string.split())
        time_delta = calculate_seconds_from_time(talk.video_duration)
        return_dict = {}
        return_dict["words"] = words
        return_dict["strokes"] = strokes
        return_dict["average_wpm"] = calculate_per_minute(words, time_delta)
        return_dict["average_spm"] = calculate_per_minute(strokes, time_delta)
        return_dict["time_delta"] = time_delta
        return return_dict
        
    # Else calculate the slice defined by start and end
    else:
        counter = 0
        # Flags to only once set the start time and end time, to avoid moving of
        # the times becauese of subtitles with the same start and end time
        start_is_set = False
        end_is_set = False
        # Save the start and end lines with subtitle-text and use it later
        line_counter_start = 0
        line_counter_end = 0
        start_time = 0
        end_time = 0
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
                any = datetime.strptime(any, "%H:%M:%S.%f").time()
                # Append to the second temporary array
                temp_array_2.append(any)
                
            # Change the String in the sbv-file to an array of datetime.time objects
            text_content[counter] = []
            text_content[counter] = copy.deepcopy(temp_array_2)

            # Find the startpoint
            # If the start-timestamp is in a subtitle-line set it to the start of this line
            if not start_is_set and \
                start >= text_content[counter][0] and \
                start <= text_content[counter][1]:
                # Dirty workaround substracting/adding one millisecond to avoid "jumping"
                # of the timestamps when the script is executed several times and
                # calculates the times new, this is caused by two subtitles one#
                # having the starttimestamp and one the same timestamp es endtimestamp
                start_time = text_content[counter][0]
                
                print("Neuer Start: ")
                print(start_time)
                # Set the start-counter to the first line with text which is included in the timespan
                line_counter_start = counter + 1
                start_is_set = True
                
            # If the entered start time is in between two subtitles from the sbv File (the one looking at right now and the previous one), than use the following ones start time as start
            if counter >= 3 and \
                not start_is_set and \
                start > text_content[counter-3][1] and \
                start < text_content[counter][0]:
                start_time = text_content[counter][0]
                print("Neuer Start: ")
                print(start_time)
                line_counter_start = counter + 1
                start_is_set = True
            # If start ist not yet set but before the first subtitle
            if counter < 3 and \
                not start_is_set and \
                start < text_content[counter][0]:
                start_time = text_content[counter][0]
                print("Neuer Start: ")
                print(start_time)
                line_counter_start = counter +1
                start_is_set = True
                    
            # Find the endoint
            # If the entered end time is in a subtitles from the sbv file use the end of the subtitle as new end
            if not end_is_set and \
                end >= text_content[counter][0] and \
                end <= text_content[counter][1]:
                # Use the end of this subtitle
                end_time = text_content[counter][1]
                print("Neues Ende: ")
                print(end_time)
                # Set the end-counter to the last line with text which is included in the timespan
                line_counter_end = counter + 1
                end_is_set = True
                
            # If the entered end time is in between two subtitles from the sbv File (the one looking at right now and the previous one), than use the first ones end time as end
            if counter >= 3 and \
                not end_is_set and \
                end > text_content[counter - 3][1] and \
                end < text_content[counter][0]:
                # Use the end of the previous subtitle timestamp
                end_time = text_content[counter-3][1]
                print("Neues Ende: ")
                print(end_time)
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
        # If the end timestamp is after the last subtitle, use the last subtitles end as end
        if not end_is_set:
            end_time = text_content[lines_in_sbv_file-2][1]    
        
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
        strokes = len(big_string)
        # The words is the length of the array if it is splitted at spaces
        words = len(big_string.split())
        time_delta = calculate_time_delta(start_time, end_time)
        return_dict = {}
        return_dict["words"] = words
        return_dict["strokes"] = strokes
        return_dict["time_delta"] = time_delta
        return return_dict

