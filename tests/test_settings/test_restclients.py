from unittest import TestCase
from ..utils import SettingLoader


class TestGlobals(TestCase):
    def setUp(self):
        self.mock_env = {
            'CERT_PATH': 'test/path/to/cert',
            'KEY_PATH': 'test/path/to/key',
            'CA_BUNDLE': 'test/path/to/ca-certs.crt',
            'CACHE_CLASS': 'test_cache_class',
        }

    def test_default_globals_with_env(self):
        # Get settings from the restclients_settings and check if they change when base_settings is loaded
        with SettingLoader('project.base_settings.restclients_settings', **self.mock_env) as restclients_settings:
            APPLICATION_CERT_PATH = restclients_settings.APPLICATION_CERT_PATH
            APPLICATION_KEY_PATH = restclients_settings.APPLICATION_KEY_PATH
            RESTCLIENTS_CA_BUNDLE = restclients_settings.RESTCLIENTS_CA_BUNDLE
            RESTCLIENTS_DAO_CACHE_CLASS = restclients_settings.RESTCLIENTS_DAO_CACHE_CLASS
            RESTCLIENTS_DEFAULT_TIMEOUT = restclients_settings.RESTCLIENTS_DEFAULT_TIMEOUT
            RESTCLIENTS_DEFAULT_POOL_SIZE = restclients_settings.RESTCLIENTS_DEFAULT_POOL_SIZE
            RESTCLIENTS_DEFAULT_ENVS = restclients_settings.RESTCLIENTS_DEFAULT_ENVS

        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertEqual(APPLICATION_CERT_PATH, base_settings.APPLICATION_CERT_PATH)
            self.assertEqual(APPLICATION_KEY_PATH, base_settings.APPLICATION_KEY_PATH)
            self.assertEqual(RESTCLIENTS_CA_BUNDLE, base_settings.RESTCLIENTS_CA_BUNDLE)
            self.assertEqual(RESTCLIENTS_DAO_CACHE_CLASS, base_settings.RESTCLIENTS_DAO_CACHE_CLASS)
            self.assertEqual(RESTCLIENTS_DEFAULT_TIMEOUT, base_settings.RESTCLIENTS_DEFAULT_TIMEOUT)
            self.assertEqual(RESTCLIENTS_DEFAULT_POOL_SIZE, base_settings.RESTCLIENTS_DEFAULT_POOL_SIZE)
            self.assertEqual(RESTCLIENTS_DEFAULT_ENVS, base_settings.RESTCLIENTS_DEFAULT_ENVS)


class TestCache(TestCase):
    def test_memcached(self):
        mock_memcached = {
            'MEMCACHED_SERVER_COUNT': '1',
            'MEMCACHED_SERVER_SPEC': 'mock_memcached_{}:11211'
        }
        with SettingLoader('project.base_settings', **mock_memcached) as base_settings:
            self.assertSequenceEqual(('mock_memcached_0:11211',), base_settings.RESTCLIENTS_MEMCACHED_SERVERS)


class TestEmail(TestCase):
    def test_email(self):
        mock_email = {
            'EMAIL_HOST': 'test.edu',
            'ENV': 'prod',
        }
        with SettingLoader('project.base_settings', **mock_email) as base_settings:
            self.assertEqual(base_settings.EMAIL_BACKEND, 'project.mail.backends.EmailBackend')


class TestRestClients(TestCase):
    def test_settings_not_overwritten(self):
        restclients = [
            'GWS_ENV',
            'SWS_ENV',
            'PWS_ENV',
            'KWS_ENV',
            'HRPWS_ENV',
            'UWNETID_ENV',
            'CANVAS_ENV',
            'CODA_ENV',
            'GRADEPAGE_ENV',
            'BOOKSTORE_ENV',
            'GRAD_ENV',
            'MYPLAN_ENV',
            'MYPLAN_AUTH_ENV',
            'SPS_CONTACTS_ENV',
            'SPS_CONTACTS_AUTH_ENV',
            'SPACE_ENV',
            'LIBCURRICS_ENV',
            'LIBRARIES_ENV',
            'CALENDAR_ENV',
            'SDBMYUW_ENV',
            'HFS_ENV',
            'UWIDP_ENV',
            'ADSEL_ENV',
            'UPASS_ENV',
            'IASYSTEM_UW_ENV',
            'IASYSTEM_UWB_ENV',
            'IASYSTEM_UWT_ENV',
            'IASYSTEM_UWEO_AP_ENV',
            'IASYSTEM_UWEO_IELP_ENV',
            'ASTRA_ENV',
            'R25_ENV',
        ]
        for env in ['PROD', 'EVAL']:
            restclients_attr = {}
            mock_env = {}
            for restclient in restclients:
                mock_env[restclient] = env
            with SettingLoader('project.base_settings.restclients_settings', **mock_env) as restclients_settings:
                for attr in filter(lambda x: (x.startswith('RESTCLIENTS') or x.startswith('ASTRA')), dir(restclients_settings)):
                    restclients_attr[attr] = getattr(restclients_settings, attr)

            with SettingLoader('project.base_settings', **mock_env) as base_settings:
                for attr in filter(lambda x: (x.startswith('RESTCLIENTS') or x.startswith('ASTRA')), dir(base_settings)):
                    self.assertEqual(restclients_attr[attr], getattr(base_settings, attr))
