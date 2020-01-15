from django.core.management.utils import get_random_secret_key
from django.urls import reverse_lazy
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
    RESTCLIENTS_DAO_CACHE_CLASS = 'myuw.util.cache_implementation.MyUWMemcachedCache'
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

if os.getenv('AUTH', 'NONE') == 'SAML_MOCK' or os.getenv('AUTH', 'NONE') == 'SAML':
    INSTALLED_APPS += ['uw_saml']
    LOGIN_URL = reverse_lazy('saml_login')
    LOGOUT_URL = reverse_lazy('saml_logout')
    SAML_USER_ATTRIBUTE = os.getenv('SAML_USER_ATTRIBUTE', 'uwnetid')
    SAML_FORCE_AUTHN = os.getenv('SAML_FORCE_AUTHN', False)

    if os.getenv('AUTH', 'NONE') == 'SAML_MOCK':
        MOCK_SAML_ATTRIBUTES = {
            'uwnetid': ['javerage'],
            'affiliations': ['student', 'member', 'alum', 'staff', 'employee'],
            'eppn': ['javerage@washington.edu'],
            'scopedAffiliations': ['student@washington.edu', 'member@washington.edu'],
            'isMemberOf': ['u_test_group', 'u_test_another_group',
                           'u_astratest_myuw_test-support-admin'],
        }

    elif os.getenv('AUTH', 'NONE') == 'SAML':
        CLUSTER_CNAME = os.getenv('CLUSTER_CNAME', 'localhost')
        UW_SAML = {
            'strict': True,
            'debug': True,
            'sp': {
                'entityId': os.getenv('SAML_ENTITY_ID', 'https://' + CLUSTER_CNAME + '/saml'),
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
                if os.getenv('SP_PRIVATE_KEY', None):
                    'privateKey': os.getenv('SP_PRIVATE_KEY'),
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
                'authnRequestsSigned': os.getenv('SP_AUTHN_REQUESTS_SIGNED', False),
                'wantMessagesSigned': os.getenv('SP_WANT_MESSAGES_SIGNED', True),
                'wantAssertionsSigned': os.getenv('SP_WANT_ASSERTIONS_SIGNED', False),
                'wantAssertionsEncrypted': os.getenv('SP_WANT_ASSERTIONS_ENCRYPTED', False),
                if os.getenv('SP_USE_2FA', False):
                    'requestedAuthnContext': ['urn:oasis:names:tc:SAML:2.0:ac:classes:TimeSyncToken'],
                    'failOnAuthnContextMismatch': True,
            }
        }

# Restclient config
APPLICATION_CERT_PATH = os.getenv('CERT_PATH', '')
APPLICATION_KEY_PATH = os.getenv('KEY_PATH', '')
RESTCLIENTS_DEFAULT_TIMEOUT = 5
RESTCLIENTS_DEFAULT_POOL_SIZE = 10
RESTCLIENTS_CA_BUNDLE = '/app/certs/ca-bundle.crt'

if os.getenv('GWS_ENV') == 'PROD' or os.getenv('GWS_ENV') == 'EVAL':
    RESTCLIENTS_GWS_DAO_CLASS = 'Live'
    RESTCLIENTS_GWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_GWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_GWS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_GWS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('GWS_ENV') == 'PROD':
        RESTCLIENTS_GWS_HOST = 'https://groups.uw.edu'
    else:
        RESTCLIENTS_GWS_HOST = 'https://iam-ws.u.washington.edu:7443'

if os.getenv('SWS_ENV') == 'PROD' or os.getenv('SWS_ENV') == 'EVAL':
    RESTCLIENTS_SWS_DAO_CLASS = 'Live'
    RESTCLIENTS_SWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_SWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_SWS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_SWS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('SWS_ENV') == 'PROD':
        RESTCLIENTS_SWS_HOST = 'https://ws.admin.washington.edu:443'
    else:
        RESTCLIENTS_SWS_HOST = 'https://wseval.s.uw.edu:443'

if os.getenv('PWS_ENV') == 'PROD' or os.getenv('PWS_ENV') == 'EVAL':
    RESTCLIENTS_PWS_DAO_CLASS = 'Live'
    RESTCLIENTS_PWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_PWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_PWS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_PWS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('PWS_ENV') == 'PROD':
        RESTCLIENTS_PWS_HOST = 'https://ws.admin.washington.edu:443'
    else:
        RESTCLIENTS_PWS_HOST = 'https://wseval.s.uw.edu:443'

if os.getenv('KWS_ENV') == 'PROD' or os.getenv('KWS_ENV') == 'EVAL':
    RESTCLIENTS_KWS_DAO_CLASS = 'Live'
    RESTCLIENTS_KWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_KWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_KWS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_KWS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('KWS_ENV') == 'PROD':
        RESTCLIENTS_KWS_HOST = 'https://ws.admin.washington.edu:443'
    else:
        RESTCLIENTS_KWS_HOST = 'https://wseval.s.uw.edu:443'

