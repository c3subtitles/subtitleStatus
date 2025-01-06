#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# This script helps creating Tweets for released subtitles and sending them
# No Flags will be reset!
#==============================================================================

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Subtitle, Talk, Event, Language

import twitter as tw
import credentials as cred

max_tweet_length = 280

"""
# DEPRECATED subtitles are not released to media any more
# A subtitle on media has been released or updated
def create_tweet_for_media(subtitle_id):
    # Check if there really is a subtitle available with this Id:
    try:
        my_subtitle = Subtitle.objects.get(id = subtitle_id)
    except:
        return(None)
    #  Stop if the subtitle is not completed
    if not my_subtitle.complete:
        return(None)
    
    # Get associated Data from the database
    try:
        my_talk = Talk.objects.get(id = my_subtitle.talk_id)
        my_language = Language.objects.get(id = my_subtitle.language_id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)
        
    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles released for "
    name_of_talk = my_talk.title
    hashtag = my_event.hashtag
    link = "https://cdn.media.ccc.de" + my_event.ftp_startfolder[3:]
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len(string) + 4 + len(name_of_talk) + 3 + 23 + len(hashtag) + 1 > max_tweet_length:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"
    
    my_tweet = string + '"' + name_of_talk + '" on: ' + link + " " + hashtag
    #print (my_tweet)
    return my_tweet
"""


# A subtitle on the selfnet mirror has been released or updated
def create_tweet_for_selfnet_mirror(subtitle_id):
    # Check if there really is a subtitle available with this Id:
    try:
        my_subtitle = Subtitle.objects.get(id = subtitle_id)
    except:
        return(None)
    #  Stop if the subtitle is not completed
    if not my_subtitle.complete:
        return(None)
    # Check if the file really is on the mirror and only then proceed
    
    
    
    # Get associated Data from the database
    try:
        my_talk = Talk.objects.get(id = my_subtitle.talk_id)
        my_language = Language.objects.get(id = my_subtitle.language_id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)

    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles released for "
    name_of_talk = my_talk.title
    hashtag = my_event.hashtag
    link = "https://mirror.selfnet.de/c3subtitles/" + my_subtitle.talk.event.subfolder_in_sync_folder
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len(string) + 4 + len(name_of_talk) + 3 + 23 + len(hashtag) + 1 > max_tweet_length:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"
    
    my_tweet = string + '"' + name_of_talk + '" on: ' + link + " " + hashtag
    #print (my_tweet)
    return my_tweet


# A subtitle on YT has been released or updated    
def create_tweet_for_YT(subtitle_id):
    # Check if there really is a subtitle available with this Id:
    try:
        my_subtitle = Subtitle.objects.get(id = subtitle_id)
    except:
        return(None)
    #  Stop if the subtitle is not completed
    if not my_subtitle.complete:
        return(None)
    
    # Get associated Data from the database
    try:
        my_talk = Talk.objects.get(id = my_subtitle.talk_id)
        my_language = Language.objects.get(id = my_subtitle.language_id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)
        
    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles released for "
    name_of_talk = my_talk.title
    hashtag = my_event.hashtag
    link = "https://youtube.com/user/mediacccde"
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len(string) + 4 + len(name_of_talk) + 3 + 23 + len(hashtag) + 1 > max_tweet_length:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"
    
    my_tweet = string + '"' + name_of_talk + '" on: ' + link + " " + hashtag
    #print (my_tweet)
    return my_tweet


# Create a tweet for a subtitle which is now auto timed and needs review
def create_tweet_for_needs_quality_control(id):
    # Check if there really is a subtitle available with this Id:
    try:
        my_subtitle = Subtitle.objects.get(id = id)
    except:
        return(None)
    #  Stop if the subtitle is not in the quality control mode
    if my_subtitle.state_id != 7:
        return(None) 
    # Get associated Data from the database
    try:
        my_talk = Talk.objects.get(id = my_subtitle.talk_id)
        my_language = Language.objects.get(id = my_subtitle.language_id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)
    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    string = my_language.language_en + " #subtitles for "
    name_of_talk = my_talk.title
    #name_of_talk = "012345678901234567890123456789012345678901234567890123456798"
    hashtag = my_event.hashtag
    link = "https://c3subtitles.de/talk/" + str(my_subtitle.talk_id)
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len(string) + 1 + len(name_of_talk) + 35 + 23 + 1 + len(hashtag) > max_tweet_length:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"
    
    my_tweet = string + '"' + name_of_talk + '" need to be reviewed! Join us on: ' + link + " " + hashtag
    #print (my_tweet)
    return my_tweet


