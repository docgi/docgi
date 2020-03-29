from .base import *  # noqa

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
MIDDLEWARE += ['docgi.base.middlewares.ThreadLocalMiddleware']
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
CORS_ORIGIN_WHITELIST = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]
CORS_ORIGIN_REGEX_WHITELIST = [
    r"http://.*.localhost:8080",
    r"http://.*.192.168.1.11:8080",
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'sql': {
            '()': 'docgi.utils.logging.DocgiLoggingFormatter',
            'format': '%(statement)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'sql': {
            'class': 'logging.StreamHandler',
            'formatter': 'sql',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['sql'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends.schema': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}
