#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# File: .../fix_sbv_linebreaks.py
#
# This File fixes the Youtube Fuckup when youtube syncs an sbv-File and breaks
# the lines where it shouldn't.
#
# You will need the Transcript File and the sbv File
#==============================================================================


import os
import sys
import SBV_Line

def trim(input):
    while input[:1] == " ":
        input = input[1:]
    while input[-1:] == " ":
        input = input[:-1]
    return input

# Check if enough arguments are given on the command line
if len(sys.argv) < 3:
    sys.exit("Two files needed as input! Try again.")
transcript_file = sys.argv[1]
sbv_file = sys.argv[2]

# Check if the sbv-filename fits
if sbv_file[-4:] == ".sbv":
    pass
else:
    sys.exit("The second file has to be the *.sbv file. Try again.")

# Check the Transcript File and read it in an array
try:
    transcript_stream = open(transcript_file, "r")
    transcript_content = transcript_stream.readlines()
    #print(transcript_content)
    transcript = []
    # Add empty line to find the startpoint better later
    transcript.append("")
    #print(transcript)
    # Lines without newline character for comparison reasons
    for any_line in transcript_content:
        transcript.append(any_line[:-1])
    #print(transcript)
    # Force String Array to have an empty line at the end
    if transcript[-1] != "":
        transcript.append("")
    #print(transcript)
except:
    sys.exit("Transkript File is not readable or does not exist.")

# Check the sbv file and read it into an text array
try:
    sbv_stream = open(sbv_file, "r")
    sbv_content = sbv_stream.readlines()
    #print(sbv_content)
    sbv = []
    # Add empty line to find the startpoint better later
    sbv.append("")
    # Lines without newline character for comparision reasons
    for any_line in sbv_content:
        sbv.append(any_line[:-1])
    #print(sbv)
    # Force String Array to have an empty line at the beginning and end
    if sbv[-1] != "":
        sbv.append("")
    #print(sbv)


    # Zeiger auf leere Zeile setzen
    # Wenn die Zeile die letze im File ist, aufhören
    # Wenn die nächste Zeile auch leer ist counter auf sie setzen
    # Wenn die Zeile nicht leer ist, also Timestamps interpretieren
    # Wenn die nächste Zeile nicht leer ist als line1 interpretieren
    # Wenn die nächste Zeile nicht leer ist als line2 interpretieren
    # Sonst counter darauf setzen und das sbv_element in den sbv_array schreiben
except:
    sys.exit("SBV File is not readable or does not exist.")

# Convert sbv input into SBV_Line class elements
sbv_input = []
counter = 0
while counter < len(sbv):
    # Search for an empty line which is not followed by another empty line
    if sbv[counter] == "":
        counter += 1
        continue
    new_sbv_element = SBV_Line.SBV_Line(timestamp_line = sbv[counter], \
        line_1 = sbv[counter + 1], line_2 = sbv[counter + 2])
    sbv_input.append(new_sbv_element)
    if sbv[counter + 2] == "":
        counter += 2
    else:
        counter += 3

print("=========================================")
print("sbv_input as SBV_Lines",len(sbv_input),"\n")
for any in sbv_input:
    print(any)

# Read transcript also in SBV_Line class elements
transcript_input = []
counter_t = 1
while counter_t < len(transcript):
    if transcript[counter_t] != "":
        counter_t += 1
        continue
    # if it is a double line subtitle line
    elif transcript[counter_t-1] != "" and transcript[counter_t-2] != "":
        new_sbv_element = SBV_Line.SBV_Line(line_1 = transcript[counter_t-2], line_2 = transcript[counter_t-1])
        counter_t += 1
        transcript_input.append(new_sbv_element)
    # if it is a single line subtitle line
    elif transcript[counter_t-1] != "" and transcript[counter_t -2] == "":
        new_sbv_element = SBV_Line.SBV_Line(line_1 = transcript[counter_t-1], line_2 = "")
        counter_t += 1
        transcript_input.append(new_sbv_element)

print("=========================================")
print("Transcript as sbv_lines, Elemente: ", len(transcript_input), "\n")

for jedes in transcript_input:
    print(jedes)


print("=========================================")
print("=========================================")

result = []
counter_t = 0
counter_sbv = 0


for any_line in transcript_input:
    # Build new result element with the 
    result.append(sbv_input[counter_sbv])
    counter_sbv += 1
    print(result[-1])
    counter_sbv += 1
    while result[-1].line_1 != transcript_input[counter_t].line_1:
        result[-1] = SBV_Line.merge_sbv_lines(result[-1], sbv_input[counter_sbv])
        counter_sbv += 1


    counter_t += 1


"""
# "Walk" over the transcript and build the result until it fits
while counter_t < len(transcript_input):
    result.append(sbv_input[counter_sbv])
    print("result counter_t", "\""+result[counter_t].line_1+"\"")
    print("transcript_input counter_t", "\""+transcript_input[counter_t].line_1+"\"")
    print(result[counter_t].line_1 == transcript_input[counter_t].line_1)
    while result[counter_t].line_1 != transcript_input[counter_t].line_1:
        print("Erste Zeile Vergleich fehlgeschlagen")
        print(result[counter_t])
        print(transcript_input[counter_t])
        print("\n")
        if counter_sbv < len(sbv_input):
            print("in if")
            result[counter_t] = SBV_Line.merge_sbv_lines(result[counter_t], sbv_input[counter_sbv])
            counter_sbv += 1    
            print("Merge")
    while result[counter_t].line_2 != transcript_input[counter_t].line_2:
        print("Zweite Zeile Vergleich fehlgeschlagen")
        if counter_sbv < len(sbv_input):
            result[counter_t] = SBV_Line.merge_sbv_lines(result[counter_t], sbv_input[counter_sbv], True)
            counter_sbv += 1
    counter_sbv += 1
    counter_t += 1

"""
    


for jedes in result:
   print(jedes)



