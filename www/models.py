from django.db import models

# Create your models here.

#Basis Modell damit jedes Feld einen Timestamp mit der letzten Änderung und der Erstellung hat
class BasisModell(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    touched = models.DateTimeField(auto_now = True)

    class Meta:
        abstract = True



# Event + dessen Daten
class Event(BasisModell):
    schedule_version = models.CharField(max_length = 50, default = "0.0")
    acronym = models.CharField(max_length = 20, default = "")
    title = models.CharField(max_length = 100, default = "No title yet")
    start = models.DateField(default = "1970-01-01")
    end = models.DateField(default = "1970-01-01")
    timeslot_duration = models.TimeField(default = "00:15")
    days = models.PositiveSmallIntegerField(default = 1)        
    schedule_xml_link = models.URLField()


    def isDifferent(id, xmlFile):
        with open("data/eventxml/{}.xml".format(id),'rb') as f:
            savedXML = f.read()
            return savedXML == xmlFile.data


# Tage die zu einem Event zugeordnet sind    
class Event_Days(BasisModell):
    event = models.ForeignKey(Event)
    index = models.PositiveSmallIntegerField(default = 0)
    date = models.DateField()
    day_start = models.DateTimeField()
    day_end = models.DateTimeField()

# Veranstaltungs "Räume" (kann auch draussen sein)
class Rooms(BasisModell):
    room = models.CharField(max_length = 30, default = "kein Raum")
    building = models.CharField(max_length = 30, default = "")

# Verschiedene Sprachen in verschiedenen Kodierungen sowie auf D und E ausgeschrieben
class Language(BasisModell):
    language_en = models.CharField(max_length = 40, default = "")
    language_de = models.CharField(max_length = 40, default = "") 
    lang_short_2 = models.CharField(max_length = 3, default = "", unique = True)
    lang_amara_short = models.CharField(max_length = 15, default = "", unique = True)
    lang_short_srt = models.CharField(max_length = 15,default = "")
    language_native = models.CharField(max_length = 40, default = "")
    amara_order = models.PositiveSmallIntegerField(default=0)

# Kategorie des Talks
class Tracks(BasisModell):
    track = models.CharField(max_length = 50, default = "")

# Präsentationsform des Talks
class Type_of(BasisModell):
    type = models.CharField(max_length = 20, default = "")

# Vortragender
class Speaker(BasisModell):
    frab_id = models.PositiveSmallIntegerField(default = -1)
    name = models.CharField(max_length = 50, default = "")

# Vortrag
class Talk(BasisModell):
    frab_id_talk = models.PositiveSmallIntegerField(default = -1)
    blacklisted = models.BooleanField(default=False)
    day = models.ForeignKey(Event_Days)
    room = models.ForeignKey(Rooms)
    link_to_logo = models.URLField(default = "")
    date = models.DateTimeField()
    start = models.TimeField()
    duration = models.TimeField()
    title = models.CharField(max_length = 50, default = "ohne Titel")
    subtitle_talk = models.CharField(max_length = 100, default = " ") # nicht UT sondern Ergänzung zum Titel
    track = models.ForeignKey(Tracks)
    event = models.ForeignKey(Event)
    type_of = models.ForeignKey(Type_of)
    orig_language = models.ForeignKey(Language)#,to_field = "lang_short_2") # aus dem Fahrplan
    abstract = models.TextField(default = "")
    description = models.TextField(default = "")
    persons = models.ManyToManyField(Speaker, default = None)
    pad_id = models.CharField(max_length = 30, default = "")
    link_to_writable_pad = models.URLField(default = "")
    link_to_readable_pad = models.URLField(default = "")
    link_to_video_file = models.URLField(default = "")
    amara_key = models.CharField(max_length = 20, default = "")
    youtube_key = models.CharField(max_length = 20)
    video_duration = models.TimeField()
    slug = models.SlugField(max_length = 200, default = "")

# Zustand des Untertitels oder dessen Pad
class States(BasisModell):
    state_de = models.CharField(max_length = 100)
    state_en = models.CharField(max_length = 100)

# Infos zu einem Untertitel in einer Sprache
class Subtitle(BasisModell):
    talk = models.ForeignKey(Talk)
    language = models.ForeignKey(Language)#, to_field = "lang_amara_short")
    is_original_lang = models.BooleanField(default = False) # aus Amara auslesen, nicht aus dem Fahrplan!
    revision = models.PositiveSmallIntegerField(default = 0)
    complete = models.BooleanField(default = False)
    state = models.ForeignKey(States, to_field = "id")
    time_processed_transcribing = models.TimeField(default = "00:00")
    time_processed_syncing = models.TimeField(default = "00:00")
    time_processed_translating = models.TimeField(default = "00:00")
    #comment = models.TextField(default = "")
    
# Links aus dem Fahrplan
class Links(BasisModell):
    talk = models.ForeignKey(Talk)
    talk_link_url = models.URLField()
    talk_link_title = models.CharField(max_length = 50, default = "Link title")   
