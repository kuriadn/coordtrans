"""Settings for Docker — app in container, PostgreSQL/PostGIS on the host."""
from .base import *  # NOQA
import logging.config
import os
import socket
import sys

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0", "web", "survey.fayvad.com"],
)

CSRF_TRUSTED_ORIGINS = env.list(
    "CSRF_TRUSTED_ORIGINS",
    default=["https://survey.fayvad.com", "http://localhost:8015"],
)

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

if DEBUG:
    TEMPLATES[0]["OPTIONS"].update({"debug": True})
    INSTALLED_APPS += ("debug_toolbar",)
    MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    THUMBNAIL_DEBUG = True

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = ["127.0.0.1", "0.0.0.0"] + [
        ip[: ip.rfind(".")] + ".1" for ip in ips
    ]

STATIC_ROOT = join(BASE_DIR, "staticfiles")
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

LOGFILE_ROOT = join(dirname(BASE_DIR), "logs")
if not exists(LOGFILE_ROOT):
    os.makedirs(LOGFILE_ROOT)

LOGGING_CONFIG = None
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(pathname)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        # Gunicorn + public internet: bots probe /.env, /.git, etc. — skip 404 noise.
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

if "celery" in sys.argv[0]:
    DEBUG = False

logging.config.dictConfig(LOGGING)
