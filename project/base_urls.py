from django.urls import include, re_path
import os

urlpatterns = []


if os.getenv('AUTH', '') == 'SAML' or os.getenv('AUTH', '') == 'SAML_MOCK':
    urlpatterns += [re_path(r'^saml/', include('uw_saml.urls'))]
