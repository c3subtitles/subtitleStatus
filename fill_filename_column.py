#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts fills the filename-column in the talk table via regex from the
# sftp folders
#
# This does not need to be done regularly, usually once
#==============================================================================

import os
import sys
import urllib
import re
import pysftp
import shutil

# E-Mail-Stuff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
#from email.mime.image import MIMEImage
from email import encoders

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle, Event, Folders_Extensions
import credentials as cred

# Stuff for the sftp access
USER = cred.SFTP_USER
HOST = cred.SFTP_HOST
PRIV_KEY = cred.SFTP_PRIV_KEY





# Access sftp server
sftp = pysftp.Connection(username = USER, host = HOST, private_key = PRIV_KEY)

my_events = Event.objects.all().exclude(subfolder_to_find_the_filenames = "")
print("Anzahl Events: " + str(my_events.count()))
my_talks = Talk.objects.filter(blacklisted = False)

# Check via every event
for this_event in my_events:
    # All talks belonging to this event and not blacklisted
    my_talks = Talk.objects.filter(blacklisted = False, event = this_event)
    print(my_talks.count())
    event_subfolder = this_event.ftp_startfolder + "/" + this_event.subfolder_to_find_the_filenames
    print(event_subfolder)
    # "Save" offset directory
    with sftp.cd():
        # Temporarily change to event subfolder
        sftp.chdir(event_subfolder)
        print("Befinde mich jetzt in: ")
        print(sftp.pwd)
        subfolder_file_list = sftp.listdir()
        for every_talk in my_talks:
            # Get frab id for the regex as string and compile the regex pattern
            frab_id = str(every_talk.frab_id_talk)
            pattern = "(?P<filename>^\S*-"+frab_id+"\S*[.])(?P<extension>\S*)"
            reg_pattern = re.compile(pattern)
            
            for every_filename in subfolder_file_list:
                # do regex-stuff
                result = reg_pattern.match(every_filename)
                # Only proceed if the right filename was found
                if (result != None):
                    print(frab_id + ": " + every_filename)
                    #print(result)
                    # If fits, cut to limits
                    new_pattern = "(?P<filename>^\S*)_\S*"
                    new_reg_pattern = re.compile(new_pattern)
                    new_result = new_reg_pattern.match(every_filename).groups()[0]
                    print(new_result)
                    print(" ")
                    # Save into database
                    every_talk.filename = new_result
                    every_talk.save()


        
# Close sftp connection
sftp.close()

