# -*- coding: utf-8 -*-

from datetime import datetime, timezone, timedelta
from django.db import models
from django.db.models import Sum, Q
from django.core.urlresolvers import reverse
from django.db import transaction
from .statistics_helper import *
import json
import credentials as cred

# Basic model which provides a field for the creation and the last change timestamp
class BasisModell(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    touched = models.DateTimeField(auto_now = True)

    class Meta:
        abstract = True


# For every event in which subfolder on the ftp the subtitles are supposed to appear and with which file extensions
class Folders_Extensions(BasisModell):
    subfolder = models.CharField(max_length = 10, default = "", blank = True)
    file_extension = models.CharField(max_length = 10, default = "", blank = True)

    def __str__(self):
        return self.subfolder+","+self.file_extension


# Event and its data
class Event(BasisModell):
    schedule_version = models.CharField(max_length = 50, default = "0.0", blank = True)
    acronym = models.CharField(max_length = 20, default = "", blank = True)
    title = models.CharField(max_length = 100, default = "No title yet", blank = True)
    start = models.DateField(default = "1970-01-01", blank = True)
    end = models.DateField(default = "1970-01-01", blank = True)
    timeslot_duration = models.TimeField(default = "00:15", blank = True)
    days = models.PositiveSmallIntegerField(default = 1, blank = True)
    schedule_xml_link = models.URLField()
    city = models.CharField(max_length = 30, default = "", blank = True)
    building = models.CharField(max_length = 30, default = "", blank = True)
    ftp_startfolder = models.CharField(max_length = 100, default = "", blank = True)
    ftp_subfolders_extensions = models.ManyToManyField(Folders_Extensions, default = None, blank = True)
    hashtag = models.CharField(max_length = 10, default = "", blank = True)
    subfolder_to_find_the_filenames = models.CharField(max_length = 20, default = "", blank = True) # To find the right filenames via regex via frab-id
    speaker_json_link = models.URLField(blank = True, default = "")
    speaker_json_version = models.CharField(max_length = 50, default = "0.0", blank = True)
    blacklisted = models.BooleanField(default = False, blank = True)
    cdn_subtitles_root_folder = models.URLField(default = "", blank = True)
    subfolder_in_sync_folder = models.CharField(max_length = 100, default = "", blank = True) # For the rsync to the selfnet mirror, no slashes at the beginning and end

    def isDifferent(id, xmlFile):
        with open("data/eventxml/{}.xml".format(id),'rb') as f:
            savedXML = f.read()
            return savedXML == xmlFile.data


    # Create Entries in Statistics_Event model for any available combination
    def create_statistics_event_entries(self):
        my_subtitles = Subtitle.objects.filter(is_original_lang = True, talk__event = self)
        my_talks = Talk.objects.filter(event = self)
        for any in my_subtitles:
            this = Statistics_Event.objects.get_or_create(event = self, language = any.language)
            # If new created, than also set the flag for recalculate
            if this[1]:
                this[0].recalculate_statistics = True
                this[0].save()
        for any in my_talks:
            this = Statistics_Event.objects.get_or_create(event = self, language = any.orig_language)
            # If new created, also recalculate
            if this[1]:
                this[0].recalculate_statistics = True
                this[0].save()

    @property
    def page_sub_titles(self):
        return [self.acronym]

    @property
    def has_statistics(self):
        statistics_this_event = Statistics_Event.objects.filter(event = self)
        if statistics_this_event.count() == 0:
            return False
        else:
            counter_statistics_with_none = 0
            for any in statistics_this_event:
                if any.words == None:
                    counter_statistics_with_none += 1
            if counter_statistics_with_none == statistics_this_event.count():
                return False
            else:
                return True

    # Save Fahrplan xml file with version in the name into ./www/static/
    def save_fahrplan_xml_file(self):
        import datetime
        if self.schedule_xml_link[0:1] == "#" or self.schedule_xml_link == "":
            return None
        from urllib import request
        from lxml import etree
        response = request.urlopen(self.schedule_xml_link)
        # Read as file
        file_content = response.read()
        file_content = str(file_content,encoding = "UTF-8")
        # Get the version from the xml
        tree = etree.parse(request.urlopen(self.schedule_xml_link))
        fahrplan = tree.getroot()
        fahrplan_version = fahrplan[0].text
        # Create the filename and save
        folder = "./www/static/fahrplan_files/"
        filename = self.acronym + " fahrplan version "  + fahrplan_version + " " + "{:%Y-%m-%d_%H:%M:%S}".format(datetime.datetime.now())
        filename = filename.replace("/","_")
        file = open(folder + filename + ".xml", mode = "w", encoding = "utf-8")
        file.write(file_content)
        file.close()
        return True

    # Save Speaker json file with version in the name into ./www/static/
    def save_speaker_json_file(self):
        import datetime
        if self.speaker_json_link[0:1] == "#" or self.speaker_json_link == "":
            return None
        from urllib import request
        response = request.urlopen(self.speaker_json_link)
        result = response.read()
        result = result.decode("utf8")
        file_content = result
        result = json.loads(result)
        fahrplan_version = result["schedule_speakers"]["version"]
        folder = "./www/static/fahrplan_files/"
        filename = self.acronym + " speaker version " + fahrplan_version + " " + "{:%Y-%m-%d_%H:%M:%S}".format(datetime.datetime.now())
        filename = filename.replace("/","_")
        file = open(folder + filename + ".json",mode = "w",encoding = "utf-8")
        file.write(file_content)
        file.close()
        return True

    def __str__(self):
        return self.acronym


# Days which belong to an event
class Event_Days(BasisModell):
    event = models.ForeignKey(Event)
    index = models.PositiveSmallIntegerField(default = 0)
    date = models.DateField(default = "1970-01-01", blank = True)
    day_start = models.DateTimeField(default = "1970-01-01 00:00", blank = True)
    day_end = models.DateTimeField(default = "1970-01-01 00:00", blank = True)

    def __str__(self):
        return 'Day {}'.format(self.index)


# "Rooms" in which an event takes place, might also be outside
class Rooms(BasisModell):
    room = models.CharField(max_length = 30, default = "kein Raum")
    building = models.CharField(max_length = 30, default = "")

    def __str__(self):
        return self.room


# Different languages and their "codes" in amara or the name in German end English in full names
class Language(BasisModell):
    language_en = models.CharField(max_length = 40, default = "")
    language_de = models.CharField(max_length = 40, default = "", blank = True)
    #lang_short_2 = models.CharField(max_length = 3, default = "", blank = True)#, unique = True) not really used
    lang_amara_short = models.CharField(max_length = 15, default = "", unique = True)
    lang_short_srt = models.CharField(max_length = 15, default = "", blank = True)
    language_native = models.CharField(max_length = 40, default = "", blank = True)
    amara_order = models.PositiveSmallIntegerField(default = 0, blank = True)
    lang_code_media = models.CharField(max_length = 3, default = "", blank = True) # ISO 639-2 to talk to the media.ccc.de API
    lang_code_iso_639_1 = models.CharField(max_length = 10, default = "", blank = True)

    def __str__(self):
        return self.lang_amara_short

    # Display-Name of the language in english, no "None" or "Klingon".
    @property
    def display_name(self):
        if self.id == 0 or self.id == 289:
            return "Original (mixed)"
        else:
            return self.language_en


# Category of the talk, like "ethics"
class Tracks(BasisModell):
    track = models.CharField(max_length = 50, default = "")

    def __str__(self):
        return self.track


# How the talk is presented, like a workshop or a talk
class Type_of(BasisModell):
    type = models.CharField(max_length = 20, default = "")

    def __str__(self):
        return self.type


# Speaker or Speakers of the Talk
class Speaker(BasisModell):
    frab_id = models.PositiveSmallIntegerField(default = -1)
    name = models.CharField(max_length = 50, default = "")
    doppelgaenger_of = models.ForeignKey('self', on_delete = models.SET_NULL, blank = True, null = True)
    abstract = models.TextField(default = "", blank = True, null = True)
    description = models.TextField(default = "", blank = True, null = True)

    @property
    def has_statistics(self):
        speakers_statistics = Statistics_Speaker.objects.filter(speaker = self)
        for any in speakers_statistics:
            if any.average_wpm is not None:
                return True
            if any.average_spm is not None:
                return True
        return False

    @property
    def has_links(self):
        speakers_links = Speaker_Links.objects.filter(speaker = self)
        if speakers_links.count() == 0:
            return False
        else:
            return True

    """
    # Probably not needed any more..
    def average_wpm_in_one_talk(self, talk):
        my_statistics = Statistics_Raw_Data.objects.filter(speaker = self, talk = talk)
        words = 0
        time = 0
        for this_statistics in my_statistics:
            if this_statistics.words is not None and this_statistics.time_delta is not None:
                words += this_statistics.words
                time += this_statistics.time_delta
            else:
                return None
        if time == 0:
            return None
        return words * 60.0 / time

    def average_spm_in_one_talk(self, talk):
        my_statistics = Statistics_Raw_Data.objects.filter(speaker = self, talk = talk)
        strokes = 0
        time = 0
        for this_statistics in my_statistics:
            if this_statistics.strokes is not None and this_statistics.time_delta is not None:
                strokes += this_statistics.strokes
                time += this_statistics.time_delta
            else:
                return None
        if time == 0:
            return None
        return strokes * 60.0 / time
    """

    @property
    def page_sub_titles(self):
        return ['Speaker', self.name]


# Links from the Fahrplan
class Speaker_Links(BasisModell):
    speaker = models.ForeignKey(Speaker, blank = True)
    title = models.CharField(max_length = 200, default = "", blank = True)
    url = models.URLField(blank = True)


# Where is the Transcipt from, autogenerated or handmade
class Transcript (BasisModell):
    creator = models.CharField(max_length = 20, blank = True, null = True) # None, trint, youtube, scribie, handmade ..., default with id=0 is None


# Talk with all its data
class Talk(BasisModell):
    frab_id_talk = models.CharField(max_length = 10, default = "-1", blank = True)
    blacklisted = models.BooleanField(default=False, blank = True)
    day = models.ForeignKey(Event_Days, default = 1, blank = True)
    room = models.ForeignKey(Rooms, default = 15)
    link_to_logo = models.URLField(default = "", blank = True)
    date = models.DateTimeField(default = "1970-01-01 00:00:00+01:00", blank = True)
    start = models.TimeField(default = "11:00" ,blank = True)
    duration = models.TimeField(default = "00:45", blank = True)
    title = models.CharField(max_length = 150, default = "ohne Titel", blank = True)
    subtitle_talk = models.CharField(max_length = 300, default = " ", blank = True) # nicht UT sondern Ergänzung zum Titel
    track = models.ForeignKey(Tracks, default = 40, blank = True)
    event = models.ForeignKey(Event, default = 3, blank = True)
    type_of = models.ForeignKey(Type_of, default = 9, blank = True)
    orig_language = models.ForeignKey(Language, default = 287, blank = True)
    abstract = models.TextField(default = "", blank = True)
    description = models.TextField(default = "", blank = True)
    persons = models.ManyToManyField(Speaker, through = "Talk_Persons", default = None, blank = True) #through="Talk_Persons"
    pad_id = models.CharField(max_length = 30, default = "", blank = True)
    link_to_writable_pad = models.URLField(default = "", blank = True)
    link_to_readable_pad = models.URLField(default = "", blank = True)
    link_to_video_file = models.URLField(max_length = 200, default = "", blank = True)
    amara_key = models.CharField(max_length = 20, default = "", blank = True)
    youtube_key = models.CharField(max_length = 20, blank = True)
    video_duration = models.TimeField(default = "00:00", blank = True)
    slug = models.SlugField(max_length = 200, default = "", blank = True)
    youtube_key_t_1 = models.CharField(max_length = 20, blank = True, default = "")
    youtube_key_t_2 = models.CharField(max_length = 20, blank = True, default = "")
    guid = models.CharField(max_length = 40, blank = True, default = "") # from the Fahrplan
    filename = models.SlugField(max_length = 200, default = "", blank = True) # will be used for a more flexible sftp upload, at the moment only for the subtitles folder in the root-event directory
    time_delta = models.FloatField(blank = True, null = True)   # The duration of the talk in seconds
    words = models.IntegerField(blank = True, null = True)      # Words in the whole subtitles file
    strokes = models.IntegerField(blank = True, null = True)    # Strokes in the whole subtitles file
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from the words and the time_delta
    average_spm = models.FloatField(blank = True, null = True)  # Calculated from the strokes and the time_delta
    recalculate_talk_statistics = models.BooleanField(default = False)
    speakers_words = models.IntegerField(blank = True, null = True)      # Words in the parts of all speakers
    speakers_strokes = models.IntegerField(blank = True, null = True)    # Strokes in the parts of all speakers
    speakers_time_delta = models.FloatField(blank = True, null = True)   # The duration of the talk in seconds while all speakers speak - the timeslots are in statistics_Raw_Data
    speakers_average_wpm = models.FloatField(blank = True, null = True)  # Calculated from the speakers_words and the speakers_time_delta
    speakers_average_spm = models.FloatField(blank = True, null = True)  # Calculated from the speakers_strokes and the speakers_time_delta
    recalculate_speakers_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string
    n_most_frequent_words_speakers = models.TextField(default = "{}")    # n most common words as json string
    has_priority = models.BooleanField(default = False)                 # If the talk has priority because it was requested by someone
    transcript_by = models.ForeignKey(Transcript, default = 0)      # Where is the Transcript from? Handmade, None, Youtube, Trint, Scribie...
    amara_activity_last_checked = models.DateTimeField(default = datetime.min, blank = True)        # Light check, only amara activity
    amara_update_interval = models.TimeField(default = "00:10", blank = True) # How often is activity checked?
    amara_complete_update_last_checked = models.DateTimeField(default = datetime.min, blank = True) # Everything checked, activity and data of every single subtitle
    needs_complete_amara_update = models.BooleanField(default = False)
    next_amara_activity_check = models.DateTimeField(default = datetime.min, blank = True)

    # Recalculate statistics data over the whole talk
    @transaction.atomic
    def recalculate_whole_talk_statistics(self, force = False):
        # Recalculate statistics data over the whole talk
        # Only if a original subtitle exists which is at least transcribing finished
        my_subtitles = Subtitle.objects.filter(Q(talk = self),
            Q(is_original_lang = True), Q(complete = True) | Q(state_id = 5) |
            Q(state_id = 7) | Q(state_id = 3) | Q(state_id = 6))
        if my_subtitles.count() == 1:
            # In this case, recalculate the time_delta
            if force or self.recalculate_talk_statistics:
                values = calculate_subtitle(self)
                if values is not None:
                    self.time_delta = values["time_delta"]
                    self.words = values["words"]
                    self.strokes = values["strokes"]
                    self.average_wpm = values["average_wpm"]
                    self.average_spm = values["average_spm"]
                    self.recalculate_talk_statistics = False
                    self.save()

                # Save the word frequencies into a json file
                if values["word_frequencies"] is not None and len(values["word_frequencies"]) > 0:
                    save_word_dict_as_json(values["word_frequencies"],"talk_complete", self.id)
                    self.n_most_frequent_words = json.dumps(n_most_common_words(values["word_frequencies"]), ensure_ascii = False)
                    self.save()
                else:
                    self.n_most_frequent_words = "{}"
                    self.save()

                # Set recalculate flags in the Statistics_Event module
                Statistics_Event.objects.filter(event = self.event).update(recalculate_statistics = True)


    # Recalculate Speakers in Talk Statistics-Data
    # If any related data in Statistics_Raw_Data exist!
    @transaction.atomic
    def recalculate_speakers_in_talk_statistics(self, force = False):
        if force or self.recalculate_speakers_statistics:
            # Dictionary for the word freqiencies
            word_freq = {}
            # Check for all Statistics_Raw_Data with this talk no matter which Speaker
            all_datasets = Statistics_Raw_Data.objects.filter(talk = self)
            # If there is no data available, set everything to Null
            if all_datasets.count() == 0:
                self.speakers_words = None
                self.speakers_strokes = None
                self.speakers_time_delta = None
                self.speakers_average_wpm = None
                self.speakers_average_spm = None
                self.recalculate_speakers_statistics = False
                self.save()
            else:
                # Check if any of these datasets first needs a recalculation
                # If so, first recalculate:
                for any_dataset in all_datasets:
                    if any_dataset.recalculate_statistics:
                        any_dataset.recalculate()
                    # Calculate word_frequencies
                    word_freq = merge_word_frequencies_dicts(word_freq, any_dataset.word_frequencies)
                # Sum up all words of any speaker in this talk
                self.speakers_words = all_datasets.aggregate(Sum("words"))["words__sum"]
                # Sum up all strokes of any speaker in this talk
                self.speakers_strokes = all_datasets.aggregate(Sum("strokes"))["strokes__sum"]
                # Sum up time_delta of any speaker in this talk
                self.speakers_time_delta = all_datasets.aggregate(Sum("time_delta"))["time_delta__sum"]
                # Calculate stuff
                self.speakers_average_wpm = calculate_per_minute(self.speakers_words, self.speakers_time_delta)
                self.speakers_average_spm = calculate_per_minute(self.speakers_strokes, self.speakers_time_delta)
                self.recalculate_speakers_statistics = False
                self.save()
            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq, "talk_speakers", self.id)
                self.n_most_frequent_words_speakers = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
                self.save()
            else:
                self.n_most_frequent_words_speakers = "{}"
                self.save()

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        self.recalculate_whole_talk_statistics(force)
        self.recalculate_speakers_in_talk_statistics(force)

    # Reset statistics data related to this talk
    # Is used for a original_subtitle update
    # use hard_reset = True if a subtitle is reset from complete to not complete any more
    @transaction.atomic
    def reset_related_statistics_data(self, hard_reset = False):
        # If hard reset, do reset the values but do not recalculate!
        # Only the Speakers statistics data is not reset here because it would get recalculated anyway
        if hard_reset:
            # Reset everything of the talk and directly related to the talk
            self.average_spm = None
            self.average_wpm = None
            self.strokes = None
            self.words = None
            self.time_delta = None
            self.speakers_average_spm = None
            self.speakers_average_wpm = None
            self.n_most_frequent_words = "{}"
            self.n_most_frequent_words_speakers = "{}"
            Statistics_Raw_Data.objects.filter(talk = self).update(time_delta = None,
                words = None,
                strokes = None)
            Talk_Persons.objects.filter(talk = self).update(average_spm = None,
                average_wpm = None,
                words = None,
                strokes = None,
                time_delta = None,
                n_most_frequent_words = "{}")
        # If no hard_reset only set all recalculate flags
        else:
            Statistics_Raw_Data.objects.filter(talk = self).update(recalculate_statistics = True)
            Talk_Persons.objects.filter(talk = self).update(recalculate_statistics = True)
            self.recalculate_talk_statistics = True
            self.recalculate_speakers_statistics = True
        self.save()

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)

    # Return the n most common words of the speakers as dict
    @property
    def n_common_words_speakers(self):
        return json.loads(self.n_most_frequent_words_speakers)

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("talk_complete", self.id)

    # Return the word_frequencies of speakers as dictionary
    @property
    def word_frequencies_speakers(self):
        return read_word_dict_from_json("talk_speakers", self.id)

    @property
    def needs_automatic_syncing(self):
        return self.subtitle_set.filter(needs_automatic_syncing = True).count() > 0

    # State of the subtitle or its pad
    @property
    def complete(self):
        return self.subtitle_set.filter(complete = False).count() == 0

    @property
    def last_changed_on_amara(self):
        try:
            changed = self.subtitle_set.filter(is_original_lang = True).get().last_changed_on_amara
            for sub in self.subtitle_set.filter(is_original_lang = False):
                if sub.last_changed_on_amara > changed:
                    changed = sub.last_changed_on_amara
            if changed < self.created:
                return None
            else:
                return changed
        except:
            return None

    def get_absolute_url(self):
        return reverse('www.views.talk', args=[str(self.id)])

    @property
    def has_statistics(self):
        """ If there are statistics data available for this talk """
        if self.average_spm is None:
            return False
        elif self.average_spm is None:
            return False
        else:
            return True

    @property
    def has_speakers_statistics(self):
        if self.speakers_average_spm is None:
            return False
        elif self.speakers_average_wpm is None:
            return False
        else:
            return True

    @property
    def language_of_original_subtitle(self):
        this_subtitles = Subtitle.objects.filter(talk = self, is_original_lang = True)
        if this_subtitles.count() == 0:
            return None
        elif this_subtitles.count() == 1:
            return this_subtitles[0].language

    @property
    def has_original_subtitle(self):
        my_subtitles = Subtitle.objects.filter(talk = self, is_original_lang = True)
        if my_subtitles.count() > 0:
            return True
        else:
            return False

    @property
    def has_finished_original_subtitle(self):
        my_subtitles = Subtitle.objects.filter(talk = self, is_original_lang = True, complete = True)
        if my_subtitles.count() > 0:
            return True
        else:
            return False

    @property
    def has_original_subtitle_in_transcript_state(self):
        if self.subtitle_set.filter(is_original_lang = True, state_id = 2).count() >= 1:
            return True
        else:
            return False

    @property
    def has_transcript_by_trint(self):
        if self.transcript_by.id == 3:
            return True
        else:
            return False

    @property
    def has_transcript_by_scribie(self):
        if self.transcript_by.id == 4:
            return True
        else:
            return False

    @property
    def has_transcript_by_youtube(self):
        if self.transcript_by.id == 2:
            return True
        else:
            return False

    @property
    def has_transcript_by_human(self):
        if self.transcript_by.id == 1:
            return True
        else:
            return False

    @property
    def page_sub_titles(self):
        return self.event.page_sub_titles + [self.title]

    @property
    def has_links(self):
        talk_links = Links.objects.filter(talk = self)
        if talk_links.count() == 0:
            return False
        else:
            return True

    # Override delete function
    @transaction.atomic
    def delete(self, *args, **kwargs):
        # Delete related Talk_Persons datasets
        Talk_Persons.objects.filter(talk = self).delete()
        # Delete related Links datasets
        Links.objects.filter(talk = self).delete()
        # Delete related Subtitle datasets
        Subtitle.objects.filter(talk = self).delete()
        # Delete realted Statistics_Raw_Data
        Statistics_Raw_Data.objects.filter(talk = self).delete()

        # Call super delete function
        super(Talk, self).delete(*args, **kwargs)

    # Create a timedelta of the amara_update_interval, for much easier use
    @property
    def calculated_time_delta_for_activities(self):
        return timedelta(seconds = self.amara_update_interval.second,
            minutes = self.amara_update_interval.minute,
            hours = self.amara_update_interval.hour,
            microseconds = self.amara_update_interval.microsecond)

    # Check activity on amara
    @transaction.atomic
    def check_activity_on_amara(self, force = False):
        # Take the timestamp for "last executed at" at the beginning of the function
        start_timestamp = datetime.now(timezone.utc)
        # Only proceed if forced or if the time delta for another query has passed
        if force or (start_timestamp > self.next_amara_activity_check):
            import requests
            # Only check for new versions. New urls or other stuff is not interesting
            # Check for changes after the last check
            # If the check is forced, do not care about the last time the activity was checked
            if force:
                parameters = {'type': 'version-added'}
            else:
                parameters = {'type': 'version-added',
                    'after': self.amara_activity_last_checked}
            basis_url = "https://amara.org/api/videos/"
            url = basis_url + self.amara_key + "/activity/"
            results = {}
            # Loop as long as not all new activity datasets have been checked
            # The json result from amara includes a "next" field which has the url for the next query if not
            # all results came with the first query
            while url != None:
                r = requests.get(url, headers = cred.AMARA_HEADER, params = parameters)
                #print(r.text)
                # If amara doesn't reply with a valid json create one.
                try:
                    activities = json.loads(r.text)
                except:
                    self.check_amara_video_data()
                    activities = json.loads('{"meta":{"previous":null,"next":null,"offset":0,"limit":20,"total_count":0},"objects":[]}')
                url = activities["meta"]["next"]
                # Get the results for any language separate
                for any in activities["objects"]:
                    language = any["language"]
                    # Parse the date time string into a datetime object
                    timestamp = datetime.strptime(any["date"], '%Y-%m-%dT%H:%M:%SZ')
                    # Amara Timestamps are all in utc, they just don't know yet, so they need to be force told
                    timestamp = timestamp.replace(tzinfo = timezone.utc)
                    # Add the new key to the dictionary and only at insert set the timestamp
                    results.setdefault(language, timestamp)
                    # Keep the newest timestamp over all api queries
                    if results[language] < timestamp:
                        results[language] = timestamp
            #print(results)
            # check if subtitles are present and need new data..
            for any_language in results.keys():
                my_subtitles = Subtitle.objects.filter(talk = self, language__lang_amara_short = any_language)
                # Set flag for big query, this means a subtitle is missing because it was recently new added
                if my_subtitles.count() == 0:
                    # Set the big update flag
                    self.needs_complete_amara_update = True
                    my_language = Language.objects.get(lang_amara_short = any_language)
                    # Don't create a subtitle here, this will cause subtitles with revision = 0
                    #my_subtitle, created = Subtitle.objects.get_or_create(talk = self, language = my_language, last_changed_on_amara = results[any_language])
                    print("Talk id: ",self.id, " will get a new created subtitle")
                elif my_subtitles.count() == 1:
                    # Only proceed if the last activity has changed
                    # The copy is a dirty workaround because saving in my_subtitles[0] did not work!
                    my_subtitle = my_subtitles[0]
                    if my_subtitle.last_changed_on_amara < results[any_language]:
                        my_subtitle.last_changed_on_amara = results[any_language]
                        # Set the big update flag
                        self.needs_complete_amara_update = True
                        my_subtitle.save()
                        print("Talk id: ",self.id, "Subtitle id: ", my_subtitle.id, " new last changes:  ", my_subtitle.last_changed_on_amara  )
                else:
                    print("Something wrong with talk", self.id, self.title)
            # Save the timestamp of the start of the function as last checked activity on amara timestamp
            self.amara_activity_last_checked = start_timestamp
            self.next_amara_activity_check = start_timestamp + self.calculated_time_delta_for_activities
            self.save()

    # Check amara video-data
    @transaction.atomic
    def check_amara_video_data(self, force = False):
        start_timestamp = datetime.now(timezone.utc)
        # Only query amara if forced or flag is set
        if force or self.needs_complete_amara_update:
            url = "https://amara.org/api/videos/" + self.amara_key + "/languages/?format=json"
            import requests
            r = requests.get(url, headers = cred.AMARA_HEADER)
            activities = json.loads(r.text)
            for any_subtitle in activities["objects"]:
                print("Talk_ID:", self.id, "Amara_key:", self.amara_key)
                print("Language_code:", any_subtitle["language_code"])
                amara_subt_lang = any_subtitle["language_code"]
                print("is_primary_audio_language = is_original:", any_subtitle["is_primary_audio_language"])
                amara_subt_is_original = any_subtitle["is_primary_audio_language"]
                print("subtitles_complete:", any_subtitle["subtitles_complete"])
                amara_subt_is_complete = any_subtitle["subtitles_complete"]
                print("versions:", len(any_subtitle["versions"]))
                amara_subt_revision = len(any_subtitle["versions"])
                print("\n")
                # Only proceed if the revision on amara is higher than zero
                # Zero can exist if someone once clicked a language but didn't save anything
                if amara_subt_revision > 0:
                    # Get the right subtitle dataset or create it, only if the version is not null
                    my_language = Language.objects.get(lang_amara_short = amara_subt_lang)
                    my_subtitle, created = Subtitle.objects.get_or_create(talk = self, language = my_language)
                    # Proceed if the version on amara has changed
                    if my_subtitle.revision != amara_subt_revision:
                        # If the subtitle was not complete and is not complete
                        if not my_subtitle.complete and not amara_subt_is_complete:
                            # Just update the data
                            my_subtitle.is_original_lang = amara_subt_is_original
                            my_subtitle.revision = amara_subt_revision
                            my_subtitle.save()
                            # If this is an subtitle which is the original language
                            # and is in a state which has already statistics, also recalculate them
                            if my_subtitle.is_original_lang and my_subtitle.state_id == (5 or 6 or 7):
                                self.reset_related_statistics_data()
                        # If the subtitle was not complete but is complete now
                        elif not my_subtitle.complete and amara_subt_is_complete:
                            my_subtitle.complete = amara_subt_is_complete
                            my_subtitle.is_orignal_lang = amara_subt_is_original
                            my_subtitle.revision = amara_subt_revision
                            # This sets the sync flags and the tweet-flag and also lets the statistics to be recalculated
                            my_subtitle.set_complete(was_already_complete = False)
                            # If the talk also is in the original language, recalculate statistics
                            if my_subtitle.is_original_lang:
                                my_subtitle.talk.reset_related_statistics_data()
                            my_subtitle.save()
                        # If the subtitle was complete and is still complete
                        elif my_subtitle.complete and amara_subt_is_complete:
                            my_subtitle.complete = amara_subt_is_complete
                            my_subtitle.is_orignal_lang = amara_subt_is_original
                            my_subtitle.revision = amara_subt_revision
                            # This sets the sync flags and the tweet-flag and lets the statistics to be recalculated
                            my_subtitle.set_complete(was_already_complete = True)
                            # If the talk also is in the original language, recalculate statistics
                            if my_subtitle.is_original_lang:
                                my_subtitle.talk.reset_related_statistics_data()
                            my_subtitle.save()
                        # If the subtitle was complete but isn't any more
                        elif my_subtitle.complete and not amara_subt_is_complete:
                            my_subtitle.complete = amara_subt_is_complete
                            my_subtitle.is_orignal_lang = amara_subt_is_original
                            my_subtitle.revision = amara_subt_revision
                            # Resets the states and also the statistics if it is the original language
                            my_subtitle.reset_from_complete()
                            my_subtitle.save()

                    # If the revision hasn't changed but the complete flag has changed, set the subtitle complete
                    elif my_subtitle.complete and not amara_subt_is_complete:
                        my_subtitle.set_complete()
                        if my_subtitle.is_original_lang:
                            my_subtitle.talk.reset_related_statistics_data()
                    # Set the right state if the default is still active on "1"
                    if my_subtitle.state_id == 1 and my_subtitle.is_original_lang:
                        my_subtitle.state_id = 2
                        my_subtitle.save()
                    elif my_subtitle.state_id == 1 and not my_subtitle.is_original_lang:
                        my_subtitle.state_id = 11
                        my_subtitle.save()
            # Save the timestamp when this function was last used and reset the flag
            self.amara_complete_update_last_checked = start_timestamp
            self.needs_complete_amara_update = False
            self.save()


    def __str__(self):
        return self.title


