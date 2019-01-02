from django.urls import reverse
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

    def _form(self, subtitle, finish=False):
        class MockRequest:
            if finish:
                POST = {'quick_finish_btn': 'finish'}
            else:
                POST = {'submit': 'save'}
        return views.get_subtitle_form(MockRequest(), self.talk, subtitle)

    def _advance(self, subtitle, steps=1):
        for _ in range(steps):
            if subtitle.state_id == self.STATE_AUTOTIMING:
                # this transition is normally triggered manually
                self.assertTrue(subtitle.is_original_lang)
                length = subtitle.talk.video_duration
                subtitle.time_processed_transcribing = length
                subtitle.time_processed_syncing = length
                subtitle.needs_automatic_syncing = False
                subtitle.blocked = False
                subtitle.state_id = self.STATE_REVIEWED_UNTIL
                subtitle.tweet_autosync_done = True
                subtitle.save()
            else:
                form = self._form(subtitle, finish=True)
                response = self.client.post(
                    subtitle.get_absolute_url(),
                    form.data, follow=True
                )
                self.assertFinished(response, subtitle)

                subtitle.refresh_from_db()
                if subtitle.state_id in [self.STATE_COMPLETE,
                                         self.STATE_TRANSLATED]:
                    # this is normally set by the amara import script
                    subtitle.complete = True
                    subtitle.save()
            subtitle.refresh_from_db()

    def _checkUpdate(self, subtitle,
                     finish=False,
                     timestamp=None,
                     oldState=Fixture.STATE_NONE,
                     newState=Fixture.STATE_NONE):
        self.assertEqual(subtitle.state_id, oldState)
        form = self._form(subtitle, finish)
        if timestamp:
            (k, v) = timestamp
            form.data[k] = v
        response = self.client.post(
            subtitle.get_absolute_url(),
            form.data, follow=True
        )

        if finish:
            self.assertFinished(response, subtitle)
        else:
            self.assertUpdated(response, subtitle)

        subtitle.refresh_from_db()
        self.assertEqual(subtitle.state_id, newState)
        null = time(0)
        length = subtitle.talk.video_duration
        self.assertTrue(null <= subtitle.time_processed_transcribing <= length)
        self.assertTrue(null <= subtitle.time_processed_syncing <= length)
        self.assertTrue(null <= subtitle.time_processed_translating <= length)
        self.assertTrue(null <= subtitle.time_quality_check_done <= length)

        if subtitle.is_original_lang:
            self.assertEqual(null, subtitle.time_processed_translating)
        else:
            self.assertEqual(null, subtitle.time_processed_transcribing)
            self.assertEqual(null, subtitle.time_processed_syncing)

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
        self._checkUpdate(self.original)

    def testPostSubtitle(self):
        self._checkUpdate(
            self.original,
            timestamp=('time_processed_transcribing', time(minute=30))
        )

    def testPostSubtitleStateTimedUntil(self):
        self.original.state_id = self.STATE_TIMED_UNTIL
        self.original.save()

        self._checkUpdate(
            self.original,
            timestamp=('time_processed_transcribing', time(minute=33)),
            oldState=self.STATE_TIMED_UNTIL,
            newState=self.STATE_TIMED_UNTIL
        )

    def testPostSubtitleFinishTranscribing(self):
        self._checkUpdate(
            self.original,
            finish=True,
            oldState=self.STATE_NONE,
            newState=self.STATE_AUTOTIMING
        )
        self.assertEqual(self.original.time_processed_transcribing,
                         self.original.talk.video_duration)

    def testPostSubtitleFinishTranscribingFromTimedUntil(self):
        self.original.state_id = self.STATE_TIMED_UNTIL
        self.original.save()

        self._checkUpdate(
            self.original,
            finish=True,
            oldState=self.STATE_TIMED_UNTIL,
            newState=self.STATE_AUTOTIMING
        )
        self.assertEqual(self.original.time_processed_transcribing,
                         self.original.talk.video_duration)

    def testSubtitleFormNative(self):
        form = self._form(self.original)
        self.assertEqual(['time_processed_transcribing'],
                         list(form.fields.keys()))

    def testSubtitleFormInAutotiming(self):
        self._advance(self.original)
        self.assertEqual(self._form(self.original),
                         'Automatic syncing, please wait and come back later!')

    def testSubtitleFormFinished(self):
        self._advance(self.original, steps=3)
        self.assertEqual(self._form(self.original),
                         'Finished :)')
        self._advance(self.translation)
        self.assertEqual(self._form(self.translation),
                         'Finished :)')

    def testPostSubtitleExactLength(self):
        self._checkUpdate(
            self.original,
            timestamp=('time_processed_transcribing', self.talk.video_duration),
        )

    def testPostSubtitleInvalid(self):
        tv = time(hour=1)
        self.assertTrue(tv > self.talk.video_duration)

        for ts in ['time_processed_transcribing',
                   'time_processed_syncing',
                   'time_processed_translating',
                   'time_quality_check_done']:
            form = self._form(self.original)
            form.data[ts] = tv
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
