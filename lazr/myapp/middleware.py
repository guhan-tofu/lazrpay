from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse

 
class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        # Enable legacy XSS filter header for older browsers (non-breaking)
        response.headers.setdefault('X-XSS-Protection', '1; mode=block')
        return response 