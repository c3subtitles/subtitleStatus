from django.test import TestCase
from www.models import Event, Event_Days, Language, Rooms, Tracks, Type_of, Talk, Subtitle


class Fixture(TestCase):
    """basic test fixture
    """
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(acronym='foo',
                                         title='bar event name',
                                         days=3)
        cls.type_of = Type_of.objects.create(type='quux')
        cls.track = Tracks.objects.create(track='test track')
        cls.room = Rooms.objects.create()

        cls.days = []
        for day in range(cls.event.days):
            cls.days.append(Event_Days.objects.create(event=cls.event,
                                                      index=day + 1))

        cls.languages = []
        for language in ['en', 'de']:
            cls.languages.append(Language.objects.create(lang_amara_short=language,
                                                         language_en=language,
                                                         language_de=language))

        cls.talks = []
        for day in cls.days:
            language = cls.languages[0 if day.index == 1 else 1]
            cls.talks.append(Talk.objects.create(day=day,
                                                 room=cls.room,
                                                 title=('talk %d' % day.index),
                                                 track=cls.track,
                                                 event=cls.event,
                                                 type_of=cls.type_of,
                                                 orig_language=language,
                                                 frab_id_talk=23 + day.index,
                                                 guid='talk-42_%d' % day.index))
        Talk.objects.create(day=cls.days[0],
                            room=cls.room,
                            title='blacklisted talk',
                            track=cls.track,
                            event=cls.event,
                            type_of=cls.type_of,
                            orig_language=cls.languages[0],
                            blacklisted=True,
                            frab_id_talk=22,
                            guid='talk-22')

        cls.subtitles = []
        for day in cls.days[1:]:
            talk = Talk.objects.filter(day=day).get()
            cls.subtitles.append(Subtitle.objects.create(talk=talk,
                                                         language=talk.orig_language,
                                                         is_original_lang=True))
            if len(cls.subtitles) > 1:
                cls.subtitles.append(
                    Subtitle.objects.create(talk=talk,
                                            language=cls.languages[0],
                                            is_original_lang=False))
