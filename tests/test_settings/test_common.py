import os
import logging
from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from ..utils import SettingLoader
from . import REQUIRED_INSTALLED_APPS, REQUIRED_MIDDLEWARE,\
    REQUIRED_STATICFILES_FINDERS, DEFAULT_TEMPLATES, DEFAULT_HANDLERS,\
    DEFAULT_LOGGERS

class TestSecretKey(TestCase):
    def test_localdev_with_django_secret(self):
        with SettingLoader('project.base_settings', ENV='localdev', DJANGO_SECRET='testdjangosecret') as base_settings:
            self.assertEqual(base_settings.SECRET_KEY, 'testdjangosecret')

    def test_localdev_without_django_secret(self):
        with patch('django.core.management.utils.get_random_secret_key', return_value='mockeddjangosecret'):
            with SettingLoader('project.base_settings', ENV='localdev') as base_settings:
                self.assertEqual(base_settings.SECRET_KEY, 'mockeddjangosecret')

    def test_notlocaldev_with_django_secret(self):
        with SettingLoader('project.base_settings', ENV='notlocaldev', DJANGO_SECRET='testdjangosecret') as base_settings:
            self.assertEqual(base_settings.SECRET_KEY, 'testdjangosecret')

    def test_notlocaldev_without_django_secret(self):
        with SettingLoader('project.base_settings', ENV='notlocaldev') as base_settings:
            self.assertIsNone(base_settings.SECRET_KEY)

class TestAllowedHosts(TestCase):
    def test_allowed_hosts(self):
        with SettingLoader('project.base_settings', ENV='notlocaldev', CLUSTER_CNAME='test.edu', HOSTNAME='1.2.3.4') as base_settings:
            self.assertEqual(base_settings.ALLOWED_HOSTS, ['test.edu', '1.2.3.4', '1.2.3.4'])
            self.assertEqual(base_settings.CSRF_TRUSTED_ORIGINS, ['https://test.edu'])

class TestInstalledApps(TestCase):
    def test_contains_required_apps(self):
        with SettingLoader('project.base_settings') as base_settings:
            for app in REQUIRED_INSTALLED_APPS:
                self.assertIn(app, base_settings.INSTALLED_APPS)

class TestMiddleware(TestCase):
    def test_contains_required_middleware(self):
        with SettingLoader('project.base_settings') as base_settings:
            for middleware in REQUIRED_MIDDLEWARE:
                self.assertIn(middleware, base_settings.MIDDLEWARE)

class TestAuthenticationBackends(TestCase):
    def test_default_authentication_backend(self):
        with SettingLoader('project.base_settings') as base_settings:
            self.assertEqual(len(base_settings.AUTHENTICATION_BACKENDS), 1)
            self.assertEqual(base_settings.AUTHENTICATION_BACKENDS[0], 'django.contrib.auth.backends.RemoteUserBackend')

class TestDatabases(TestCase):
    def test_without_db(self):
        sqlite3_db = {
            'default': {
                'ENGINE': 'django_prometheus.db.backends.sqlite3',
                'NAME': '',
            }
        }
        with SettingLoader('project.base_settings') as base_settings:
            sqlite3_db['default']['NAME'] = os.path.join(base_settings.BASE_DIR, 'db.sqlite3')
            self.assertDictEqual(base_settings.DATABASES, sqlite3_db)

    def test_db_sqlite3(self):
        sqlite3_db = {
            'default': {
                'ENGINE': 'django_prometheus.db.backends.sqlite3',
                'NAME': '',
            }
        }
        with SettingLoader('project.base_settings', DB='sqlite3') as base_settings:
            sqlite3_db['default']['NAME'] = os.path.join(base_settings.BASE_DIR, 'db.sqlite3')
            self.assertDictEqual(base_settings.DATABASES, sqlite3_db)

    def test_db_mysql_default(self):
        mysql_db = {
            'default': {
                'ENGINE': 'django_prometheus.db.backends.mysql',
                'HOST': 'localhost',
                'NAME': 'db',
                'USER': None,
                'PASSWORD': None,
            }
        }
        with SettingLoader('project.base_settings', DB='mysql') as base_settings:
            self.assertDictEqual(base_settings.DATABASES, mysql_db)

    def test_db_mysql_with_env_values(self):
        database_env_values = {
            'DATABASE_HOSTNAME': 'test_hostname',
            'DATABASE_DB_NAME': 'test_db',
            'DATABASE_USERNAME': 'test_username',
            'DATABASE_PASSWORD': 'test_password',
        }
        mysql_db = {
            'default': {
                'ENGINE': 'django_prometheus.db.backends.mysql',
                'HOST': database_env_values['DATABASE_HOSTNAME'],
                'NAME': database_env_values['DATABASE_DB_NAME'],
                'USER': database_env_values['DATABASE_USERNAME'],
                'PASSWORD': database_env_values['DATABASE_PASSWORD'],
            }
        }
        with SettingLoader('project.base_settings', DB='mysql', **database_env_values) as base_settings:
            self.assertDictEqual(base_settings.DATABASES, mysql_db)

    def test_db_postgres_default(self):
        postgres_db = {
            'default': {
                'ENGINE': 'django_prometheus.db.backends.postgresql',
                'HOST': 'localhost',
                'NAME': 'db',
                'USER': None,
                'PASSWORD': None,
            }
        }
        with SettingLoader('project.base_settings', DB='postgres') as base_settings:
            self.assertDictEqual(base_settings.DATABASES, postgres_db)

    def test_db_postgres_with_env_values(self):
        database_env_values = {
            'DATABASE_HOSTNAME': 'test_hostname',
            'DATABASE_DB_NAME': 'test_db',
            'DATABASE_USERNAME': 'test_username',
            'DATABASE_PASSWORD': 'test_password',
        }
        postgres_db = {
            'default': {
                'ENGINE': 'django_prometheus.db.backends.postgresql',
                'HOST': database_env_values['DATABASE_HOSTNAME'],
                'NAME': database_env_values['DATABASE_DB_NAME'],
                'USER': database_env_values['DATABASE_USERNAME'],
                'PASSWORD': database_env_values['DATABASE_PASSWORD'],
            }
        }
        with SettingLoader('project.base_settings', DB='postgres', **database_env_values) as base_settings:
            self.assertDictEqual(base_settings.DATABASES, postgres_db)

