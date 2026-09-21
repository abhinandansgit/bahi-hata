#!/usr/bin/env bash
# Build script for Vercel Free Serverless Deployment
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Collecting static assets with WhiteNoise..."
python3 manage.py collectstatic --noinput --clear

echo "Build complete!"
