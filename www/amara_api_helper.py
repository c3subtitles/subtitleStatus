#!/usr/bin/python3
# -*- coding: utf-8 -*-

#==============================================================================
# amara_api_helper.py
# This file includes helper functions for the amara api
# It is mainly used in models.py 
#
#==============================================================================

import json
import requests
from .lock import *
import time
import credentials as cred

amara_api_call_sleep_short = 0.1
amara_api_call_sleep_long = 0.8

basis_url =  "https://amara.org/api/videos/"

# Add a new URL to a talk on amara, decide if it is the primary or not
def add_url_to_amara(url, talk, primary = False):
    basis_url = "https://amara.org/api/videos/"
    # If the talk does not have an amara key yet, the first url is the primary one
    if talk.amara_key == "":
        parameters = {"video_url": url,
            "primary_audio_language_code": talk.orig_language.lang_amara_short}
        with advisory_lock(amara_api_lock) as acquired:
            time.sleep(amara_api_call_sleep_long)
            r = requests.post(basis_url, headers = cred.AMARA_HEADER, data = json.dumps(parameters))
        print(r)
        print(type(r))
        #print(r.error)
        print(r.status_code)
        print(r.ok)
        print(r.json())
        response = r.json()
        print(response)
        print(type(response))
        if r.status_code == 400 and r.ok == False:
            if "Video already added" in response[0]:
                #FALSCH
                amara_key = response[0][-11:]
                talk.amara_key = amara_key
                talk.save()
                print("in tiefem if")
        else:
            return_content = json.loads(r.content)
            print("return_content: ", return_content)
            talk.amara_key = return_content["objects"][0]["id"]
            talk.save()
            print(r.content)#, r.content["id"])
            print("Amara Key: ", return_content["objects"][0]["id"])
    else:
        api_url = basis_url + talk.amara_key + "/urls/"
        # You can't make an url primary if it is already uploaded
        if check_if_url_on_amara(url, talk):
            r = make_uploaded_url_primary(url, talk)
        else:
            parameters = {"url": url,
                "primary": primary}
            with advisory_lock(amara_api_lock) as acquired:
                time.sleep(amara_api_call_sleep_long)
                r = requests.post(api_url, headers = cred.AMARA_HEADER, data = json.dumps(parameters))
    return r

# Get all URLs currently stored in amara for a specific video
# Additional info like the id and if the url is a primary one is also read
def get_uploaded_urls(talk):
    api_url = basis_url + talk.amara_key + "/urls/"
    if talk.amara_key == "":
        return {}
    # Get the id of the url and make it primary afterwards
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.get(api_url, headers = cred.AMARA_HEADER)
    results_dict = json.loads(result)
    links_on_amara = {}
    for any in results_dict["objects"]:
        this_url = any['url']
        links_on_amara[this_url] = {}
        links_on_amara[this_url]['id'] = any['id']
        links_on_amara[this_url]['primary'] = any['primary']
    return links_on_amara

# If a URL is already uploaded you can't upload the url a second time with primary = True
# You have to get the id of the URL and mark it as primary
def make_uploaded_url_primary(url, talk):
    api_url = basis_url + talk.amara_key + "/urls/"
    if talk.amara_key == "":
        return None
    # Get the id of the url and make it primary afterwards
    links_on_amara = get_uploaded_urls(talk=talk)
    api_url = api_url + str(links_on_amara[url]['id']) + "/"
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.put(api_url, headers = cred.AMARA_HEADER, data=json.dumps({'primary':True}))
    return result

# Remove an URL from amara
# To do this, you need the ID of the URL
def remove_url_from_amara(url, talk):
    # Get all urls on amara and their ID and put it in a dictionary
    # Check if the url which is supposed to get removed is in the dictionary
    # Remove the url
    links_on_amara = get_uploaded_urls(talk=talk)
    # Removing of a primary link is not possible
    if links_on_amara[url]['primary'] == True:
        return False
    api_url = basis_url + talk.amara_key + "/urls/" + str(links_on_amara[url]['id']) + "/"
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep)
        result = requests.delete(api_url, headers = cred.AMARA_HEADER)
    return result

# Check if a specific url is already on amara
# As additional check, check if the url is up and primary
def check_if_url_on_amara(url, talk, also_check_if_primary = False):
    # Return None if the talk does not yet have an amara key
    if talk.amara_key == "":
        return None
        
    # Get all urls from amara, compare to the ones you have and if it is primary
    api_url = basis_url + talk.amara_key + "/urls/"
    with advisory_lock(amara_api_lock) as acquired:
        time.sleep(amara_api_call_sleep_long)
        result = requests.get(api_url, headers = cred.AMARA_HEADER)
    print(result)
    results_dict = result.json()
    links_on_amara = {}
    for any in results_dict["objects"]:
        links_on_amara[any['url']] = any['primary']
    if url in links_on_amara:
        if also_check_if_primary:
            if links_on_amara[url] == True:
                return True
            else:
                return False
        else:
            return True
    else:
        return False

# Compare which links are in the database and which links are in amara
# Mirror the status in c3subtitles to amara, not the opposite
def update_amara_urls(talk):
    # If no amara key first do the add_url_to_amara with the first url in the database
    if talk.amara_key == "":
        add_url_to_amara(talk.primary_amara_video_link, talk, primary = True)
    # Get all already uploaded video links
    already_uploaded_video_links = get_uploaded_urls(talk)
    # Get all video links in the database, second priority, not the primary one
    secondary_links_in_db = talk.additional_amara_video_links.split(" ")
    # Check if the primary video link is already up if not do upload it and make it primary
    # If it is up but not as primary make it primary
    if talk.primary_amara_video_link not in already_uploaded_video_links:
        add_url_to_amara(talk.primary_amara_video_link, talk, primary = True)
    else:
        if already_uploaded_video_links[talk.primary_amara_video_link]['primary'] == False:
            make_uploaded_url_primary(talk.primary_amara_video_link, talk)

    # Check all secondary links if the are up, if not add them
    for any_link in secondary_links_in_db:
        if any_link not in already_uploaded_video_links:
            add_url_to_amara(any_link, talk, primary = False)
    
    # Check if online are some links which should be removed
    already_uploaded_video_links = get_uploaded_urls(talk)
    video_links_in_the_database = {}
    video_links_in_the_database[talk.primary_amara_video_link] = ""
    for any_link in talk.additional_amara_video_links.split(" "):
        video_links_in_the_database[any_link] = ""
    for any_link in already_uploaded_video_links:
        if any_link not in video_links_in_the_database:
            remove_url_from_amara(any_link, talk)

# Read which links are stored in amara for a specific video
# Download these urls and store them in c3subtitles
def read_links_from_amara(talk, do_save = True):
    if talk.amara_key == "":
        return None
    links_on_amara = get_uploaded_urls(talk)
    talk.additional_amara_video_link = ""
    for any_link in links_on_amara.keys():
        if links_on_amara[any_link]['primary']:
            talk.primary_amara_video_link = any_link
        else:
            talk.additional_amara_video_links += " " + any_link
    talk.additional_amara_video_links = talk.additional_amara_video_links[1:]
    if do_save:
        talk.save()
    return [talk.primary_amara_video_link, talk.additional_amara_video_links]
