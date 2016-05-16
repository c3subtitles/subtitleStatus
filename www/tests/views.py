from .fixture import Fixture


class OtherViewsTestCase(Fixture):
    def testGetHome(self):
        response = self.client.get('/')
        self.assertContains(response, self.event.title)

    def testGetClock(self):
        response = self.client.get('/hello/')
        self.assertContains(response, 'Hello, world!')


class EventViewTestCase(Fixture):
    def testGetEvent(self):
        response = self.client.get('/event/%s/' % self.event.acronym)
        self.assertContains(response, self.event.acronym)
        self.assertContains(response, self.event.title)

        for talk in self.talks:
            self.assertContains(response, talk.title)

    def testGetEventDay(self):
        for day, talk in zip(self.days, self.talks):
            response = self.client.get('/event/%s/day/%d' %
                                       (self.event.acronym,
                                        day.index))
            self.assertContains(response, talk.title)

    def testGetEventLanguage(self):
        for language, talk in zip(self.languages, self.talks):
            response = self.client.get('/event/%s/day/0/lang/%s' %
                                       (self.event.acronym,
                                        language.lang_amara_short))
            self.assertContains(response, talk.title)

    def testGetEventDayLanguage(self):
        response = self.client.get('/event/%s/day/%d/lang/%s' %
                                   (self.event.acronym,
                                    self.days[0].index,
                                    self.languages[0].lang_amara_short))
        self.assertContains(response, self.talks[0].title)
        self.assertNotContains(response, self.talks[1].title)
