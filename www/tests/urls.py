from django.core.urlresolvers import reverse
from django.test import TestCase
from .. import views

class UrlStabilityTestCase(TestCase):
    """Test to ensure that public URLs don't change (so we can use
    reverse() in all the other test cases).
    """

    def assertUrlIsStable(self, url, viewname, *args, **kwargs):
        self.assertEqual(url, reverse(viewname, args=args, kwargs=kwargs))

    def testHomeUrl(self):
        self.assertUrlIsStable('/', 'home')

    def testClockUrl(self):
        self.assertUrlIsStable('/clock/', views.clock)

    def testEventUrl(self):
        self.assertUrlIsStable('/event/test/',
                               'event', acronym='test')
        self.assertUrlIsStable('/event/test/day/1',
                               'event', acronym='test', day=1)
        self.assertUrlIsStable('/event/test/day/1/lang/foo',
                               'event', acronym='test', day=1, language='foo')

    def testTalkUrl(self):
        self.assertUrlIsStable('/talk/23/',
                               'talk', id=23)
        self.assertUrlIsStable('/talk/frab-id/42/',
                               views.talk_by_frab, frab_id=42)
        self.assertUrlIsStable('/talk/guid/ABC-zyx-2342_/',
                               views.talk_by_guid, guid='ABC-zyx-2342_')

    def testSubtitleUrl(self):
        self.assertUrlIsStable('/subtitle/423/',
                               'subtitle', id=423)
