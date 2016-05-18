from django.core.urlresolvers import reverse
from datetime import time
from .fixture import Fixture
from .. import views
from ..models import Subtitle, Talk


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
            response = self.client.get(
                reverse('event',
                        kwargs={
                            'acronym': self.event.acronym,
                            'day': day.index,
                        }))
            self.assertContains(response, talk.title)

    def testGetEventLanguage(self):
        for language, talk in zip(self.languages, self.talks):
            response = self.client.get(
                reverse('event',
                        kwargs={
                            'acronym': self.event.acronym,
                            'day': 0,
                            'language': language.lang_amara_short,
                        }))
            self.assertContains(response, talk.title)

    def testGetEventDayLanguage(self):
        response = self.client.get(
            reverse('event',
                    kwargs={
                        'acronym': self.event.acronym,
                        'day': self.days[0].index,
                        'language': self.languages[0].lang_amara_short,
                    }))
        self.assertContains(response, self.talks[0].title)
        self.assertNotContains(response, self.talks[1].title)

    def testGetEventFail(self):
        response = self.client.get(
            reverse('event', args=[self.event.acronym[1:]]))
        self.assertEqual(404, response.status_code)


class TalkViewTestCase(Fixture):
    def testGetTalkWithoutSubtitles(self):
        with self.assertTemplateUsed('talk.html'):
            with self.assertTemplateNotUsed('progress_bar_original.html'):
                with self.assertTemplateNotUsed('progress_bar_translation.html'):
                    response = self.client.get(
                        reverse('talk', args=[self.talks[0].id]))
        self.assertContains(response, self.talks[0].title)

    def testGetTalkWithSubtitle(self):
        with self.assertTemplateUsed('talk.html'):
            with self.assertTemplateUsed('progress_bar_original.html'):
                with self.assertTemplateNotUsed('progress_bar_translation.html'):
                    response = self.client.get(
                        reverse('talk', args=[self.talks[1].id]))
        self.assertContains(response, self.talks[1].title)

    def testGetTalkWithTranslation(self):
        with self.assertTemplateUsed('talk.html'):
            with self.assertTemplateUsed('progress_bar_original.html'):
                with self.assertTemplateUsed('progress_bar_translation.html'):
                    response = self.client.get(
                        reverse('talk', args=[self.talks[2].id]))
        self.assertContains(response, self.talks[2].title)
    def testGetTalkFail(self):
        response = self.client.get(
            reverse('talk', args=[self.talks[-1].id + 1]))
        self.assertEqual(404, response.status_code)

    def testGetTalkBlacklisted(self):
        talk = Talk.objects.filter(blacklisted=True).get()
        response = self.client.get(talk.get_absolute_url())
        self.assertEqual(404, response.status_code)

    def testGetTalkByFrabId(self):
        for talk in self.talks:
            response = self.client.get(
                reverse(views.talk_by_frab, args=[talk.frab_id_talk]))
            self.assertRedirects(response, talk.get_absolute_url(),
                                 status_code=301)

    def testGetTalkByGuid(self):
        for talk in self.talks:
            response = self.client.get(
                reverse(views.talk_by_guid, args=[talk.guid]))
            self.assertRedirects(response, talk.get_absolute_url(),
                                 status_code=301)


class SubtitleViewTestCase(Fixture):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.talk = cls.talks[1]

    def setUp(self):
        # create additional subtitles here so they don't persist between tests
        self.original = Subtitle.objects.create(talk=self.talk,
                                                language=self.languages[1],
                                                is_original_lang=True,
                                                revision=41,
                                                state=self.states[0])
        self.translation = Subtitle.objects.create(talk=self.talk,
                                                   language=self.languages[0],
                                                   is_original_lang=False,
                                                   revision=22,
                                                   state=self.states[0])

    def _form(self, subtitle):
        class MockRequest:
            POST = {'submit': 'save'}
        return views.get_subtitle_form(MockRequest(), self.talk, subtitle)

    def assertUpdated(self, response, subtitle):
        self.assertRedirects(response, subtitle.talk.get_absolute_url())
        self.assertNotContains(response, 'Step finished.')
        self.assertNotContains(response, 'You entered invalid data.')
        self.assertContains(response, 'Subtitle Status is saved.')

    def assertFinished(self, response, subtitle):
        self.assertRedirects(response, subtitle.talk.get_absolute_url())
        self.assertNotContains(response, 'You entered invalid data.')
        self.assertNotContains(response, 'Subtitle Status is saved.')
        self.assertContains(response, 'Step finished.')

    def assertInvalid(self, response, subtitle):
        self.assertRedirects(response, subtitle.talk.get_absolute_url())
        self.assertNotContains(response, 'Subtitle Status is saved.')
        self.assertNotContains(response, 'Step finished.')
        self.assertContains(response, 'You entered invalid data.')

    def testPostSubtitleNop(self):
        form = self._form(self.original)
        response = self.client.post(
            self.original.get_absolute_url(),
            form.data, follow=True)
        self.assertUpdated(response, self.original)

    def testPostSubtitle(self):
        form = self._form(self.original)
        form.data['time_processed_transcribing'] = time(minute=30)
        response = self.client.post(
            self.original.get_absolute_url(),
            form.data, follow=True)
        self.assertUpdated(response, self.original)
        self.original.refresh_from_db()
        self.assertEqual(self.original.time_processed_transcribing,
                         time(minute=30))
        self.assertEqual(self.original.state_id, 1)

    def testPostSubtitleExactLength(self):
        length=self.talk.video_duration
        form = self._form(self.original)
        form.data['time_processed_transcribing'] = length
        response = self.client.post(
            self.original.get_absolute_url(),
            form.data, follow=True)
        self.assertUpdated(response, self.original)
        self.original.refresh_from_db()
        self.assertEqual(self.original.time_processed_transcribing,
                         length)
        self.assertEqual(self.original.state_id, 1)

    def testPostSubtitleInvalid(self):
        form = self._form(self.original)
        form.data['time_processed_transcribing'] = time(hour=1)
        response = self.client.post(
            self.original.get_absolute_url(),
            form.data, follow=True)
        self.assertInvalid(response, self.original)

    def testGetSubtitleFail(self):
        url = reverse('subtitle', args=[self.translation.id + 1])
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)
        response = self.client.post(url)
        self.assertEqual(404, response.status_code)