# States for every subtitle like "complete" or "needs sync"
class States(BasisModell):
    state_de = models.CharField(max_length = 100)
    state_en = models.CharField(max_length = 100)
    def __str__(self):
        return self.state_en


# Infos to a subtitle in one language
class Subtitle(BasisModell):
    talk = models.ForeignKey(Talk)
    language = models.ForeignKey(Language)#, to_field = "lang_amara_short")
    is_original_lang = models.BooleanField(default = False, verbose_name='original language') # Read from Amara, not from the Fahrplan!
    revision = models.PositiveSmallIntegerField(default = 0)
    complete = models.BooleanField(default = False)
    state = models.ForeignKey(States, default = 1, blank = True)
    time_processed_transcribing = models.TimeField(default = "00:00", blank = True, verbose_name="")
    time_processed_syncing = models.TimeField(default = "00:00", blank = True, verbose_name="")
    time_quality_check_done = models.TimeField(default = "00:00", blank = True, verbose_name="")
    time_processed_translating = models.TimeField(default = "00:00", blank = True, verbose_name="")
    needs_automatic_syncing = models.BooleanField(default = False)
    blocked = models.BooleanField(default = False)
    needs_sync_to_ftp = models.BooleanField(default = False)
    needs_removal_from_ftp = models.BooleanField(default = False)
    tweet = models.BooleanField(default = False)
    needs_sync_to_YT = models.BooleanField(default = False)
    needs_removal_from_YT = models.BooleanField(default = False)
    tweet_autosync_done = models.BooleanField(default = False)
    #comment = models.TextField(default = "")
    last_changed_on_amara = models.DateTimeField(default = datetime.min, blank = True)
    yt_caption_id = models.CharField(max_length = 50, default = "", blank = True)
    blacklisted = models.BooleanField(default = False) # If syncs to the cdn, and media or YT should be blocked
    needs_sync_to_sync_folder = models.BooleanField(default = False)
    needs_removal_from_sync_folder = models.BooleanField(default = False)

    def _still_in_progress(self, timestamp, state, original_language=True):
        if original_language != self.is_original_lang:
            return False

        return ((timestamp < self.talk.video_duration) or
                (self.state_id == state and timestamp <= self.talk.video_duration))

    @property
    def transcription_in_progress(self):
        return self._still_in_progress(self.time_processed_transcribing, state=2)

    @property
    def syncing_in_progress(self):
        return self._still_in_progress(self.time_processed_syncing, state=5)

    @property
    def quality_check_in_progress(self):
        return self._still_in_progress(self.time_quality_check_done, state=7)

    @property
    def translation_in_progress(self):
        return self._still_in_progress(self.time_processed_translating, state=11, original_language=False)

    @property
    def language_short(self):
        # Workaround because of Klingon / Orignal
        lang = self.language.lang_short_srt
        return self.language.lang_short_srt

    # Get the filename for the fileservers
    def get_filename_srt(self):
        if self.talk.filename != "":
            filename = self.talk.filename + "." + self.language.lang_short_srt + ".srt"
            return filename
        else:
            return None

    # Return the transcript file with amara fails fixed
    def as_transcript(self, save = False):
        import re
        import requests
        # Create the url for the srt File
        # Only the srt-Version of all possible fileformats includes the "*" and "&"
        url = "https://www.amara.org/api2/partners/videos/" + self.talk.amara_key +"/languages/" + self.language.lang_amara_short + "/subtitles/?format=srt"
        # If this fails for any reason return None
        try:
        # No header necessary, this works without identification
            r = requests.get(url)
        except:
            return None
        srt_file =  r.text
        # Split the file at every double linebreak
        srt_file = srt_file.split("\r\n\r\n")
        transcript = ""
        for any_block in srt_file:
            # Split every textblock in its lines
            any_block = any_block.split("\r\n")
            line_counter = 2
            while line_counter < len(any_block):
                # Ignore empty subtitle lines
                if any_block[line_counter] != "":
                    transcript += any_block[line_counter] + "\n"
                line_counter += 1
            # Double line break after a complete block
            transcript += "\n"
        # Fix some amara fails
        transcript = re.sub("<i>", "*", transcript)
        transcript = re.sub("</i>", "*", transcript)
        transcript = re.sub("&amp;", "&", transcript)
        if save:
            filename = self.talk.slug+"." + self.language.lang_amara_short + ".transcript"
            folder = "./downloads/subtitle_transcript_files/"
            # Save File in ./downloads
            file = open(folder+filename,mode = "w",encoding = "utf-8")
            file.write(transcript)
            file.close()
        return transcript

    # Return the sbv_file with fixes (no fixes necessary, but "*" get lost)
    def as_sbv(self, save = False):
        import requests
        # Create the url for the sbv File
        url = "https://www.amara.org/api2/partners/videos/" + self.talk.amara_key +"/languages/" + self.language.lang_amara_short + "/subtitles/?format=sbv"
        # If this fails for any reason return None
        try:
        # No header necessary, this works without identification
            r = requests.get(url)
        except:
            return None
        sbv_file =  r.text
        if save:
            filename = self.talk.slug+"." + self.language.lang_amara_short + ".sbv"
            folder = "./downloads/subtitle_sbv_files/"
            # Save File in ./downloads
            file = open(folder+filename,mode = "w",encoding = "utf-8")
            file.write(sbv_file)
            file.close()
        return sbv_file

    # Return the srt_file with fixes
    def as_srt(self, save = False):
        import re
        import requests
        # Create the url for the srt File
        # Only the srt-Version of all possible fileformats includes the "*" and "&"
        url = "https://www.amara.org/api2/partners/videos/" + self.talk.amara_key +"/languages/" + self.language.lang_amara_short + "/subtitles/?format=srt"
        # If this fails for any reason return None
        try:
        # No header necessary, this works without identification
            r = requests.get(url)
        except:
            return None
        srt_file =  r.text
        # Fix some amara fails
        srt_file = re.sub("<i>", "*", srt_file)
        srt_file = re.sub("</i>", "*", srt_file)
        srt_file = re.sub("&amp;", "&", srt_file)
        if save:
            filename = self.talk.slug+"." + self.language.lang_amara_short + ".srt"
            folder = "./downloads/subtitle_srt_files/"
            # Save File in ./downloads
            file = open(folder+filename,mode = "w",encoding = "utf-8")
            file.write(srt_file)
            file.close()
        return srt_file

    # Saves Subtitles Files to the sync folder
    def sync_subtitle_to_sync_folder(self, force = False):
        # Sync the subtitle if it is not blacklisted and the sync flag is true of when it is forced
        if (not self.blacklisted and self.needs_sync_to_sync_folder) or force:
            import shutil
            # Download the subtitle as srt file
            self.as_srt(save = True)
            # Copy the subtitle to the right folder
            file_from = "/opt/subtitleStatus/downloads/subtitle_srt_files/" + self.talk.slug + "." + self.language.lang_amara_short + ".srt"
            file_to = "/opt/subtitleStatus/subtitles_sync_folder/" + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt()
            try:
                shutil.copy2(file_from, file_to)
            except:
                print("Exception")
                return False
            # Remove the sync flag and save
            self.needs_sync_to_sync_folder = False
            self.save()
            return True
        else:
            return False

    # Removes Subtitles Files from the sync folder
    def remove_subtitle_from_sync_folder(self, force = False):
        if self.needs_removal_from_sync_folder or force:
            file_name = "/opt/subtitleStatus/subtitles_sync_folder/" + self.talk.event.subfolder_in_sync_folder + "/" + self.get_filename_srt()
            import os
            try:
                os.remove(file_name)
            except:
                pass
            self.needs_removal_from_sync_folder = False
            self.save()

    # Set all flags for a sync to cdn, media frontend, YT ...
    def set_all_sync_flags(self, save = False):
        #self.needs_sync_to_ftp = True
        #self.needs_sync_to_media = True
        #self.needs_sync_to_YT = True
        self.needs_sync_to_sync_folder = True
        if save:
            self.save()

    # Set all flags for a removal from the cdn, media frontend, YT...
    def set_all_removal_flags(self, save = False):
        #self.needs_removal_from_ftp = True
        #self.needs_removal_from_media = True
        #self.needs_removal_from_YT = True
        self.needs_removal_from_sync_folder = True
        if save:
            self.save()

    # Set the subtitle complete
    @transaction.atomic
    def set_complete(self, was_already_complete = False):
        if self.is_original_lang:
            self.time_processed_transcribing = self.talk.video_duration
            self.time_processed_syncing = self.talk.video_duration
            self.time_quality_check_done = self.talk.video_duration
            self.state_id = 8
            # Let the related statistics data be recalculated
            self.talk.reset_related_statistics_data()
        else:
            self.time_processed_translating = self.talk.video_duration
            self.state_id = 12
        # Only tweet if the file was not already complete
        if not was_already_complete:
            self.tweet = True
        self.blocked = False
        self.set_all_sync_flags()
        self.needs_automatic_syncing = False
        self.save()

    # Reset subtitle if it was complete but it is not any more
    @transaction.atomic
    def reset_from_complete(self):
        self.time_processed_transcribing = "00:00:00"
        self.time_processed_syncing = "00:00:00"
        self.time_quality_check_done = "00:00:00"
        self.time_processed_translating = "00:00:00"
        if self.is_original_lang:
            self.state_id = 2
            # Hard reset for the related statistics data
            self.talk.reset_related_statistics_data(True)
        else:
            self.state_id = 11
        self.set_all_removal_flags()
        self.needs_automatic_syncing = False
        self.blocked = False
        self.save()

    # Set to autotiming in progress
    @transaction.atomic
    def set_to_autotiming_in_progress(self):
        # Stop if the subtitle is not the original language
        if not self.is_original_lang:
            return None
        needs_save = False
        if self.time_processed_transcribing != self.talk.video_duration:
            self.time_processed_transcribing = self.talk.video_duration
            needs_save = True
        if self.blocked == False:
            self.blocked = True
            needs_save = True
        if self.needs_automatic_syncing == False:
            self.needs_automatic_syncing = True
            needs_save = True
        if self.state_id != 4:
            self.state_id = 4
            needs_save = True
        if needs_save:
            self.save()
        return needs_save

