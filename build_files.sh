#!/usr/bin/env bash
# Build script for Vercel Free Serverless Deployment
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static assets with WhiteNoise..."
echo "Running database migrations..."
python3 manage.py migrate

echo "Seeding initial database content..."
python3 bahihata/seed.py

echo "Build complete!"

