#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts checks for the flag "needs_sync_to_ftp" and 
# "needs_removal_from_ftp"
# It downloads the corresponding files from amara, removes the <i> and </i>
# and saves them in /downloads/subtitles_srt als subtitle_id.lang.srt
# Afterwards it connects to the ftp server and puts every *.srt file with the
# right file extension and name in the corresponding folder
#
# In the case that the "needs_removal_from_ftp" flag was set, it checks for the
# file in the folders and removes it.
#
# Afterwards it sends a log via email and resets the flags in the database
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

# Stuff for the e-mail
FROM = "localhost@subtitles.ber.c3voc.de"
TO = "barbara+transcript@selfnet.de"
TEXT = []
TEXT.append("??? ")

# Stuff for the sftp access
USER = "voc-subs"
HOST = "koeln.ftp.media.ccc.de"
PRIV_KEY = "/home/subtitles/.ssh/id_rsa"
"""
# Check current workfolder
if os.getcwd() != "/opt/subtitleStatus":
    print("Wrong path!")
    sys.exit(0)
"""    
# Change to /opt/subtitleStatus/downloads/subtitles_srt
os.chdir("./downloads/subtitles_srt")
# Check if the folder changing worked
if os.getcwd() != "/opt/subtitleStatus/downloads/subtitles_srt":
    print("Wrong path!")
    sys.exit(0)
working_folder = "/opt/subtitleStatus/downloads/subtitles_srt"
# Clear the Folder ./downloads/subtitles_srt/
# Short and ugly solution
os.system("touch stupid_temp_file")
os.system("rm *")

# Get all subtitles with flag "needs_sync_to_ftp"
my_subtitles = Subtitle.objects.filter(needs_sync_to_ftp = True).select_related("Talk","Event","Folders_Extensions","Language")

    
# Access sftp server
sftp = pysftp.Connection(username = USER, host = HOST, private_key = PRIV_KEY)

# Download ever *.srt file and fix "*" issue
for this_subtitle in my_subtitles:
    # Create filename with subtitle_id.lang_short_srt.srt
    filename = str(this_subtitle.id)+"."+this_subtitle.language.lang_short_srt+".srt"
    
    print(filename)
    
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
        #print(line)
        file.write(line)
    file.close()
    
    # Get Event Subfolder and format folders
    event_subfolder = this_subtitle.talk.event.ftp_startfolder
    
    # If the event doesn't have a subfolder on the ftp server for $reason, next loop
    if event_subfolder == "":
        continue
    
    # All possible subfolders for an event and their file extensions
    event_file_formats = this_subtitle.talk.event.ftp_subfolders_extensions.all()
    #for every in event_file_formats:
    #    print(every)
    
    # "Save" offset directory
    with sftp.cd():
        # Temporarily change to event subfolder
        sftp.chdir(event_subfolder)
        print(sftp.pwd)
        for every_file_format in event_file_formats:
            # Keep event subfolder "in mind"
            with sftp.cd():
                # Change to format associated subfolder
                sftp.chdir(every_file_format.subfolder)
                print("Format: "+every_file_format.file_extension)
                print(sftp.pwd)
                
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
                        #print(test)
                        filename_talk = result.group("filename")
                    #print(reg_pattern.group("extension"))
                        print(filename_talk)
                        # Create the name for the *.srt-File and copy the file created from amara with that name
                        filename_subtitle = filename_talk+language_srt+".srt"
                        shutil.copyfile(filename,filename_subtitle)
                        print(filename_subtitle)
                        
                        # Copy created *.srt-file on sftp
                        with sftp.cd():
                            sftp.chdir("subtitles")
                            sftp.put(filename_subtitle)
        print(sftp.pwd)
    print(sftp.pwd)
        

    
    # Jeden Ordner in dem das File liegen sollte nachsehen, zusammenbauen aus Pfad Event und Unterpfade Formate
    # Jeweils mit "with"
    # Nachsehen ob es File mit frab-Id im namen gibt (iterieren und reg-ex??)
        # Wenn nein nächster Untertitel
        # Wenn ja File-Namen passend abschneiden
        # File-Namen für UT zusammen bauen und unter neuen Namen kopieren, diesen dann in ./subtitles auf remote kopieren
        # Pro UT eine Zeile an E-Mail hängen
        
    # Reset Flag needs_sync_to_ftp
    
# Get all subtitles with flag "needs_removal_from_ftp"
my_subtitles = Subtitle.objects.filter(needs_removal_from_ftp = True).select_related("Talk","Event","Folders_Extensions","Language")

# Iterate over every possible subfolder (depending on event)
    #Find out name of file and then check if available in ./subtitles Folder an delete it

    # Reset Flag "needs_removal_from_ftp"
    
# Close sftp Connection:
sftp.close()