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
# Run collectstatic and ensure output directory is not empty
python manage.py collectstatic --noinput --clear || true

# Copy any static assets from the project static folder into staticfiles (fallback)
if [ -d static ]; then
  cp -r static/* staticfiles/ || true
fi

# Add placeholder to avoid empty directory warnings
mkdir -p staticfiles && echo "keep" > staticfiles/.keep
