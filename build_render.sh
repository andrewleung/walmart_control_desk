#!/bin/sh
set -eu

mkdir -p data/uploads
python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