# Links from the Fahrplan
class Links(BasisModell):
    talk = models.ForeignKey(Talk, blank = True)
    url = models.URLField(blank = True)
    title = models.CharField(max_length = 200, default = "Link title", blank = True)


# Statistics about Speakers and their words per minute and strokes per minute
# These datasets have to be collected by "hand", they can not be auto created
# speaker, talk, start and end need to be entered manually
class Statistics_Raw_Data(BasisModell):
    speaker = models.ForeignKey(Speaker)
    talk = models.ForeignKey(Talk)
    start = models.TimeField(blank = True, null = True)
    end = models.TimeField(blank = True, null = True)
    time_delta = models.FloatField(blank = True, null = True) # only seconds!
    words = models.IntegerField(blank = True, null = True)
    strokes = models.IntegerField(blank = True, null = True)
    recalculate_statistics = models.BooleanField(default = False)

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        # Only calculate if it is forced or if the recalculate flag
        # is set to true
        if force or self.recalculate_statistics:
            values = calculate_subtitle(self.talk, self.start, self.end)
            if values is not None:
                self.time_delta = values["time_delta"]
                self.words = values["words"]
                self.strokes = values["strokes"]
                self.recalculate_statistics = False
                self.save()
                # Set recalculate flags in the connected Statistics_Event module
                Talk.objects.filter(id = self.talk_id).update(recalculate_speakers_statistics = True)
                # Set recalculate flag in the connected Talk_Persons Statistics
                Talk_Persons.objects.filter(talk = self.talk, speaker = self.speaker).update(recalculate_statistics = True)
                # Set recalculate flag in the connected Statistics_Speaker module and also create the database entry
                # Get or create the related Statistics_Speaker database entry.
                # The necessary language is not the language of the talk but the language of the related is_orignal subtitle!
                this_speaker, created = Statistics_Speaker.objects.get_or_create(speaker = self.speaker, language = self.talk.language_of_original_subtitle)
                this_speaker.recalculate_statistics = True
                this_speaker.save()

            # Save the word frequencies into a json file
            if values["word_frequencies"] is not None and len(values["word_frequencies"]) > 0:
                save_word_dict_as_json(values["word_frequencies"],"statistics_raw_data", self.id)

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("statistics_raw_data", self.id)


