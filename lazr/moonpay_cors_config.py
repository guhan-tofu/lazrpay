# MoonPay CORS Configuration
# This file contains CORS settings specifically for MoonPay integration

# MoonPay domains that need CORS access
MOONPAY_CORS_DOMAINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "https://sell-sandbox.moonpay.com",
    "https://sell.moonpay.com",
    "https://verify.walletconnect.org",
    "https://api.moonpay.com",
    "https://static.moonpay.com",
]

# MoonPay CSP domains
MOONPAY_CSP_DOMAINS = {
    "script_src": [
        "https://static.moonpay.com",
        "https://verify.walletconnect.org",
        "https://cdn.tailwindcss.com",
        "https://cdnjs.cloudflare.com",
        "https://fonts.googleapis.com",
    ],
    "style_src": [
        "https://fonts.googleapis.com",
        "https://cdnjs.cloudflare.com",
    ],
    "font_src": [
        "https://fonts.gstatic.com",
        "https://cdnjs.cloudflare.com",
    ],
    "frame_src": [
        "https://sell-sandbox.moonpay.com",
        "https://sell.moonpay.com",
        "https://verify.walletconnect.org",
    ],
    "connect_src": [
        "https://api.moonpay.com",
        "https://sell-sandbox.moonpay.com",
        "https://sell.moonpay.com",
        "https://verify.walletconnect.org",
        "https://api.devnet.solana.com",
    ],
    "frame_ancestors": [
        "https://sell-sandbox.moonpay.com",
        "https://sell.moonpay.com",
    ],
}

# MoonPay API endpoints
MOONPAY_API_ENDPOINTS = {
    "sandbox": {
        "base_url": "https://api.moonpay.com",
        "sell_url": "https://sell-sandbox.moonpay.com",
        "webhook_url": "https://api.moonpay.com/v3/webhooks",
    },
    "production": {
        "base_url": "https://api.moonpay.com",
        "sell_url": "https://sell.moonpay.com",
        "webhook_url": "https://api.moonpay.com/v3/webhooks",
    }
}