if os.getenv('HRPWS_ENV') == 'PROD' or os.getenv('HRPWS_ENV') == 'EVAL':
    RESTCLIENTS_HRPWS_DAO_CLASS = 'Live'
    RESTCLIENTS_HRPWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_HRPWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_HRPWS_TIMEOUT = os.getenv('HRPWS_TIMEOUT', RESTCLIENTS_DEFAULT_TIMEOUT)
    RESTCLIENTS_HRPWS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('HRPWS_ENV') == 'PROD':
        RESTCLIENTS_HRPWS_HOST = 'https://ws.admin.washington.edu:443'
    else:
        RESTCLIENTS_HRPWS_HOST = 'https://wseval.s.uw.edu:443'

if os.getenv('NWS_ENV') == 'PROD' or os.getenv('NWS_ENV') == 'EVAL':
    RESTCLIENTS_NWS_DAO_CLASS = 'Live'
    RESTCLIENTS_NWS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_NWS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_NWS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_NWS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('NWS_ENV') == 'PROD':
        RESTCLIENTS_NWS_HOST = 'https://api.concert.uw.edu'
    else:
        RESTCLIENTS_NWS_HOST = 'https://api.test.concert.uw.edu'

if os.getenv('UWNETID_ENV') == 'PROD' or os.getenv('UWNETID_ENV') == 'EVAL':
    RESTCLIENTS_UWNETID_DAO_CLASS = 'Live'
    RESTCLIENTS_UWNETID_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_UWNETID_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_UWNETID_TIMEOUT = os.getenv('UWNETID_TIMEOUT', 55)
    RESTCLIENTS_UWNETID_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_UWNETID_HOST = 'https://uwnetid.washington.edu'
    if os.getenv('UWNETID_ENV') == 'EVAL':
        RESTCLIENTS_UWNETID_VERSION = 'v0-eval'

if os.getenv('CANVAS_ENV') == 'PROD' or os.getenv('CANVAS_ENV') == 'EVAL':
    RESTCLIENTS_CANVAS_DAO_CLASS = 'Live'
    RESTCLIENTS_CANVAS_OAUTH_BEARER = os.getenv('CANVAS_OAUTH_BEARER', '')
    RESTCLIENTS_CANVAS_TIMEOUT = os.getenv('CANVAS_TIMEOUT', RESTCLIENTS_DEFAULT_TIMEOUT)
    RESTCLIENTS_CANVAS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('CANVAS_ENV') == 'PROD':
        RESTCLIENTS_CANVAS_HOST = 'https://canvas.uw.edu'
    else:
        RESTCLIENTS_CANVAS_HOST = 'https://uw.test.instructure.com'

if os.getenv('CODA_ENV') == 'PROD' or os.getenv('CODA_ENV') == 'EVAL':
    RESTCLIENTS_CODA_DAO_CLASS = 'Live'
    RESTCLIENTS_CODA_AUTH_TOKEN = os.getenv('CODA_AUTH_TOKEN', '')
    RESTCLIENTS_CODA_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_CODA_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('CODA_ENV') == 'PROD':
        RESTCLIENTS_CODA_HOST = 'https://coda.uw.edu'
    else:
        RESTCLIENTS_CODA_HOST = 'https://coda-test.uw.edu'

if os.getenv('CATALYST_ENV') == 'PROD' or os.getenv('CATALYST_ENV') == 'EVAL':
    RESTCLIENTS_CATALYST_DAO_CLASS = 'Live'
    if os.getenv('CATALYST_PRIVATE_KEY') is not None:
        RESTCLIENTS_CATALYST_SOL_AUTH_PUBLIC_KEY = os.getenv('CATALYST_PUBLIC_KEY')
        RESTCLIENTS_CATALYST_SOL_AUTH_PRIVATE_KEY = os.getenv('CATALYST_PRIVATE_KEY')
    else:
        RESTCLIENTS_CATALYST_CERT_FILE = APPLICATION_CERT_PATH
        RESTCLIENTS_CATALYST_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_CATALYST_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_CATALYST_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('CATALYST_ENV') == 'PROD':
        RESTCLIENTS_CATALYST_HOST = 'https://catalyst.uw.edu'
    else:
        RESTCLIENTS_CATALYST_HOST = 'https://cat-dev-tools11.s.uw.edu'

if os.getenv('GRADEPAGE_ENV') == 'PROD' or os.getenv('GRADEPAGE_ENV') == 'EVAL':
    RESTCLIENTS_GRADEPAGE_DAO_CLASS = 'Live'
    RESTCLIENTS_GRADEPAGE_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_GRADEPAGE_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('GRADEPAGE_ENV') == 'PROD':
        RESTCLIENTS_GRADEPAGE_HOST = 'https://gradepage.uw.edu'
    else:
        RESTCLIENTS_GRADEPAGE_HOST = 'https://gradepage-test.s.uw.edu'

