"""WSGI config for the alumni management backend."""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = get_wsgi_application()
