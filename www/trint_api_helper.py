#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# trint_api_helper.y
# This file includes helper functions for the trint api
# It is mainly used in models.py and via the admin interface 
#
#==============================================================================

import json
import requests
from urllib.parse import urlencode

#from www.models import *
import json
import time
import os

# E-Mail-Stuff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from subprocess import Popen, PIPE
import re
import threading

import credentials as cred

#from .lock import *

# TODO everything starting here into a subprocess which won't be joined
def poll_trint_api_in_background(talk, headers, make_pad_link_available, release_draft = True, do_send_email = True):
    trint_id = talk.trint_transcript_id
    url = "https://api.trint.com/export/srt/" + trint_id
    
    # Poll until the transcript is available
    while True:
        querystring = {"captions-by-paragraph":"false","max-subtitle-character-length":"42","highlights-only":"false","enable-speakers":"false","speaker-on-new-line":"false","speaker-uppercase":"false","skip-strikethroughs":"false"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        #print(response.text)
        # Wait until the url is ready
        if response.text != "Not Found":
            break
        time.sleep(10)

    # If the talk is not yet set to trint transcript, do it
    talk.refresh_from_db()
    if talk.transcript_by_id != 3:
        talk.transcript_by_id = 3
        talk.save()
        
    # Make the pad link available, remove the "#" at the beginning
    if make_pad_link_available and talk.link_to_writable_pad[0:1] == "#":
        talk.link_to_writable_pad = talk.link_to_writable_pad[1:]
        talk.save()
    if str(response.text) == "Forbidden":
        return False
    # Get the link to the srt file
    srt_link = json.loads(response.text)["url"]
    response = requests.request("GET", srt_link)
    # Save the srt transcript
    srt_text = response.text
    
    # E-Mail with srt and transcript as attachment
    FROM = "subtitles@c3subtitles.ext.selfnet.de"
    TO = cred.E_MAIL_TO_FOR_TRANSCRIPTS_TIMING
    TEXT = []
    TEXT.append("Trint ready for Talk: " + str(talk.frab_id_talk) + " " + talk.title)
    # Building the email
    msg = MIMEMultipart()

    # Build text for email with important Links
    text = MIMEText("Talk:         "+talk.title+" \n"+
        "Talk-ID:      "+str(talk.id)+"\n"+
        "Talk Frab-ID: " + str(talk.frab_id_talk)+"\n"+
        "Talk-Sprache: " + talk.orig_language.lang_amara_short + "\n" +
        "Trint-Key:    " + talk.trint_transcript_id + "\n\n" +
        "Pad writable link:    " + talk.link_to_writable_pad + "\n" +
        "Amara-Adresse:        "+"www.amara.org/videos/"+talk.amara_key+"/ \n" +
        "Talk-Adresse bei uns: https://c3subtitles.de/talk/" + str(talk.id) + "\n" +
        "Admin-Talk-Adresse:   https://c3subtitles.de/admin/www/talk/" + str(talk.id) + "\n"+
        "YouTube-Adresse im C3Subtitles YT-Account: https://www.youtube.com/watch?v=" + talk.c3subtitles_youtube_key + "\n", "plain")
    msg.attach(text)
    msg["Subject"] = "Trint transcript ready for Talk: " + str(talk.frab_id_talk) + " \"" + talk.title + "\" from " + talk.event.title
    msg["From"] = FROM
    msg["To"] = TO
    msg["reply-to"] = "subtitles-logs@lists.selfnet.de"
    
    filename = talk.slug+"."+talk.orig_language.lang_amara_short+".srt"
    folder = "/tmp/"
    # Save File in ./downloads
    file = open(folder+filename, mode = "w",encoding = "utf-8")
    for line in srt_text:
        file.write(line)
    file.close()
    
    # Release the draft subtitle
    if release_draft and talk.amara_key != "":
        my_ss = talk.subtitle_set.all().filter(is_original_lang=True)
        if my_ss.count()==1:
            my_s = my_ss[0]
            my_s.put_subtitle_draft_into_sync_folder(draft=True, text=srt_text)
            my_s.has_draft_subtitle_file = True
            my_s.save()

    # Build attachment File for email an attach and delete the file afterwards
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(open(folder + filename, 'rb').read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment',filename=os.path.split(filename)[1])
    msg.attach(attachment)
    os.remove(folder + filename)

    # Create the transcript from srt and also attach it to the mail
    text_content = srt_text.split("\n")
    filename = talk.slug+"."+talk.orig_language.lang_amara_short+".txt"
    transcript = []
    # Ignore first two lines and check lines afterwards
    # Took this from the other file?!
    transcript.append(text_content[2]+"\n")
    if len(text_content) <= 3:
        i = 4
    elif len(text_content) < 5:
        i = 2
    elif text_content[3] == "":
        i = 3
    elif text_content[4] == "":
        i = 4
    elif text_content[5] == "":
        i = 5

    # Check rest of whole file
    while i < len(text_content):
        # If line is empty jump two down
        if(text_content[i] == ""):
            transcript.append("\n")
            i += 3
        # If line ist not empty save to future output
        else:
            transcript.append(text_content[i]+"\n")
            i += 1
    new_transcript = ""
    for any in transcript:
        new_transcript += " " + any
    new_transcript = new_transcript.replace("\n", " ")
    new_transcript = new_transcript.replace("  ", " ")
    new_transcript = new_transcript.replace("  ", " ")
    if new_transcript[0:1] == " ":
        new_transcript = new_transcript[1:]

    # Save File in ./downloads
    file = open(folder+filename,mode = "w",encoding = "utf-8")
    for line in new_transcript:
        file.write(line)
    file.close()
    # Build attachment File for email an attach and delete afterwards
    attachment = MIMEBase('application', 'octet-stream')
    attachment.set_payload(open(folder + filename, 'rb').read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment',filename=os.path.split(filename)[1])
    msg.attach(attachment)
    os.remove(folder + filename)

    # Mail verschicken
    if do_send_email:
        try:
            p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE, universal_newlines=True)
            p.communicate(msg.as_string())
            print("Mail send")
            return True
        except:
            print("Mail Exception")
            return False

# This function uses the talk.link_to_video_file to push the file to the amara api
# and polls for the finished transcript
# If this is used via the browser in admin, the interface is blocked until the
# transcript is ready and the email is sent
def get_trint_transcript_via_api(talk, trint_api_key=cred.TRINT_API_KEY, make_pad_link_available=True, release_draft = True, do_send_email = True):
    # Only proceed if the talk actually has a video file link
    # Not proceed if the talk has no video link and no transcript id
    if talk.link_to_video_file == "" and talk.trint_transcript_id =="":
        return False

    # Download the talk-file into a folder like /tmp/
    # Get the filename from the whole path
    filename = talk.link_to_video_file.split("/")[-1]
    output_filename = "/var/tmp/" + filename
    url = talk.link_to_video_file
    r = requests.get(url)
    # Only download the file if it is needed later on
    if talk.trint_transcript_id == "":
        open(output_filename , 'wb').write(r.content)
    
    # Afterwards upload to trint
    headers = {'api-key':trint_api_key,'content-type':'video/mp4',}
    
    # Only upload to amara if the language is English or German, no Klingon!!
    if talk.orig_language.lang_amara_short == "en" or talk.orig_language.lang_amara_short == "de":
        pass
    else:
        return False

    # Only upload the video if the talk does not yet have a trint_transcript_id
    if talk.trint_transcript_id == "":
        params = (('filename', filename),('folder-id',talk.event.trint_folder_id),('language',talk.orig_language.lang_amara_short),('detect-speaker-change',True),)

        data = open(output_filename, 'rb').read()
        response = requests.post('https://upload.trint.com/', headers=headers, params=params, data=data)
        output = response.json()
        # Avoid overwriting changes in the talk if someone else worked on it in the meantime
        talk.refresh_from_db()
        talk.trint_transcript_id = output["trintId"]
        talk.transcript_by_id = 3
        talk.save()
        # Delete the file locally
        os.remove(output_filename)
    
    #poll_trint_api_in_background(talk=talk, headers=headers)
    threading.Thread(target=poll_trint_api_in_background, name=None, args=[talk, headers, make_pad_link_available, release_draft, do_send_email]).start()


