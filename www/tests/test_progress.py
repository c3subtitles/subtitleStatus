from math import fsum
from .fixture import Fixture
from ..views import progress_bar_for_talks

class ProgressBarTestCase(Fixture):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.talks = cls.event.talk_set.filter(blacklisted=False)

    def _check_bar(self, bar):
        total = fsum(bar.values())
        self.assertAlmostEqual(total, 100)

        for value in bar.values():
            self.assertTrue(0 <= value <= 100)

    def _check_talks(self, talks):
        self._check_bar(progress_bar_for_talks(talks))

    def testTotal(self):
        self._check_talks(self.talks)

    def testTotalDay(self):
        for day in self.days:
            self._check_talks(self.talks.filter(day=day))

    def testTotalLanguage(self):
        for language in self.languages:
            self._check_talks(self.talks.filter(orig_language=language))

    def testTotalDayLanguage(self):
        for day in self.days:
            for language in self.languages:
                self._check_talks(self.talks.filter(day=day,
                                                    orig_language=language))
