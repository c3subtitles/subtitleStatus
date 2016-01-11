#!/bin/sh

python manage.py migrate
python manage.py set_default_site --name localhost --domain localhost:8000
python manage.py createsuperuser --username admin --email root@localhost
python manage.py loaddata 32c3
python import_languages.py
python update_events_xml_schedule_import.py
