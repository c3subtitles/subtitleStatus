#!/usr/bin/env python3

import os
import sys
import lxml

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

import www.models as models

print ("Hallo Welt")

