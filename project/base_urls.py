from django.urls import include, re_path
import os

urlpatterns = [
    re_path(r'^', include('django_prometheus.urls'))
]

if os.getenv('AUTH', '') in ['SAML', 'SAML_MOCK', 'SAML_DJANGO_LOGIN']:
    urlpatterns += [re_path(r'^saml/', include('uw_saml.urls'))]
