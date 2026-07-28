#!/bin/sh
set -eu

mkdir -p data/uploads
python manage.py migrate --noinput
python manage.py seed_synthetic_demo
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}" --workers 2 --timeout 120
