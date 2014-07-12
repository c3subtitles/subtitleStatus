from django.db import models

# Create your models here.

#Basis Modell damit jedes Feld einen Timestamp mit der letzten Änderung und der Erstellung hat
class BasisModell(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    touched = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True



# Event + dessen Daten
class Event(BasisModell):
    schedule_version = models.CharField(max_length = 50, default = "0.0")
    title = models.CharField(max_length = 100, default = "No title yet")
    start = models.DateField()#default = "01.01.1970")
    end = models.DateField()#default = "01.01.1970")
    timeslot_duration = models.TimeField()#default = "0:15")
    days = models.PositiveSmallIntegerField(default = 1)        
    schedule_xml = models.BinaryField()
    schedule_xml_link = models.URLField()

# Tage die zu einem Event zugeordnet sind    
class Event_Days(BasisModell):
    event = models.ForeignKey(Event, related_name = "corresponding_event")
    index = models.PositiveSmallIntegerField(default = 0)
    date = models.DateField()#default = "01.01.1970")
    day_start = models.DateTimeField()#default = "00:00 01.01.1970")
    day_end = models.DateTimeField()#default = "23:50 01.01.1970")

# Veranstaltungs "Räume" (kann auch draussen sein)
class Rooms(BasisModell):
    room = models.CharField(max_length = 30, default = "kein Raum")
    building = models.CharField(max_length = 30, default = "")

# Verschiedene Sprachen in verschiedenen Kodierungen sowie auf D und E ausgeschrieben
class Language(BasisModell):
    language_en = models.CharField(max_length = 40, default = "")
    language_de = models.CharField(max_length = 40, default = "") 
    lang_short_2 = models.CharField(max_length = 3, default = "", unique = True)
    lang_unisubs_short = models.CharField(max_length = 3, default = "", unique = True)
    lang_short_srt = models.CharField(max_length = 5, default = "")

# Kategorie des Talks
class Tracks(BasisModell):
    track = models.CharField(max_length = 20, default = "")

# Präsentationsform des Talks
class Type_of(BasisModell):
    type_of_talk = models.CharField(max_length = 20, default = "")

# Vortragender
class Speaker(BasisModell):
    name = models.CharField(max_length = 30, default = "")

# Vortrag
class Talk(BasisModell):
    frab_id = models.PositiveSmallIntegerField(default = -1)
    blacklisted = models.BooleanField(default=False)
    day = models.ForeignKey(Event_Days)
    room = models.ForeignKey(Rooms)
    link_to_logo = models.URLField(default = "")
    date = models.DateTimeField()#default = "01.01.1970 00:00")
    start = models.TimeField()#default = "00:00")
    duration = models.TimeField()#default = "00:00")
    title = models.CharField(max_length = 50, default = "ohne Titel")
    subtitle_talk = models.CharField(max_length = 100, default = " ") # nicht UT sondern Ergänzung zum Titel
    track = models.ForeignKey(Tracks)
    event = models.ForeignKey(Event)
    type_of = models.ForeignKey(Type_of)
    orig_language = models.ForeignKey(Language,to_field = "lang_short_2")
    abstract = models.TextField(default = "")
    description = models.TextField(default = "")
    persons = models.ManyToManyField(Speaker, default = None)
    pad_id = models.CharField(max_length = 30, default = "")
    link_to_writable_pad = models.URLField(default = "")
    link_to_readable_pad = models.URLField(default = "")
    link_to_video_file = models.URLField(default = "")
    unisubs_id = models.CharField(max_length = 20, default = "")
    live_subs_available = models.NullBooleanField(default = None)
    live_subs_in_pad = models.BooleanField(default=True)

# Zustand des Untertitles oder dessen Pad
class States(BasisModell):
    state = models.CharField(max_length = 100)

# Infos zu einem Untertitel in einer Sprache
class Subtitle(BasisModell):
    talk = models.ForeignKey(Talk, related_name = "corresponding_talk")
    language = models.ForeignKey(Language, to_field = "lang_unisubs_short")
    revision = models.PositiveSmallIntegerField(default = 0)
    complete = models.BooleanField(default = False)
    state = models.ForeignKey(States, related_name = "corresponding_state", to_field = "id")
    comment = models.TextField(default = "")
    sub_srt_file = models.BinaryField()
    
# Links aus dem Fahrplan
class Links(BasisModell):
    talk = models.ForeignKey(Talk)
    url = models.URLField()
    title = models.CharField(max_length = 50, default = "Link title")   
