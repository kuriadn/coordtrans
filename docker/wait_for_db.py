#!/usr/bin/env python
"""Block until PostgreSQL on the host accepts connections."""
import os
import sys
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.environ.get("DJANGO_SETTINGS_MODULE", "fayvadgeo.settings.docker"))
django.setup()

from django.db import connection
from django.db.utils import OperationalError

max_attempts = int(os.environ.get("DB_WAIT_ATTEMPTS", "30"))
delay = float(os.environ.get("DB_WAIT_DELAY", "2"))

for attempt in range(1, max_attempts + 1):
    try:
        connection.ensure_connection()
        print("Database is ready.")
        sys.exit(0)
    except OperationalError as exc:
        print(f"Database not ready ({attempt}/{max_attempts}): {exc}")
        time.sleep(delay)

print("Could not connect to the database.", file=sys.stderr)
sys.exit(1)
