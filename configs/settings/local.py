from .base import *

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]


EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

EMAIL_HOST = 'localhost'

EMAIL_PORT = 1025
