from unittest import TestCase
from ..utils import SettingLoader


class SAMLBaseAuthTest:
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

        self.mock_env['SAML_FORCE_AUTHN'] = 'False'
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertFalse(base_settings.SAML_FORCE_AUTHN)


class NoAuthBackendTest(TestCase):
    def test_common_attributes(self):
        with SettingLoader('project.base_settings') as base_settings:
            self.assertNotIn('uw_saml', base_settings.INSTALLED_APPS)
            self.assertFalse(hasattr(base_settings, 'LOGIN_URL'))
            self.assertFalse(hasattr(base_settings, 'LOGOUT_URL'))
            self.assertFalse(hasattr(base_settings, 'SAML_USER_ATTRIBUTE'))
            self.assertFalse(hasattr(base_settings, 'SAML_FORCE_AUTHN'))


class SAMLTest(TestCase, SAMLBaseAuthTest):
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


class SAMLMockTest(TestCase, SAMLBaseAuthTest):
    def setUp(self):
        self.mock_env = {
            'AUTH': 'SAML_MOCK',
        }

    def test_attributes(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertIsNotNone(base_settings.DEFAULT_SAML_ATTRIBUTES)
            self.assertIsNotNone(base_settings.MOCK_SAML_ATTRIBUTES)

            self.assertDictEqual(base_settings.DEFAULT_SAML_ATTRIBUTES, base_settings.MOCK_SAML_ATTRIBUTES)


class SAMLDjangoLoginTest(TestCase, SAMLBaseAuthTest):
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


class BLTITest(TestCase):
    def setUp(self):
        self.mock_env = {
            'AUTH': 'BLTI',
            'LTI_CONSUMERS': '{"0000-0000-0000": "01234567ABCDEF"}',
            'BLTI_AES_KEY': 'AE91AE1DF0E6FB44',
            'BLTI_AES_IV': '01C8837249AE8667',
        }

    def test_attributes(self):
        with SettingLoader('project.base_settings', **self.mock_env) as base_settings:
            self.assertIn('blti', base_settings.INSTALLED_APPS)
            self.assertIn('blti.middleware.SessionHeaderMiddleware', base_settings.MIDDLEWARE)
            self.assertIn('blti.middleware.CSRFHeaderMiddleware', base_settings.MIDDLEWARE)
            self.assertDictEqual({"0000-0000-0000": "01234567ABCDEF"}, base_settings.LTI_CONSUMERS)


class MultipleAuthTest(TestCase):
    def test_valid_auth_list(self):
        mock_env = {
            'AUTH': 'SAML BLTI',
        }

        with SettingLoader('project.base_settings', **mock_env) as base_settings:
            self.assertIn('uw_saml', base_settings.INSTALLED_APPS)
            self.assertIn('blti', base_settings.INSTALLED_APPS)

    def test_invalid_auth_list(self):
        mock_env = {
            'AUTH': 'SAML_MOCK SAML',
        }

        # Ensure that only the first occurence of a SAML type was configured
        with SettingLoader('project.base_settings', **mock_env) as base_settings:
            self.assertIn('uw_saml', base_settings.INSTALLED_APPS)
            self.assertIsNotNone(base_settings.MOCK_SAML_ATTRIBUTES)
            self.assertDictEqual(base_settings.DEFAULT_SAML_ATTRIBUTES, base_settings.MOCK_SAML_ATTRIBUTES)
            self.assertFalse(hasattr(base_settings, 'UW_SAML'))
