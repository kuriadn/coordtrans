#!/bin/sh
set -e

echo "Waiting for database..."
python docker/wait_for_db.py

python manage.py migrate --noinput

python manage.py collectstatic --noinput

exec "$@"
