from .base import *  # noqa

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

MIDDLEWARE += ['apps.utils.middlewares.DocgiMiddleware']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
