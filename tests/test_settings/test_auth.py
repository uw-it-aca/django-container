from unittest import TestCase
from ..utils import SettingLoader

class BaseAuthTest:
    def test_common_attributes(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertIn('uw_saml', base_settings.INSTALLED_APPS)
            self.assertEqual('/saml/login', base_settings.LOGIN_URL)
            self.assertEqual('/saml/logout', base_settings.LOGOUT_URL)
            self.assertEqual('uwnetid', base_settings.SAML_USER_ATTRIBUTE)
            self.assertFalse(base_settings.SAML_FORCE_AUTHN)

        self.mock_env['SAML_USER_ATTRIBUTE'] = 'mock_uwnetid'
        self.mock_env['SAML_FORCE_AUTHN'] = 'True'
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertEqual(self.mock_env['SAML_USER_ATTRIBUTE'], base_settings.SAML_USER_ATTRIBUTE)
            self.assertTrue(base_settings.SAML_FORCE_AUTHN)

class TestNoAuthBackend(TestCase):
    def test_common_attributes(self):
        with SettingLoader('project.base_settings') as base_settings:
            self.assertNotIn('uw_saml', base_settings.INSTALLED_APPS)
            self.assertFalse(hasattr(base_settings, 'LOGIN_URL'))
            self.assertFalse(hasattr(base_settings, 'LOGOUT_URL'))
            self.assertFalse(hasattr(base_settings, 'SAML_USER_ATTRIBUTE'))
            self.assertFalse(hasattr(base_settings, 'SAML_FORCE_AUTHN'))

class TestSAML(TestCase, BaseAuthTest):
    def setUp(self):
        self.mock_env = {
            'AUTH': 'SAML',
            'CLUSTER_CNAME': 'test.com',
        }

    def test_attributes(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertEqual(self.mock_env['CLUSTER_CNAME'], base_settings.CLUSTER_CNAME)
            
            # Just tests that UW_SAML attributes exists
            self.assertIsNotNone(base_settings.UW_SAML)

class TestSAMLMOCK(TestCase, BaseAuthTest):
    def setUp(self):
        self.mock_env = {
            'AUTH': 'SAML_MOCK',
        }

    def test_attributes(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertIsNotNone(base_settings.DEFAULT_SAML_ATTRIBUTES)
            self.assertIsNotNone(base_settings.MOCK_SAML_ATTRIBUTES)
            
            self.assertDictEqual(base_settings.DEFAULT_SAML_ATTRIBUTES, base_settings.MOCK_SAML_ATTRIBUTES)

class TestSAMLDJANGOLOGIN(TestCase, BaseAuthTest):
    def setUp(self):
        self.mock_env = {
            'AUTH': 'SAML_DJANGO_LOGIN',
            'DJANGO_LOGIN_USERNAME': 'test_user',
            'DJANGO_LOGIN_PASSWORD': 'test_password',
            'DJANGO_LOGIN_EMAIL': 'test_email',
        }

    def test_attributes(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertIn('django.contrib.auth.backends.ModelBackend', base_settings.AUTHENTICATION_BACKENDS)
            self.assertIsNotNone(base_settings.DJANGO_LOGIN_MOCK_SAML)

    def test_django_user_conf(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertEqual(len(base_settings.DJANGO_LOGIN_MOCK_SAML['SAML_USERS']), 1)
            
            self.assertEqual(base_settings.DJANGO_LOGIN_MOCK_SAML['SAML_USERS'][0]['username'], self.mock_env['DJANGO_LOGIN_USERNAME'])
            self.assertEqual(base_settings.DJANGO_LOGIN_MOCK_SAML['SAML_USERS'][0]['password'], self.mock_env['DJANGO_LOGIN_PASSWORD'])
            self.assertEqual(base_settings.DJANGO_LOGIN_MOCK_SAML['SAML_USERS'][0]['email'], self.mock_env['DJANGO_LOGIN_EMAIL'])
            self.assertDictEqual(base_settings.DJANGO_LOGIN_MOCK_SAML['SAML_USERS'][0]['MOCK_ATTRIBUTES'], base_settings.DEFAULT_SAML_ATTRIBUTES)