# Create a tweet for a subtitle which is now available with transcript
def create_tweet_for_transcript_is_now_available(talk_id):
    # Check if there really is a talk available with this Id:
    try:
        my_talk = Talk.objects.get(id = talk_id)
        #my_language = Language.objects.get(id = my_talk.orig_language.language_id)
        my_language = Language.objects.get(id = my_talk.orig_language.id)
        my_event = Event.objects.get(id = my_talk.event_id)
    except:
        return(None)
    # Workaround for Klingon :D
    if my_language.id == 289:
        my_language.language_en = "Original"
    lang_string = my_language.language_en
    name_of_talk = my_talk.title
    #name_of_talk = "012345678901234567890123456789012345678901234567890123456798" +"012345678901234567890123456789012345678901234567890123456798" +"012345678901234567890123456789012345678901234567890123456798"
    hashtags = my_event.hashtag
    link = "https://c3subtitles.de/talk/" + str(talk_id)
    # Test : The [language] talk "talk title" now has a transcript available for you to work on.
    # Join us here: c3s-link
    # Hashtags
    
    # Länge des Tweets setzt sich zusammen aus den Strings und 23 Zeichen für den Link
    while len("The ") + len(lang_string) + len(" talk \"") + len(name_of_talk) + len("\" now has a transcript available for you to work on. Join us here: ") + 23 + 2 + len(hashtags) > max_tweet_length:
        name_of_talk = name_of_talk[:-2]
        name_of_talk = name_of_talk + "…"

    my_tweet = "The " + lang_string + " talk \"" + name_of_talk + "\" now has a transcript available for you to work on. Join us here: https://c3subtitles.de/talk/" + str(my_talk.id) + " " + hashtags
    print (my_tweet)
    return my_tweet


# Pure tweeting
def do_tweet(tweet_content = "Something!", use_progress_twitter_account=False):
    return False                # don't update twitter anymore
    if tweet_content == None:
        return False
    my_twitter = tw.Twitter( auth = tw.OAuth(cred.TW_C3R_ACCESS_TOKEN,
        cred.TW_C3R_ACCESS_TOKEN_SECRET,
        cred.TW_C3R_API_KEY,
        cred.TW_C3R_API_SECRET))
    if use_progress_twitter_account:
        my_twitter = tw.Twitter(auth = tw.OAuth(cred.TW_C3P_ACCESS_TOKEN,
            cred.TW_C3P_ACCESS_TOKEN_SECRET,
            cred.TW_C3P_API_KEY,
            cred.TW_C3P_API_SECRET))
    try:
        my_twitter.statuses.update(status = tweet_content)
        return True
    except tw.TwitterHTTPError as e:
        return False

# Tweet only media.ccc.de releases/updates
def tweet_subtitles_update_media(id):
    return do_tweet(create_tweet_for_media(id))

# Tweet only YT releases/updates
def tweet_subtitles_update_YT(id):
    return do_tweet(create_tweet_for_YT(id))

def tweet_subtitle_needs_quality_control(id):
    return do_tweet(create_tweet_for_needs_quality_control(id), use_progress_twitter_account=True)
 
# Tweet for YT and media updates/releases
def tweet_subtitles_update(id):
    ret_1 = tweet_subtitles_update_media(id)
    ret_2 = tweet_subtitles_update_YT(id)
    if ret_1 == ret_2 == True:
        return True
    else:
        return False

def tweet_subtitles_update_mirror(id):
    return do_tweet(create_tweet_for_selfnet_mirror(id))