if os.getenv('BOOKSTORE_ENV') == 'PROD' or os.getenv('BOOKSTORE_ENV') == 'EVAL':
    RESTCLIENTS_BOOKSTORE_DAO_CLASS = 'Live'
    RESTCLIENTS_BOOKSTORE_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_BOOKSTORE_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_BOOKSTORE_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_BOOKSTORE_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_BOOKSTORE_HOST = 'https://www7.bookstore.washington.edu'

if os.getenv('GRAD_ENV') == 'PROD' or os.getenv('GRAD_ENV') == 'EVAL':
    RESTCLIENTS_GRAD_DAO_CLASS = 'Live'
    RESTCLIENTS_GRAD_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_GRAD_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_GRAD_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_GRAD_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('GRAD_ENV') == 'PROD':
        RESTCLIENTS_GRAD_HOST = 'https://webapps.grad.uw.edu'
    else:
        RESTCLIENTS_GRAD_HOST = 'https://testweb.grad.uw.edu'

if os.getenv('MYPLAN_ENV') == 'PROD' or os.getenv('MYPLAN_ENV') == 'EVAL':
    RESTCLIENTS_MYPLAN_DAO_CLASS = 'Live'
    RESTCLIENTS_MYPLAN_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_MYPLAN_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_MYPLAN_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_MYPLAN_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('MYPLAN_ENV') == 'PROD':
        RESTCLIENTS_MYPLAN_HOST = 'https://ws.uwstdent.washington.edu'
    else:
        RESTCLIENTS_MYPLAN_HOST = 'https://ws-eval.uwstudent.washington.edu'

if os.getenv('LIBCURRICS_ENV') == 'PROD' or os.getenv('LIBCURRICS_ENV') == 'EVAL':
    RESTCLIENTS_LIBCURRICS_DAO_CLASS = 'Live'
    RESTCLIENTS_LIBCURRICS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_LIBCURRICS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_LIBCURRICS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_LIBCURRICS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_LIBCURRICS_HOST = 'https://currics.lib.washington.edu'

if os.getenv('LIBRARIES_ENV') == 'PROD' or os.getenv('LIBRARIES_ENV') == 'EVAL':
    RESTCLIENTS_LIBRARIES_DAO_CLASS = 'Live'
    RESTCLIENTS_LIBRARIES_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_LIBRARIES_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_LIBRARIES_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_LIBRARIES_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_LIBRARIES_HOST = 'https://mylibinfo.lib.washington.edu'

if os.getenv('CALENDAR_ENV') == 'PROD' or os.getenv('CALENDAR_ENV') == 'EVAL':
    RESTCLIENTS_CALENDAR_DAO_CLASS = 'Live'
    RESTCLIENTS_CALENDAR_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_CALENDAR_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_CALENDAR_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_CALENDAR_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_CALENDAR_HOST = 'https://www.trumba.com'

if os.getenv('SDBMYUW_ENV') == 'PROD' or os.getenv('SDBMYUW_ENV') == 'EVAL':
    RESTCLIENTS_SDBMYUW_DAO_CLASS='Live'
    RESTCLIENTS_SDBMYUW_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_SDBMYUW_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('SDBMYUW_ENV') == 'PROD':
        RESTCLIENTS_SDBMYUW_HOST = 'https://sdb.admin.uw.edu'
    else:
        RESTCLIENTS_SDBMYUW_HOST = 'https://it-eval.s.uw.edu'

if os.getenv('HFS_ENV') == 'PROD' or os.getenv('HFS_ENV') == 'EVAL':
    RESTCLIENTS_HFS_DAO_CLASS = 'Live'
    RESTCLIENTS_HFS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_HFS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_HFS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_HFS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('HFS_ENV') == 'PROD':
        RESTCLIENTS_HFS_HOST = 'https://api.hfs.washington.edu'
    else:
        RESTCLIENTS_HFS_HOST = 'https://tapi.washington.edu'

if os.getenv('ADSEL_ENV') == 'PROD' or os.getenv('ADSEL_ENV') == 'EVAL':
    RESTCLIENTS_ADSEL_DAO_CLASS = 'Live'
    RESTCLIENTS_ADSEL_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_ADSEL_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_ADSEL_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_ADSEL_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('ADSEL_ENV') == 'PROD':
        RESTCLIENTS_ADSEL_HOST = 'https://adselapi.uw.edu'
    else:
        RESTCLIENTS_ADSEL_HOST = 'https://test.adselapi.uw.edu'

