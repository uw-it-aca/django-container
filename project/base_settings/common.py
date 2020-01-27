from django.core.management.utils import get_random_secret_key
import os
import sys
import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


if os.getenv('ENV', 'localdev') == 'localdev':
    SECRET_KEY = os.getenv('DJANGO_SECRET', get_random_secret_key())
else:
    SECRET_KEY = os.getenv('DJANGO_SECRET', None)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.PersistentRemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.RemoteUserBackend',
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Los_Angeles'

USE_I18N = True
USE_L10N = True
USE_TZ = True

ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'

if os.getenv('DB', 'sqlite3') == 'sqlite3':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
elif os.getenv('DB', 'sqlite3') == 'mysql':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.getenv('DATABASE_HOSTNAME', 'localhost'),
            'NAME': os.getenv('DATABASE_DB_NAME', 'db'),
            'USER': os.getenv('DATABASE_USERNAME', None),
            'PASSWORD': os.getenv('DATABASE_PASSWORD', None),
        }
    }
elif os.getenv('DB', 'sqlite3') == 'postgres':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.getenv('DATABASE_HOSTNAME', 'localhost'),
            'NAME': os.getenv('DATABASE_DB_NAME', 'db'),
            'USER': os.getenv('DATABASE_USERNAME', None),
            'PASSWORD': os.getenv('DATABASE_PASSWORD', None),
        }
    }

if os.getenv('CACHE', '') == 'memcached':
    RESTCLIENTS_DAO_CACHE_CLASS = 'myuw.util.cache_implementation.MyUWMemcachedCache'
    RESTCLIENTS_MEMCACHED_SERVERS = (
        os.getenv('CACHE_NODE_0', '') + ':' + os.getenv('CACHE_PORT', '11211'),
        os.getenv('CACHE_NODE_1', '') + ':' + os.getenv('CACHE_PORT', '11211'),
    )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATIC_ROOT = '/static/'
STATIC_URL = '/static/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'debug':  True,
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }
    }
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'stdout_stream': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno < logging.WARN
        },
        'stderr_stream': {
            '()': 'django.utils.log.CallbackFilter',
            'callback': lambda record: record.levelno > logging.INFO
        }
    },
    'formatters': {
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'filters': ['stdout_stream']
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
            'filters': ['stderr_stream']
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout', 'stderr'],
            'level': 'INFO' if os.getenv('ENV', 'dev') == 'prod' else 'DEBUG'
        }
    }
}
