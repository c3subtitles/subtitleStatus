#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts removes the linebreaks which youtube insertsin *.sbv Files
# They might call it a feature, I call it a bug
# Use the input file as first parameter and the output as second parameter
#==============================================================================

#import os
import sys

if len(sys.argv) < 2:
    sys.exit("Not enough arguments! Filename needed!")
elif len(sys.argv) < 3:
    sys.exit("Not enough arguments! Filename for output needed!")
#i_file = Path(sys.argv[1])
#o_file = Path(sys.argv[2])
read_file = open(sys.argv[1], mode = "r", encoding = "utf-8")
out_file = open(sys.argv[2], mode = "w", encoding = "utf-8")

output = []

file_content = read_file.read()
text_content = file_content.splitlines()
max_counter = len(text_content)

counter = 0
while counter < max_counter-2:
    # Time codes
    output.append(text_content[counter]+"\n")
    counter += 1
    
    # First line of subtitle
    output.append(text_content[counter]+"\n")
    counter += 1
    
    while(text_content[counter]!=""):
        output[-1]= output[-1][0:-1]+" "+text_content[counter]
        counter += 1
    # Append one empty line
    output.append(text_content[counter]+"\n")
    counter += 1

for line in output:
    out_file.write(line)
    
out_file.close()
print("Done!")