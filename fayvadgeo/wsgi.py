"""
WSGI config for fayvadgeo project.
"""
import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "fayvadgeo.settings.production"
)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from django.conf import settings

if settings.DEBUG:
    try:
        import django.views.debug
        from werkzeug.debug import DebuggedApplication

        def null_technical_500_response(request, exc_type, exc_value, tb):
            raise exc_value.with_traceback(tb)

        django.views.debug.technical_500_response = null_technical_500_response
        application = DebuggedApplication(
            application,
            evalex=True,
            pin_security=False,
        )
    except ImportError:
        pass
