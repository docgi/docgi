import logging
from threading import local

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)
_thread_locals = local()


class ThreadLocalMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.query_count = 0
        return self.get_response(request)
