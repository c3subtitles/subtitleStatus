#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
#
# DEPRECATED
# The filename column is not filled from the SFTP connection any more!
# The SFTP connection to the media cdn is not used any more.
#
# This scripts fills the filename-column in the talk table via regex from the
# sftp folders
#
# This does not need to be done regularly, usually once
# 
# The subfolder path to find the right filenames is set in the events-table
# It is build from the "ftp_startfolder" and the "subfolder_to_find_the_filenames"
# The right names are found via a regex on the frab-id and the ending with the
# last "_" is cut off.
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
                    if every_talk.filename != new_result:
                        every_talk.filename = new_result
                        every_talk.save()
        
# Close sftp connection
sftp.close()
