from django.utils.deprecation import MiddlewareMixin

from docgi.utils.logging import _thread_locals


class ThreadLocalMiddleware(MiddlewareMixin):
    def __init__(self, get_response):	
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        _thread_locals.query_count = 0
        return response
