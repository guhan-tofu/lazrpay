from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse
# this is for extra security headers with MoonPay CSP support
class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        response.headers.setdefault('X-XSS-Protection', '1; mode=block')
        
        # Content Security Policy for MoonPay integration
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
            "https://static.moonpay.com "
            "https://verify.walletconnect.org "
            "https://cdn.tailwindcss.com "
            "https://cdnjs.cloudflare.com "
            "https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' "
            "https://fonts.googleapis.com "
            "https://cdnjs.cloudflare.com; "
            "font-src 'self' "
            "https://fonts.gstatic.com "
            "https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "frame-src 'self' "
            "https://sell-sandbox.moonpay.com "
            "https://sell.moonpay.com "
            "https://verify.walletconnect.org; "
            "connect-src 'self' "
            "https://api.moonpay.com "
            "https://sell-sandbox.moonpay.com "
            "https://sell.moonpay.com "
            "https://verify.walletconnect.org "
            "https://api.devnet.solana.com "
            "https://lazrpay.onrender.com; "
            "frame-ancestors 'self' "
            "https://sell-sandbox.moonpay.com "
            "https://sell.moonpay.com;"
        )
        
        response.headers['Content-Security-Policy'] = csp_policy
        
        return response 