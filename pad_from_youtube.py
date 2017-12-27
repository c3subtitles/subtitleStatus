#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

import django
django.setup()
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from www.models import Talk, Language, Subtitle

def chunks(file):
    """Read `file`, splitting it at doubled linebreaks"""
    lines = []
    for line in file:
        lines.append(re.sub(' {2,}', ' ', line.strip()))
    return '\n'.join(lines).split('\n\n')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit("usage: ./{} transcript.sbv".format(sys.argv[0]))

    transcript = []
    try:
        with open(sys.argv[1], 'r') as file:
            transcript = chunks(file)
    except IOError as err:
        sys.exit("Transcript not readable: {}").format(err)

    out = ""

    for chunk in transcript:
        lines = chunk.split('\n')

        for line in lines[1:]:
            if line[0] == '[' and line[-1] == ']':
                 # keep this as a separate line
                 out += '\n' + line + '\n'
            else:
                 out += ' ' + line

    print(out)
