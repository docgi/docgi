import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa


CORS_ORIGIN_REGEX_WHITELIST = [
    r"http://(.*.)?docgi.nakhoa.me"
]
ALLOWED_HOSTS = ["api-docgi.nakhoa.me"]

sentry_sdk.init(
    dsn="https://dd67cd0bc90b4bb3b3f3496c8517cb68@o394442.ingest.sentry.io/5244540",
    integrations=[DjangoIntegration()],

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)
