import os
import json
from .common import INSTALLED_APPS, MIDDLEWARE, AUTHENTICATION_BACKENDS
from .setting_utils import parse_bool_from_str

for auth in os.getenv('AUTH', '').split(' '):
    if auth.startswith('SAML') and 'uw_saml' not in INSTALLED_APPS:
        INSTALLED_APPS += ['uw_saml']
        LOGIN_URL = '/saml/login'
        LOGOUT_URL = '/saml/logout'
        SAML_USER_ATTRIBUTE = os.getenv('SAML_USER_ATTRIBUTE', 'uwnetid')
        SAML_FORCE_AUTHN = parse_bool_from_str(os.getenv('SAML_FORCE_AUTHN', 'False'))

        if auth == 'SAML_MOCK' or auth == 'SAML_DJANGO_LOGIN':
            DEFAULT_SAML_ATTRIBUTES = {
                'uwnetid': ['javerage'],
                'affiliations': ['student', 'member', 'alum', 'staff', 'employee'],
                'eppn': ['javerage@washington.edu'],
                'scopedAffiliations': [
                    'student@washington.edu', 'member@washington.edu',
                    'alum@washington.edu', 'staff@washington.edu',
                    'employee@washington.edu'],
                'isMemberOf': ['u_test_group', 'u_test_another_group']
            }
            if auth == 'SAML_MOCK':
                MOCK_SAML_ATTRIBUTES = DEFAULT_SAML_ATTRIBUTES

            else:
                AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',)
                DJANGO_LOGIN_MOCK_SAML = {
                    'NAME_ID': 'mock-nameid',
                    'SESSION_INDEX': 'mock-session',
                    'SAML_USERS': [{
                        'username': os.getenv('DJANGO_LOGIN_USERNAME', 'javerage'),
                        'password': os.getenv('DJANGO_LOGIN_PASSWORD', 'javerage'),
                        'email': os.getenv('DJANGO_LOGIN_EMAIL', 'javerage@uw.edu'),
                        'MOCK_ATTRIBUTES': DEFAULT_SAML_ATTRIBUTES,
                    }]
                }

        elif auth == 'SAML':
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
                        'url': 'https://' + CLUSTER_CNAME + LOGOUT_URL,
                        'binding': 'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'
                    },
                    'NameIDFormat': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
                    'x509cert': os.getenv('SP_CERT', ''),
                    'privateKey': os.getenv('SP_PRIVATE_KEY', ''),
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
                    'authnRequestsSigned': parse_bool_from_str(os.getenv('SP_AUTHN_REQUESTS_SIGNED', 'False')),
                    'wantMessagesSigned': parse_bool_from_str(os.getenv('SP_WANT_MESSAGES_SIGNED', 'True')),
                    'wantAssertionsSigned': parse_bool_from_str(os.getenv('SP_WANT_ASSERTIONS_SIGNED', 'False')),
                    'wantAssertionsEncrypted': parse_bool_from_str(os.getenv('SP_WANT_ASSERTIONS_ENCRYPTED', 'False')),
                    'requestedAuthnContext': [
                        'urn:oasis:names:tc:SAML:2.0:ac:classes:TimeSyncToken'
                    ] if parse_bool_from_str(os.getenv('SP_USE_2FA', 'False')) else False,
                    'failOnAuthnContextMismatch': parse_bool_from_str(os.getenv('SP_USE_2FA', 'False')),
                }
            }

    if auth.startswith('BLTI') and 'blti' not in INSTALLED_APPS:
        INSTALLED_APPS += ['blti']

        MIDDLEWARE = ['blti.middleware.CSRFHeaderMiddleware',
                      'blti.middleware.SessionHeaderMiddleware'] + MIDDLEWARE

        # BLTI consumer key:secret pairs in env as a serialized dict
        LTI_CONSUMERS = json.loads(os.getenv('LTI_CONSUMERS', '{}'))
        LTI_ENFORCE_SSL = parse_bool_from_str(os.getenv('LTI_ENFORCE_SSL', 'False'))

        # BLTI session object encryption values
        BLTI_AES_KEY = bytes(os.getenv('BLTI_AES_KEY', ''), encoding='utf8')
        BLTI_AES_IV = bytes(os.getenv('BLTI_AES_IV', ''), encoding='utf8')