# Speakers can have different Statistic values for different languages they spoke during talks
# This is calculated from the Statistics_Raw_Data which only counts the actual time the speaker speaks
# The subtitle must be finished or in review
class Statistics_Speaker(BasisModell):
    speaker = models.ForeignKey(Speaker)
    language = models.ForeignKey(Language)
    words = models.IntegerField(blank = True, null = True)      # All words from this speaker in this language summed up
    strokes = models.IntegerField(blank = True, null = True)    # All strokes from this speaker in this language summed up
    time_delta = models.FloatField(blank = True, null = True)   # Summed up time deltas from this speaker in this language
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from words and time delta
    average_spm = models.FloatField(blank = True, null = True)  # Caluclated from strokes and time_delta
    recalculate_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        # Recalculate absolutely everything
        if force or self.recalculate_statistics:
            # Empty dictionary for the word_frequencies
            word_freq = {}
            # All timeslots form Statistics_Raw_Data which has the same speaker and via the talk also the same language
            # All Subtitles which are the orignal language and the right language
            my_subtitles = Subtitle.objects.filter(is_original_lang = True, language = self.language)
            # Use temporary values
            words = strokes = time_delta = 0
            # Iterate over all these subtitles and get the right talk_id, then check if it has the right speaker
            for any in my_subtitles:
                talk_persons = Talk_Persons.objects.filter(speaker = self.speaker, talk = any.talk)
                # Just to be careful, first check if anything needs a recalculation first
                for any2 in talk_persons:
                    any2.recalculate()
                    # While looping over all connected talk_persons also add the word_frequencies up
                    word_freq = merge_word_frequencies_dicts(word_freq, any2.word_frequencies)
                # Only sum up if there is something to sum up
                if talk_persons.count() > 0:
                    # Do not add up if None
                    temp = talk_persons.aggregate(Sum("words"))["words__sum"]
                    if temp is not None:
                        words += temp
                    temp = talk_persons.aggregate(Sum("strokes"))["strokes__sum"]
                    if temp is not None:
                        strokes += temp
                    temp = talk_persons.aggregate(Sum("time_delta"))["time_delta__sum"]
                    if temp is not None:
                        time_delta += temp
            # If really everything was none:
            if (words or strokes or time_delta) is None:
                self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
            else:
                self.words = words
                self.strokes = strokes
                self.time_delta = time_delta
                self.average_wpm = calculate_per_minute(self.words, self.time_delta)
                self.average_spm = calculate_per_minute(self.strokes, self.time_delta)

            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq,"statistics_speaker", self.id)
                self.n_most_frequent_words = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
            else:
                self.n_most_frequent_words = "{}"
            self.recalculate_statistics = False
            self.save()

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("statistics_speaker", self.id)

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)


