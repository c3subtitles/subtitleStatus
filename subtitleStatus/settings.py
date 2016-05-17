"""
Django settings for wwwsubs project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import string
from django.utils.crypto import get_random_string

SITE_ID = 1
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = BASE_DIR

TEMPLATES = [
    {'BACKEND': 'django.template.backends.django.DjangoTemplates',
     'APP_DIRS': True,
     'OPTIONS': {'debug': False,
                 'context_processors': [
                     'django.contrib.auth.context_processors.auth',
                     'django.template.context_processors.debug',
                     'django.template.context_processors.i18n',
                     'django.template.context_processors.media',
                     'django.template.context_processors.static',
                     'django.template.context_processors.tz',
                     'django.contrib.messages.context_processors.messages',
                ],
     },
    },
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
if config.has_option('django', 'secret'):
    SECRET_KEY = config.get('django', 'secret')
else:
    SECRET_FILE = os.path.join(os.path.dirname(__file__), '.secret')
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, 'r') as f:
            SECRET_KEY = f.read().strip()
    else:
        SECRET_KEY = get_random_string(50, string.printable)
        with open(SECRET_FILE, 'w') as f:
            os.chmod(SECRET_FILE, 0o600)
            os.chown(SECRET_FILE, os.getuid(), os.getgid())
            f.write(SECRET_KEY)

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True
DEBUG = False

TEMPLATE_DEBUG = False
#TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['subtitles.media.ccc.de', 'c3subtitles.de', 'c3subtitles.ext.selfnet.de']

# Redirect after login
LOGIN_REDIRECT_URL = '/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'bootstrapform',
    'account',
    'www',
    'django_extensions',
    'subtitleStatus',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'subtitleStatus.urls'

WSGI_APPLICATION = 'subtitleStatus.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {}

# database configuration from config file
if config.get('sql', 'type', fallback='sqlite').lower() == 'sqlite':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'subtitlestatus.sqlite3'),
    }
elif config.get('sql', 'type').lower() == 'postgresql':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config.get('sql', 'database'),
        'USER': config.get('sql', 'user', fallback=''),
        'PASSWORD': config.get('sql', 'password', fallback=''),
        'HOST': config.get('sql', 'host', fallback=''),
        'PORT': config.get('sql', 'port', fallback='')
    }
elif config.get('sql', 'type').lower() == 'mysql':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config.get('sql', 'database'),
        'USER': config.get('sql', 'user'),
        'PASSWORD': config.get('sql', 'password'),
        'HOST': config.get('sql', 'host', fallback=''),
        'PORT': config.get('sql', 'port', fallback='')
    }
else:
    raise ValueError('invalid database type "%s"' % config.get('sql', 'type').lower())

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static/")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'django': {
            'handlers' : ['console'],
            'level' : 'WARNING'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'filters': None,
            'level': 'WARNING',
        }
    }
}

try:
    from .local_settings import *
except ImportError:
    pass
