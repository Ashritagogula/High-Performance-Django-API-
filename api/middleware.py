from django.db import connection
from django.conf import settings

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            response['X-Query-Count'] = str(len(connection.queries))
        return response
