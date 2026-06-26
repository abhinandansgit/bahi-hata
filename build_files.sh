#!/bin/bash

echo "Installing Python dependencies..."
python -m pip install -r requirements.txt

# Ensure the STATIC_ROOT directory exists
mkdir -p staticfiles

echo "Running Django collectstatic..."
python manage.py collectstatic --noinput --clear || true

# Copy any static assets from the project static folder into staticfiles (fallback)
if [ -d static ]; then
  cp -r static/* staticfiles/ || true
fi

# Add placeholder to avoid empty directory warnings
echo "keep" > staticfiles/.keep

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput || echo "WARNING: Migrations failed (will retry at runtime)"

echo "Build complete!"
