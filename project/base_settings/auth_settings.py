import os
import json
from .common import INSTALLED_APPS, MIDDLEWARE, AUTHENTICATION_BACKENDS
from .setting_utils import parse_bool_from_str


def auth_from_env(auth):
    return next((a for a in os.getenv('AUTH', '').split(' ') if a.startswith(auth)), None)


_auth = auth_from_env('SAML')
if _auth:
    INSTALLED_APPS.append('uw_saml')
    LOGIN_URL = '/saml/login'
    LOGOUT_URL = '/saml/logout'
    SAML_USER_ATTRIBUTE = os.getenv('SAML_USER_ATTRIBUTE', 'uwnetid')
    SAML_FORCE_AUTHN = parse_bool_from_str(os.getenv('SAML_FORCE_AUTHN', 'False'))

    if _auth == 'SAML_MOCK' or _auth == 'SAML_DJANGO_LOGIN':
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
        if _auth == 'SAML_MOCK':
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

    elif _auth == 'SAML':
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

_auth = auth_from_env('BLTI')
if _auth:
    INSTALLED_APPS.append('blti')

    try:
        MIDDLEWARE.remove('django.middleware.clickjacking.XFrameOptionsMiddleware')
    except Exception as ex:
        pass

    MIDDLEWARE.insert(0, 'blti.middleware.SessionHeaderMiddleware')
    MIDDLEWARE.insert(0, 'blti.middleware.CSRFHeaderMiddleware')
    MIDDLEWARE.insert(0, 'blti.middleware.SameSiteMiddleware')

    # relax samesite (django-blti>=2.2.1),
    # but protect cookies from casual snooping
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

    LTI_ENFORCE_SSL = parse_bool_from_str(os.getenv('LTI_ENFORCE_SSL', 'False'))

    if _auth == 'BLTI_DEV' and os.getenv('ENV', 'localdev') == 'localdev':
        LTI_DEVELOP_APP = os.getenv('LTI_DEVELOP_APP', '')
        LTI_CONSUMERS = {'0000-0000-0000': '01234567ABCDEF'}
        BLTI_AES_KEY = bytes('AE91AE1DF0E6FB44', encoding='utf8')
        BLTI_AES_IV = bytes('01C8837249AE8667', encoding='utf8')
        MIDDLEWARE.remove('blti.middleware.SameSiteMiddleware')
        CSRF_COOKIE_SECURE = False
    else:
        # BLTI consumer key:secret pairs in env as a serialized dict
        LTI_CONSUMERS = json.loads(os.getenv('LTI_CONSUMERS', '{}'))

        # BLTI session object encryption values
        BLTI_AES_KEY = bytes(os.getenv('BLTI_AES_KEY', ''), encoding='utf8')
        BLTI_AES_IV = bytes(os.getenv('BLTI_AES_IV', ''), encoding='utf8')
