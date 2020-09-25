from django.urls import include, re_path
import os

urlpatterns = [
    re_path(r'^', include('django_prometheus.urls'))
]

if any(item in ['SAML', 'SAML_MOCK', 'SAML_DJANGO_LOGIN'] for item in os.getenv('AUTH', '').split(' ')):
    urlpatterns += [re_path(r'^saml/', include('uw_saml.urls'))]
