import os
from django.core.asgi import get_asgi_application
# this is the asgi entry point
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lazr.settings")
application = get_asgi_application()
