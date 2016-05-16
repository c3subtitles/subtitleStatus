from django.test import TestCase, Client
from www.models import Event

class EventViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = Event.objects.create(acronym='foo',
                                         title='bar event name')

    def testGetHome(self):
        response = self.client.get('/')
        self.assertContains(response, self.event.title)

    def testGetEvent(self):
        response = self.client.get('/event/%s/' % self.event.acronym)
        self.assertContains(response, self.event.acronym)
        self.assertContains(response, self.event.title)
