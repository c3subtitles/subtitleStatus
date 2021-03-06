import os
from collections import namedtuple
from contextlib import contextmanager
from django.test import TestCase
from .fixture import fixture_file, fixture_sets
from .. import transforms


@contextmanager
def timing_input(name):
    Fixture = namedtuple('Fixture', ['pad', 'transcript'])

    with fixture_file(name, "pad.txt") as pad:
        with fixture_file(name, "transcript.txt") as transcript:
            yield Fixture(pad, transcript)


@contextmanager
def sbv_alignment_input(name):
    Fixture = namedtuple('Fixture', ['transcript', 'youtube', 'result'], defaults=(None,))

    with fixture_file(name, "transcript.txt") as transcript:
        with fixture_file(name, "youtube.sbv") as youtube:
            result = None
            try:
                with fixture_file(name, "result.sbv") as res:
                    result = res
            except FileNotFoundError:
                pass
            yield Fixture(transcript, youtube, result)


class TransformsTestCase(TestCase):
    """Test to ensure correctness of transcript transforms."""

    def testPadToTiming(self):
        for fixture_name in fixture_sets("transforms", "timing"):
            with self.subTest(fixture=fixture_name):
                with timing_input(fixture_name) as fixture:
                    result = transforms.timing_from_pad(fixture.pad)
                    self.assertIsNotNone(result)
                    self.maxDiff = None
                    self.assertEqual(transforms.normalise(fixture.transcript), transforms.normalise(result))

    def testSbvAlignment(self):
        for fixture_name in fixture_sets("transforms", "sbv-align"):
            with self.subTest(fixture=fixture_name):
                with sbv_alignment_input(fixture_name) as fixture:
                    result = transforms.align_transcript_sbv(fixture.transcript, fixture.youtube)
                    self.assertIsNotNone(result)

                    if fixture.result is not None:
                        self.assertEqual(transforms.normalise(fixture.result), result)
