from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property
import ssl


class EmailBackend(SMTPBackend):
    """
    See https://code.djangoproject.com/ticket/34504
    """
    @cached_property
    def ssl_context(self):
        ssl_context = super().ssl_context
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        return ssl_context
