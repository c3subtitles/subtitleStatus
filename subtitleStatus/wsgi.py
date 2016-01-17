"""
WSGI config for wwwsubs project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import uwsgi
from uwsgidecorators import timer
from django.utils import autoreload

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "subtitleStatus.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()


@timer(3)
def autoreload_on_code_change(_):
    if autoreload.code_changed():
        uwsgi.reload()
