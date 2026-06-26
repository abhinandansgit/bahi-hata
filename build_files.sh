#!/bin/bash

# Set minimal Django environment for static collection
export DJANGO_SETTINGS_MODULE=bahihata.settings
export SECRET_KEY=placeholder-secret-key
export DEBUG=False
export ALLOWED_HOSTS="*"
# Use SQLite for static collection (fallback)
export DATABASE_URL=sqlite:///db.sqlite3

# Ensure the STATIC_ROOT directory exists
mkdir -p staticfiles

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

echo "Running Django collectstatic..."
# python manage.py collectstatic --noinput --clear || true
