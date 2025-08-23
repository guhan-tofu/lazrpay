import os
from django.core.wsgi import get_wsgi_application
# this is the wsgi entry point
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lazr.settings")
application = get_wsgi_application()
