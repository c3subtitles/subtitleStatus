from django.core.urlresolvers import reverse
from .fixture import Fixture
from .. import views
from ..models import Talk

class OtherViewsTestCase(Fixture):
    def testGetHome(self):
        with self.assertTemplateUsed('base.html'):
            with self.assertTemplateUsed('main.html'):
                response = self.client.get(reverse(views.start))
        self.assertContains(response, self.event.title)

    def testGetClock(self):
        response = self.client.get(reverse(views.clock))
        self.assertContains(response, 'Hello, world!')


class EventViewTestCase(Fixture):
    def testGetEvent(self):
        with self.assertTemplateUsed('event.html'):
            with self.assertTemplateUsed('progress_bar_original.html'):
                response = self.client.get(self.event.get_absolute_url())
        self.assertContains(response, self.event.acronym)
        self.assertContains(response, self.event.title)

        for talk in self.talks:
            self.assertContains(response, talk.title)

    def testGetEventDay(self):
        for day, talk in zip(self.days, self.talks):
            response = self.client.get(reverse('event',
                                               kwargs={
                                                   'acronym': self.event.acronym,
                                                   'day': day.index,
                                               }))
            self.assertContains(response, talk.title)

    def testGetEventLanguage(self):
        for language, talk in zip(self.languages, self.talks):
            response = self.client.get(reverse('event',
                                               kwargs={
                                                   'acronym': self.event.acronym,
                                                   'day': 0,
                                                   'language': language.lang_amara_short,
                                               }))
            self.assertContains(response, talk.title)

    def testGetEventDayLanguage(self):
        response = self.client.get(reverse('event',
                                           kwargs={
                                               'acronym': self.event.acronym,
                                               'day': self.days[0].index,
                                               'language': self.languages[0].lang_amara_short,
                                           }))
        self.assertContains(response, self.talks[0].title)
        self.assertNotContains(response, self.talks[1].title)

    def testGetEventFail(self):
        response = self.client.get(reverse('event',
                                           args=[self.event.acronym[1:]]))
        self.assertEqual(404, response.status_code)


class TalkViewTestCase(Fixture):
    def testGetTalkWithoutSubtitles(self):
        with self.assertTemplateUsed('talk.html'):
            with self.assertTemplateNotUsed('progress_bar_original.html'):
                with self.assertTemplateNotUsed('progress_bar_translation.html'):
                    response = self.client.get(reverse('talk',
                                                       args=[self.talks[0].id]))
        self.assertContains(response, self.talks[0].title)

    def testGetTalkFail(self):
        response = self.client.get(reverse('talk',
                                           args=[self.talks[-1].id + 1]))
        self.assertEqual(404, response.status_code)

    def testGetTalkBlacklisted(self):
        talk = Talk.objects.filter(blacklisted=True).get()
        response = self.client.get(talk.get_absolute_url())
        self.assertEqual(404, response.status_code)

    def testGetTalkByFrabId(self):
        for talk in self.talks:
            response = self.client.get(reverse(views.talk_by_frab,
                                           args=[talk.frab_id_talk]))
            self.assertRedirects(response, talk.get_absolute_url(),
                                 status_code=301)

    def testGetTalkByGuid(self):
        for talk in self.talks:
            response = self.client.get(reverse(views.talk_by_guid,
                                               args=[talk.guid]))
            self.assertRedirects(response, talk.get_absolute_url(),
                                 status_code=301)
