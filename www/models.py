# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.

#Basis Modell damit jedes Feld einen Timestamp mit der letzten Änderung und der Erstellung hat
class BasisModell(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    touched = models.DateTimeField(auto_now = True)

    class Meta:
        abstract = True


# Pro Event welche Unterordner auf dem FTP Subtitles bekommen und wie darin das File-Format der Videos heißt
class Folders_Extensions(BasisModell):
    subfolder = models.CharField(max_length = 10, default = "", blank = True)
    file_extension = models.CharField(max_length = 10, default = "", blank = True)        

    def __str__(self):
        return self.subfolder+","+self.file_extension

    
# Event + dessen Daten
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
    
    def isDifferent(id, xmlFile):
        with open("data/eventxml/{}.xml".format(id),'rb') as f:
            savedXML = f.read()
            return savedXML == xmlFile.data


# Tage die zu einem Event zugeordnet sind
class Event_Days(BasisModell):
    event = models.ForeignKey(Event)
    index = models.PositiveSmallIntegerField(default = 0)
    date = models.DateField(default = "1970-01-01", blank = True)
    day_start = models.DateTimeField(default = "1970-01-01 00:00", blank = True)
    day_end = models.DateTimeField(default = "1970-01-01 00:00", blank = True)

# Veranstaltungs "Räume" (kann auch draussen sein)
class Rooms(BasisModell):
    room = models.CharField(max_length = 30, default = "kein Raum")
    building = models.CharField(max_length = 30, default = "")

    def __str__(self):
        return self.room

# Verschiedene Sprachen in verschiedenen Kodierungen sowie auf D und E ausgeschrieben
class Language(BasisModell):
    language_en = models.CharField(max_length = 40, default = "")
    language_de = models.CharField(max_length = 40, default = "", blank = True)
    lang_short_2 = models.CharField(max_length = 3, default = "", blank = True)#, unique = True)
    lang_amara_short = models.CharField(max_length = 15, default = "", unique = True)
    lang_short_srt = models.CharField(max_length = 15,default = "", blank = True)
    language_native = models.CharField(max_length = 40, default = "", blank = True)
    amara_order = models.PositiveSmallIntegerField(default=0, blank = True)

    def __str__(self):
        return self.lang_amara_short

# Kategorie des Talks
class Tracks(BasisModell):
    track = models.CharField(max_length = 50, default = "")

    def __str__(self):
        return self.track

# Präsentationsform des Talks
class Type_of(BasisModell):
    type = models.CharField(max_length = 20, default = "")

    def __str__(self):
        return self.type

# Vortragender
class Speaker(BasisModell):
    frab_id = models.PositiveSmallIntegerField(default = -1)
    name = models.CharField(max_length = 50, default = "")

# Vortrag
class Talk(BasisModell):
    frab_id_talk = models.PositiveSmallIntegerField(default = -1)
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
    persons = models.ManyToManyField(Speaker, default = None, blank = True)
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

    @property
    def needs_automatic_syncing(self):
        return self.subtitle_set.filter(needs_automatic_syncing=True).count() > 0

# Zustand des Untertitels oder dessen Pad
class States(BasisModell):
    state_de = models.CharField(max_length = 100)
    state_en = models.CharField(max_length = 100)
    def __str__(self):
        return self.state_en

# Infos zu einem Untertitel in einer Sprache
class Subtitle(BasisModell):
    talk = models.ForeignKey(Talk)
    language = models.ForeignKey(Language)#, to_field = "lang_amara_short")
    is_original_lang = models.BooleanField(default = False) # aus Amara auslesen, nicht aus dem Fahrplan!
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
    #comment = models.TextField(default = "")

    @property
    def transcription_in_progress(self):
        return self.is_original_lang and (self.time_processed_transcribing <
                                          self.talk.video_duration)

# Links aus dem Fahrplan
class Links(BasisModell):
    talk = models.ForeignKey(Talk, blank = True)
    url = models.URLField(blank = True)
    title = models.CharField(max_length = 200, default = "Link title", blank = True)