if os.getenv('UPASS_ENV') == 'PROD' or os.getenv('UPASS_ENV') == 'EVAL':
    RESTCLIENTS_UPASS_DAO_CLASS = 'Live'
    RESTCLIENTS_UPASS_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_UPASS_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_UPASS_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_UPASS_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    if os.getenv('UPASS_ENV') == 'PROD':
        RESTCLIENTS_UPASS_HOST = 'https://wscc.admin.uw.edu'
    else:
        RESTCLIENTS_UPASS_HOST = 'https://eval-wscc.admin.uw.edu'

if os.getenv('IASYSTEM_UW_ENV') == 'PROD' or os.getenv('IASYSTEM_UW_ENV') == 'EVAL':
    RESTCLIENTS_IASYSTEM_UW_DAO_CLASS = 'Live'
    RESTCLIENTS_IASYSTEM_UW_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_IASYSTEM_UW_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_IASYSTEM_UW_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_IASYSTEM_UW_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_IASYSTEM_UW_HOST = 'https://uw.iasystem.org'

if os.getenv('IASYSTEM_UWB_ENV') == 'PROD' or os.getenv('IASYSTEM_UWB_ENV') == 'EVAL':
    RESTCLIENTS_IASYSTEM_UWB_DAO_CLASS = 'Live'
    RESTCLIENTS_IASYSTEM_UWB_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_IASYSTEM_UWB_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_IASYSTEM_UWB_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_IASYSTEM_UWB_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_IASYSTEM_UWB_HOST = 'https://uwb.iasystem.org'

if os.getenv('IASYSTEM_UWT_ENV') == 'PROD' or os.getenv('IASYSTEM_UWT_ENV') == 'EVAL':
    RESTCLIENTS_IASYSTEM_UWT_DAO_CLASS = 'Live'
    RESTCLIENTS_IASYSTEM_UWT_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_IASYSTEM_UWT_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_IASYSTEM_UWT_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_IASYSTEM_UWT_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_IASYSTEM_UWT_HOST = 'https://uwt.iasystem.org'

if os.getenv('IASYSTEM_UWEO_AP_ENV') == 'PROD' or os.getenv('IASYSTEM_UWEO_AP_ENV') == 'EVAL':
    RESTCLIENTS_IASYSTEM_UWEO_AP_DAO_CLASS = 'Live'
    RESTCLIENTS_IASYSTEM_UWEO_AP_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_IASYSTEM_UWEO_AP_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_IASYSTEM_UWEO_AP_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_IASYSTEM_UWEO_AP_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_IASYSTEM_UWEO_AP_HOST = 'https://uweo-ap.iasystem.org'

if os.getenv('IASYSTEM_UWEO_IELP_ENV') == 'PROD' or os.getenv('IASYSTEM_UWEO_IELP_ENV') == 'EVAL':
    RESTCLIENTS_IASYSTEM_UWEO_IELP_DAO_CLASS = 'Live'
    RESTCLIENTS_IASYSTEM_UWEO_IELP_CERT_FILE = APPLICATION_CERT_PATH
    RESTCLIENTS_IASYSTEM_UWEO_IELP_KEY_FILE = APPLICATION_KEY_PATH
    RESTCLIENTS_IASYSTEM_UWEO_IELP_TIMEOUT = RESTCLIENTS_DEFAULT_TIMEOUT
    RESTCLIENTS_IASYSTEM_UWEO_IELP_POOL_SIZE = RESTCLIENTS_DEFAULT_POOL_SIZE
    RESTCLIENTS_IASYSTEM_UWEO_IELP_HOST = 'https://uweo-ielp.iasystem.org'

if os.getenv('ASTRA_ENV') == 'PROD' or os.getenv('ASTRA_ENV') == 'EVAL':
    ASTRA_CERT = APPLICATION_CERT_PATH
    ASTRA_KEY = APPLICATION_KEY_PATH
    ASTRA_APPLICATION = os.getenv('ASTRA_APPLICATION', '')
    ASTRA_ENVIRONMENT = os.getenv('ASTRA_ENV')
    if os.getenv('ASTRA_ENV') == 'PROD':
        ASTRA_WSDL = 'https://astra.admin.uw.edu/astraws/v2/default.asmx?wsdl'
    else:
        ASTRA_WSDL = 'https://eval-astra.admin.uw.edu/astraws/v2/default.asmx?wsdl'

if os.getenv('R25_ENV') == 'PROD' or os.getenv('R25_ENV') == 'EVAL':
    RESTCLIENTS_R25_DAO_CLASS = 'Live'
    RESTCLIENTS_R25_INSTANCE = 'washington'
    RESTCLIENTS_R25_SSL_VERSION = 'TLSv1_2'
    RESTCLIENTS_R25_BASIC_AUTH = os.getenv('R25_BASIC_AUTH', '')
    RESTCLIENTS_R25_HOST = 'https://webservices.collegenet.com'