class TestMemcached(TestCase):
    def test_servers(self):
        memcached = {
            'MEMCACHED_SERVER_COUNT': '2',
            'MEMCACHED_SERVER_SPEC': 'mock_memcached_{}:11211'
        }
        with SettingLoader('project.base_settings', **memcached) as base_settings:
            self.assertEqual(base_settings.MEMCACHED_SERVER_COUNT, 2)
            self.assertListEqual(
                base_settings.MEMCACHED_SERVERS,
                ['mock_memcached_0:11211', 'mock_memcached_1:11211'])

    def test_cache_backend(self):
        memcached = {
            'MEMCACHED_SERVER_COUNT': '1',
            'MEMCACHED_SERVER_SPEC': 'mock_memcached_{}:11211',
            'MEMCACHED_USE_POOLING': 'True',
            'MEMCACHED_MAX_POOL_SIZE': '9',
            'SESSION_BACKEND': 'MEMCACHED',
        }
        with SettingLoader('project.base_settings', **memcached) as base_settings:
            self.assertEqual(base_settings.CACHES['default']['LOCATION'],
                             ['mock_memcached_0:11211'])
            self.assertDictEqual(base_settings.CACHES['default']['OPTIONS'], {
                'use_pooling': 'True', 'max_pool_size': 9})
            self.assertEqual(base_settings.SESSION_ENGINE,
                             'django.contrib.sessions.backends.cache')


class TestStaticfilesFinders(TestCase):
    def test_requried_finders(self):
        with SettingLoader('project.base_settings') as base_settings:
            for finder in REQUIRED_STATICFILES_FINDERS:
                self.assertIn(finder, base_settings.STATICFILES_FINDERS)

class TestTemplates(TestCase):
    def test_template_default(self):
        with SettingLoader('project.base_settings') as base_settings:
            template = base_settings.TEMPLATES[0]
            self.assertDictEqual(DEFAULT_TEMPLATES[0], template)

class TestLogging(TestCase):
    def test_basic_settings(self):
        with SettingLoader('project.base_settings') as base_settings:
            self.assertEqual(base_settings.LOGGING['version'], 1)
            self.assertFalse(base_settings.LOGGING['disable_existing_loggers'])

    def test_default_filters(self):
        with SettingLoader('project.base_settings') as base_settings:
            class TestObject:
                def __init__(self, levelno):
                    self.levelno = levelno

            self.assertIn('stdout_stream', base_settings.LOGGING['filters'])
            self.assertIn('()', base_settings.LOGGING['filters']['stdout_stream'])
            self.assertEqual('django.utils.log.CallbackFilter', base_settings.LOGGING['filters']['stdout_stream']['()'])
            self.assertIn('callback', base_settings.LOGGING['filters']['stdout_stream'])
            self.assertTrue(base_settings.LOGGING['filters']['stdout_stream']['callback'](TestObject(logging.INFO)))
            self.assertFalse(base_settings.LOGGING['filters']['stdout_stream']['callback'](TestObject(logging.WARN)))

            self.assertIn('stderr_stream', base_settings.LOGGING['filters'])
            self.assertIn('()', base_settings.LOGGING['filters']['stderr_stream'])
            self.assertEqual('django.utils.log.CallbackFilter', base_settings.LOGGING['filters']['stderr_stream']['()'])
            self.assertIn('callback', base_settings.LOGGING['filters']['stderr_stream'])
            self.assertTrue(base_settings.LOGGING['filters']['stderr_stream']['callback'](TestObject(logging.WARN)))
            self.assertFalse(base_settings.LOGGING['filters']['stderr_stream']['callback'](TestObject(logging.INFO)))

    def test_default_handlers(self):
        with SettingLoader('project.base_settings') as base_settings:
            self.assertDictEqual(DEFAULT_HANDLERS, base_settings.LOGGING['handlers'])

    def test_default_loggers(self):
        with SettingLoader('project.base_settings') as base_settings:
            self.assertDictEqual(DEFAULT_LOGGERS, base_settings.LOGGING['loggers'])

    def test_prod_loggers(self):
        with SettingLoader('project.base_settings', ENV='prod') as base_settings:
            prod_logger = deepcopy(DEFAULT_LOGGERS)
            prod_logger['']['level'] = 'INFO'
            self.assertDictEqual(prod_logger, base_settings.LOGGING['loggers'])

class TestUtilCleanUp(TestCase):
    def test_cleanup(self):
        list_of_setting_utils_attr = None
        with SettingLoader('project.base_settings.setting_utils') as setting_utils:
            list_of_setting_utils_attr = setting_utils.list_of_attributes

        with SettingLoader('project.base_settings') as base_settings:
            for attr in list_of_setting_utils_attr:
                self.assertFalse(hasattr(base_settings, attr))
