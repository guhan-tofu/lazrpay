from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
# this is for extra security headers
class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        response.headers.setdefault('X-XSS-Protection', '1; mode=block')
        return response 