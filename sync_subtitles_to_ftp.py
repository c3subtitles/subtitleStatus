#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This scripts checks for the flag "needs_sync_to_ftp" and 
# "needs_removal_from_ftp"
# It downloads the corresponding files from amara, removes the <i> and </i>
# and saves them in /downloads/subtitles_srt als subtitle_id.lang.srt
# Afterwards it connects to the ftp server and puts every *.srt file with the
# right file extension and name in the corresponding folder and in the
# event root-subtitles folder
#
# In the case that the "needs_removal_from_ftp" flag was set, it checks for the
# file in the folders and removes them.
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
import credentials as cred

# Stuff for the e-mail
FROM = cred.E_MAIL_FROM
TO = cred.E_MAIL_TO
TEXT = []
#TEXT.append("??? ")
email_text_added_subtitles = "Added subtitle files:\n"
email_text_removed_subtitles = "Removed subtitle files:\n"

# Stuff for the sftp access
USER = cred.SFTP_USER
HOST = cred.SFTP_HOST
PRIV_KEY = cred.SFTP_PRIV_KEY

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
        
        
        # root-subtitles-folder
        # Go in the subtitles folder and also save the file here with another file-name
        filename_root_subtitles_folder = this_subtitle.talk.filename + "." + language_srt + ".srt"
        with sftp.cd():
            sftp.chdir("subtitles")
            shutil.copyfile(filename, filename_root_subtitles_folder)
            sftp.put(filename_root_subtitles_folder)
        
            # When done add Name to email body
            email_text_added_subtitles += filename_root_subtitles_folder + "\n"
                        
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
    
    # srt-Ending
    language_srt = this_subtitle.language.lang_short_srt
    
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
                            # If the file is removed now, add the filename to the email
                            if not sftp.exists(filename_talk):
                                email_text_removed_subtitles += filename_talk+"\n"

        # Also remove the subtitle from the root-event-subtitles-folder
        # Go in the subtitles folder and remove the folder
        filename_root_subtitles_folder = this_subtitle.talk.filename + "." + language_srt + ".srt"
        with sftp.cd():
            sftp.chdir("subtitles")
            # Check if the file exists and if so, remove it
            if sftp.exists(filename_root_subtitles_folder):
                sftp.remove(filename_root_subtitles_folder)
                # If the file is removed now, add the filename to the email
                if not sftp.exists(filename_root_subtitles_folder):
                    email_text_removed_subtitles += filename_root_subtitles_folder + "\n"
        
                            
    # Reset needs_removal_from_ftp Flag
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