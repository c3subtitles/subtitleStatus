from django.contrib import admin
from www.models import Talk
from www.models import Tracks
from www.models import Links
from www.models import Type_of
from www.models import Speaker
from www.models import Speaker_Links
from www.models import Subtitle
from www.models import States
from www.models import Event
from www.models import Event_Days
from www.models import Rooms
from www.models import Language


# Register your models here.
admin.site.register(Talk)
admin.site.register(Tracks)
admin.site.register(Links)
admin.site.register(Type_of)
admin.site.register(Speaker)
admin.site.register(Speaker_Links)
admin.site.register(Subtitle)
admin.site.register(States)
admin.site.register(Event)
admin.site.register(Event_Days)
admin.site.register(Rooms)
admin.site.register(Language)