# Every Event can have different Statistic values for different languages
# The statistics applies to whole talk-time, not only the speakers time, it
# includes breaks, and Q&A and other stuff
class Statistics_Event(BasisModell):
    event = models.ForeignKey(Event)
    language = models.ForeignKey(Language)
    words = models.IntegerField(blank = True, null = True)  # Summed up from finished / in review whole talks, not only speakers time
    strokes = models.IntegerField(blank = True, null = True)    # Calculated from finished / in review whole talks, not only speakers time
    time_delta = models.FloatField(blank = True, null = True)   # Seconds of all talks from this event which are in review or finished
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from words and time_delta
    average_spm = models.FloatField(blank = True, null = True)  # Calculated from strokes and time_delta
    recalculate_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        if force or self.recalculate_statistics:
            # Find all Subtitles connected with this event and this language
            my_subtitles = Subtitle.objects.filter(talk__event = self.event, language = self.language, is_original_lang = True)
            # If nothing is found
            if my_subtitles.count() == 0:
                self.words = None
                self.strokes = None
                self.time_delta = None
                self.average_wpm = None
                self.average_spm = None
            else:
                self.words = my_subtitles.aggregate(Sum("talk__words"))["talk__words__sum"]
                self.strokes = my_subtitles.aggregate(Sum("talk__strokes"))["talk__strokes__sum"]
                self.time_delta = my_subtitles.aggregate(Sum("talk__time_delta"))["talk__time_delta__sum"]
                # If there is not really a finished subtitle in the language
                if (self.words or self.strokes or self.time_delta) is None:
                    self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
                else:
                    self.average_wpm = calculate_per_minute(self.words, self.time_delta)
                    self.average_spm = calculate_per_minute(self.strokes, self.time_delta)

            # Dictionary for the word freqiencies
            word_freq = {}
            # Merge all sub word_frequencies
            for any in my_subtitles:
                word_freq = merge_word_frequencies_dicts(any.talk.word_frequencies, word_freq)
            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq,"statistics_event", self.id)
                self.n_most_frequent_words = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
            else:
                self.n_most_frequent_words = "{}"
            self.recalculate_statistics = False
            self.save()

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("statistics_event", self.id)

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)

    @property
    def has_statistics(self):
        if self.average_wpm is not None and self.average_spm is not None:
            return True
        else:
            return False


