"""
WSGI config for pycontw2018 project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "pycontw2018.settings.local"
)

application = get_wsgi_application()

# Wrap werkzeug debugger if DEBUG is on
from django.conf import settings
if settings.DEBUG and settings.WERKZEUG_DEBUG:
    try:
        import django.view.debug
        import six
        from werkzeug.debug import DebuggedApplication

        def null_technical_500_response(request, exc_type, exc_value, tb):
            six.reraise(exc_type, exc_value, tb)

        django.views.debug.technical_500_reponse = null_technical_500_response
        application = DebuggedApplication(application, evalex=True)
    except ImportError:
        pass
