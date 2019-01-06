from django.test import TestCase
from datetime import time


from www.models import Event, Event_Days, Language, Rooms, Tracks, Type_of, Talk, Subtitle, States, Transcript
from .factories import EventFactory, TrackFactory, TypeOfFactory, StateFactory, RoomFactory


class Fixture(TestCase):
    """basic test fixture
    """
    STATE_NONE = 1
    STATE_TRANSCRIBED_UNTIL = 2
    STATE_TRANSCRIBED = 3
    STATE_AUTOTIMING = 4
    STATE_TIMED_UNTIL = 5
    STATE_TIMED = 6
    STATE_REVIEWED_UNTIL = 7
    STATE_COMPLETE = 8
    STATE_UNKNOWN = 9
    STATE_TRANSLATED_UNTIL = 11
    STATE_TRANSLATED = 12

    @classmethod
    def setUpTestData(cls):
        cls.states = [StateFactory(__sequence=state)
                      for state in range(1, 13)]

        cls.event = EventFactory()
        cls.type_of = TypeOfFactory()
        cls.track = TrackFactory()
        cls.room = RoomFactory()
        cls.days = Event_Days.objects.filter(event=cls.event)

        cls.languages = []
        for language in ['en', 'de']:
            cls.languages.append(Language.objects.create(lang_amara_short=language,
                                                         language_en=language,
                                                         language_de=language))

        cls.transcripts = []
        for creator in ['trint', 'youtube']:
            cls.transcripts.append(Transcript.objects.create(creator=creator))

        cls.talks = []
        for day in cls.days:
            if day.index == 1:
                language = cls.languages[0]
                length = time(0)
                creator = cls.transcripts[0]
            else:
                language = cls.languages[1]
                length = time(minute=45)
                creator = cls.transcripts[1]
            cls.talks.append(Talk.objects.create(day=day,
                                                 room=cls.room,
                                                 title=('talk %d' % day.index),
                                                 track=cls.track,
                                                 event=cls.event,
                                                 type_of=cls.type_of,
                                                 orig_language=language,
                                                 frab_id_talk=23 + day.index,
                                                 guid='talk-42_%d' % day.index,
                                                 transcript_by=creator,
                                                 video_duration=length))
        Talk.objects.create(day=cls.days[0],
                            room=cls.room,
                            title='blacklisted talk',
                            track=cls.track,
                            event=cls.event,
                            type_of=cls.type_of,
                            orig_language=cls.languages[0],
                            blacklisted=True,
                            frab_id_talk=22,
                            transcript_by=creator,
                            guid='talk-22')

        cls.subtitles = []
        for day in cls.days[1:]:
            talk = Talk.objects.filter(day=day).get()
            cls.subtitles.append(Subtitle.objects.create(talk=talk,
                                                         language=talk.orig_language,
                                                         is_original_lang=True,
                                                         state=cls.states[0]))
            if len(cls.subtitles) > 1:
                cls.subtitles.append(
                    Subtitle.objects.create(talk=talk,
                                            language=cls.languages[0],
                                            is_original_lang=False,
                                            state=cls.states[0]))