# m:n Connection between Talks and Speakers and their Statistics data
class Talk_Persons(BasisModell):
    talk = models.ForeignKey(Talk)
    speaker = models.ForeignKey(Speaker)
    words = models.IntegerField(blank = True, null = True)      # All words from this speaker in this talk summed up
    strokes = models.IntegerField(blank = True, null = True)    # All strokes from this speaker in this talk summed up
    time_delta = models.FloatField(blank = True, null = True)   # Summed up time deltas from this speaker in this talk
    average_wpm = models.FloatField(blank = True, null = True)  # Calculated from words and time delta
    average_spm = models.FloatField(blank = True, null = True)  # Caluclated from strokes and time_delta
    recalculate_statistics = models.BooleanField(default = False)
    n_most_frequent_words = models.TextField(default = "{}")    # n most common words as json string

    # Recalculate statistics-data
    @transaction.atomic
    def recalculate(self, force = False):
        # Recalculate absolutely everything
        if force or self.recalculate_statistics:
            # Get statistics_raw for this speaker and this talk and sum it up
            raw_data = Statistics_Raw_Data.objects.filter(talk = self.talk, speaker = self.speaker)
            # If for some reason something needs a recalculation
            for any in raw_data:
                any.recalculate()
            if raw_data.count() == 0:
                self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
            else:
                self.words = raw_data.aggregate(Sum("words"))["words__sum"]
                self.strokes = raw_data.aggregate(Sum("strokes"))["strokes__sum"]
                self.time_delta = raw_data.aggregate(Sum("time_delta"))["time_delta__sum"]
                if (self.words or self.strokes or self.time_delta) is None:
                    self.words = self.strokes = self.time_delta = self.average_wpm = self.average_spm = None
                else:
                    self.average_wpm = calculate_per_minute(self.words, self.time_delta)
                    self.average_spm = calculate_per_minute(self.strokes, self.time_delta)

            # Dictionary for the word freqiencies
            word_freq = {}
            # Merge all sub word_frequencies
            for any in raw_data:
                word_freq = merge_word_frequencies_dicts(any.word_frequencies, word_freq)
            # Save the word frequencies into a json file
            if word_freq is not None and len(word_freq) > 0:
                save_word_dict_as_json(word_freq,"talk_persons", self.id)
                self.n_most_frequent_words = json.dumps(n_most_common_words(word_freq), ensure_ascii = False)
            else:
                self.n_most_frequent_words = "{}"
            self.recalculate_statistics = False
            self.save()

    # Return the word_frequencies as dictionary
    @property
    def word_frequencies(self):
        return read_word_dict_from_json("talk_persons", self.id)

    # Return the n most common words as dict
    @property
    def n_common_words(self):
        return json.loads(self.n_most_frequent_words)

    @property
    def has_statistics(self):
        if self.average_wpm is not None and self.average_spm is not None:
            return True
        else:
            return False