"""
# Download ever *.srt file and fix "*" issue
for this_subtitle in my_subtitles:
    # Create filename with subtitle_id.lang_short_srt.srt
    filename = str(this_subtitle.id)+"."+this_subtitle.language.lang_short_srt+".srt"
    
    #print(filename)
    
    language = this_subtitle.language.lang_amara_short
    language_srt = this_subtitle.language.lang_short_srt
    amara_key = this_subtitle.talk.amara_key
    # Create download url
    url = "https://www.amara.org/api2/partners/videos/"+amara_key+"/languages/"+str(language)+"/subtitles/?format=srt"
    
    # Download *.srt-File from Amara
    request = urllib.request.Request(url)
    response = urllib.request.urlopen(request)
    file_content = response.read()
    # Convert from bytes object to string object
    file_content = str(file_content,encoding = "UTF-8")
    
    # Split in single lines:
    text_content = file_content.splitlines()
    
    file = open(filename, mode = "w",encoding = "utf-8")
    
    # First fix <i> and </i> issue and than save into file
    for line in text_content:
        line = re.sub("<i>","*",line)
        line = re.sub("</i>","*",line)
        file.write(line)
        file.write("\n")
        #print(line)
    file.close()
    
    # Get Event Subfolder and format folders
    event_subfolder = this_subtitle.talk.event.ftp_startfolder
    
    # If the event doesn't have a subfolder on the ftp server for $reason, next loop
    if event_subfolder == "":
        continue
    
    # All possible subfolders for an event and their file extensions
    event_file_formats = this_subtitle.talk.event.ftp_subfolders_extensions.all()
    
    # "Save" offset directory
    with sftp.cd():
        # Temporarily change to event subfolder
        sftp.chdir(event_subfolder)
        #print(sftp.pwd)
        for every_file_format in event_file_formats:
            # Keep event subfolder "in mind"
            with sftp.cd():
                # Change to format associated subfolder
                sftp.chdir(every_file_format.subfolder)
                #print(sftp.pwd)
                
                # Get the name of all files in current folder
                subfolder_file_list = sftp.listdir()
                
                # Get frab_id from database to compare all file entries with
                frab_id = str(this_subtitle.talk.frab_id_talk)
                pattern = "(?P<filename>^\S*-"+frab_id+"\S*[.])(?P<extension>\S*)"
                reg_pattern = re.compile(pattern)
                for every_filename in subfolder_file_list:
                    #print(every_filename)
                    #print(frab_id)
                    result = reg_pattern.match(every_filename)
                    # Only proceed if the right filename was found
                    if (result != None):
                        # Get Filename from regex
                        filename_talk = result.group("filename")
                        #print(filename_talk)
                        
                        # Create the name for the *.srt-File and copy the file created from amara with that name
                        filename_subtitle = filename_talk+language_srt+".srt"
                        shutil.copyfile(filename,filename_subtitle)
                        #print(filename_subtitle)
                        
                        # Copy created *.srt-file on sftp
                        with sftp.cd():
                            sftp.chdir("subtitles")
                            sftp.put(filename_subtitle)
                        
                        # Add text to email body
                        email_text_added_subtitles+=filename_subtitle+"\n"
                        
    # Reset needs_sync_to_ftp Flag
    this_subtitle.needs_sync_to_ftp = False
    this_subtitle.save()
    
 
# Get all subtitles with flag "needs_removal_from_ftp"
my_subtitles = Subtitle.objects.filter(needs_removal_from_ftp = True).select_related("Talk","Event","Folders_Extensions")

for this_subtitle in my_subtitles:
    frab_id = str(this_subtitle.talk.frab_id_talk)
    print(frab_id)
    
    # Get Event Subfolder and format folders
    event_subfolder = this_subtitle.talk.event.ftp_startfolder
    
    # If the event doesn't have a subfolder on the ftp server for $reason, next loop
    if event_subfolder == "":
        continue
    
    # All possible subfolders for an event and their file extensions
    event_file_formats = this_subtitle.talk.event.ftp_subfolders_extensions.all()
    
    # Create regex and compile
    pattern = "(?P<filename>^\S*-"+frab_id+"\S*[.]srt)"
    reg_pattern = re.compile(pattern)
    
    # Temporarily change to event subfolder
    with sftp.cd():
        sftp.chdir(event_subfolder)
    
        # Change to format associated subfolder
        for every_file_format in event_file_formats:
            # Keep event subfolder "in mind"
            with sftp.cd():
                # Change to format associated subfolder
                sftp.chdir(every_file_format.subfolder+"/subtitles")
                #print(sftp.pwd)
                
                # Get the name of all files in current folder
                subfolder_file_list = sftp.listdir()
                
                for every_filename in subfolder_file_list:
                    #print(frab_id)
                    result = reg_pattern.match(every_filename)
                    # Only proceed if the right filename was found
                    if (result != None):
                        # Get Filename from regex
                        filename_talk = result.group("filename")
                        #print(filename_talk)
                        # Check if file really exists and delete it
                        if sftp.exists(filename_talk):
                            sftp.remove(filename_talk)
                        if not sftp.exists(filename_talk):
                            email_text_removed_subtitles+=filename_talk+"\n"

    # Reset needs_sync_to_ftp Flag
    this_subtitle.needs_removal_from_ftp = False
    this_subtitle.save()
    
#print()
#print(email_text_added_subtitles)
#print(email_text_removed_subtitles)

# Close sftp Connection:
sftp.close()

# Building the email
msg = MIMEMultipart()
msg["Subject"] = "Synced or removed srt-Files from FTP-Server"
msg["From"] = FROM
msg["To"] = TO
if email_text_added_subtitles != "Added subtitle files:\n" or email_text_removed_subtitles != "Removed subtitle files:\n":
    text = MIMEText(email_text_added_subtitles+"\n\n"+email_text_removed_subtitles, "plain")
    msg.attach(text)
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
else: 
    print("Nothing done!")
"""