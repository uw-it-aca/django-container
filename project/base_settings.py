from django.core.management.utils import get_random_secret_key
import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(__file__))


if os.getenv('ENV', 'localdev') == "localdev":
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

if os.getenv('CACHE', 'none') == 'memcached':
    RESTCLIENTS_DAO_CACHE_CLASS='myuw.util.cache_implementation.MyUWMemcachedCache'
    RESTCLIENTS_MEMCACHED_SERVERS = (os.getenv('CACHE_NODE_0', '') + ':' + os.getenv('CACHE_PORT', '11211'), os.getenv('CACHE_NODE_1', '') + ':' + os.getenv('CACHE_PORT', '11211'),)



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
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
    },
    'handlers': {
        'stdout': {
            'level':'INFO',
            'class':'logging.StreamHandler',
            'stream': sys.stdout
        },
        'stderr': {
            'level':'ERROR',
            'class':'logging.StreamHandler',
            'stream': sys.stderr
        },
    },
    'loggers': {
        '': {
            'handlers': ['stdout'],
            'level': 'INFO',
            'propagate': False,
        },
        '': {
            'handlers': ['stderr'],
            'level': 'ERROR',
            'propagate': False,
        }
    }
}

if os.getenv('AUTH', 'NONE') == 'SAML_MOCK':
    INSTALLED_APPS += ['uw_saml']

    MOCK_SAML_ATTRIBUTES = {
    'uwnetid': ['javerage'],
    'affiliations': ['student', 'member', 'alum', 'staff', 'employee'],
    'eppn': ['javerage@washington.edu'],
    'scopedAffiliations': ['student@washington.edu', 'member@washington.edu'],
    'isMemberOf': ['u_test_group', 'u_test_another_group',
                   'u_astratest_myuw_test-support-admin'],
    }

    from django.urls import reverse_lazy
    LOGIN_URL = reverse_lazy('saml_login')
    LOGOUT_URL = reverse_lazy('saml_logout')

elif os.getenv('AUTH', 'NONE') == 'SAML':
    INSTALLED_APPS += ['uw_saml']

    CLUSTER_CNAME = os.getenv('CLUSTER_CNAME', 'localhost')

    UW_SAML = {
        'strict': True,
        'debug': True,
        'sp': {
            'entityId': os.getenv("SAML_ENTITY_ID", "https://" + CLUSTER_CNAME + "/saml"),
            'assertionConsumerService': {
                'url': 'https://' + CLUSTER_CNAME + '/saml/sso',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'
            },
            'singleLogoutService': {
                'url': 'https://' + CLUSTER_CNAME + '/saml/logout',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'x509cert': os.getenv('SP_CERT', ''),
                },
        'idp': {
            'entityId': 'urn:mace:incommon:washington.edu',
            'singleSignOnService': {
                'url': 'https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'singleLogoutService': {
                'url': 'https://idp.u.washington.edu/idp/logout',
                'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
            },
            'x509cert': os.getenv('IDP_CERT', ''),
        },
        'security': {
            'authnRequestsSigned': False,
            'wantMessagesSigned': True,
            'wantAssertionsSigned': False,
            'wantAssertionsEncrypted': False,
                }
    }

    from django.urls import reverse
    LOGIN_URL = reverse('saml_login')
    LOGOUT_URL = reverse('saml_logout')
    REMOTE_USER_FORMAT = 'uwnetid'

APPLICATION_CERT_PATH = os.getenv('CERT_PATH', '')
APPLICATION_KEY_PATH = os.getenv('KEY_PATH', '')

# Restclient config

RESTCLIENTS_CA_BUNDLE = '/app/certs/ca-bundle.crt' 

if os.getenv('GWS_ENV') == 'PROD' or os.getenv('GWS_ENV') == 'EVAL':
    RESTCLIENTS_GWS_DAO_CLASS = 'Live'
    RESTCLIENTS_GWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_GWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_GWS_TIMEOUT=5
    RESTCLIENTS_GWS_POOL_SIZE=10

if os.getenv('GWS_ENV') == 'PROD':
    RESTCLIENTS_GWS_HOST='https://iam-ws.u.washington.edu:7443'


if os.getenv('SWS_ENV') == 'PROD' or os.getenv('SWS_ENV') == 'EVAL':
    RESTCLIENTS_SWS_DAO_CLASS = 'Live'
    RESTCLIENTS_SWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_SWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_SWS_TIMEOUT=5
    RESTCLIENTS_SWS_POOL_SIZE=10

if os.getenv('SWS_ENV') == 'PROD':
    RESTCLIENTS_SWS_HOST='https://ws.admin.washington.edu:443'

if os.getenv('SWS_ENV') == 'EVAL':
    RESTCLIENTS_SWS_HOST = 'https://wseval.s.uw.edu:443'

if os.getenv('PWS_ENV') == 'PROD' or os.getenv('PWS_ENV') == 'EVAL':
    RESTCLIENTS_PWS_DAO_CLASS = 'Live'
    RESTCLIENTS_PWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_PWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_PWS_TIMEOUT=5
    RESTCLIENTS_PWS_POOL_SIZE=10

if os.getenv('PWS_ENV') == 'PROD':
    RESTCLIENTS_PWS_HOST = 'https://ws.admin.washington.edu:443'

if os.getenv('PWS_ENV') == 'EVAL':
    RESTCLIENTS_PWS_HOST = 'https://wseval.s.uw.edu:443'

if os.getenv('CANVAS_ENV') == 'PROD' or os.getenv('CANVAS_ENV') == 'EVAL':
    RESTCLIENTS_CANVAS_DAO_CLASS='Live'
    RESTCLIENTS_CANVAS_OAUTH_BEARER= os.getenv('CANVAS_OAUTH_BEARER', '')
    RESTCLIENTS_CANVAS_TIMEOUT=5
    RESTCLIENTS_CANVAS_POOL_SIZE=10

if os.getenv('CAVNAS_ENV') == 'PROD':
    RESTCLIENTS_CANVAS_HOST = 'https://canvas.uw.edu'

if os.getenv('CANVAS_ENV') == 'EVAL':
    RESTCLIENTS_CANVAS_HOST = 'https://uw.test.instructure.com'
