from django.urls import include, re_path


urlpatterns = [
]

if os.getenv("AUTH", "mock") == "SAML" or os.getenv("AUTH", "SAML_MOCK") == "SAML_MOCK":
    urlpatterns += [ re_path(r'^saml/', include('uw_saml.urls')) ]