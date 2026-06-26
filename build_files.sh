#!/bin/bash
echo "Building Frontend React App..."
cd frontend
npm install
npm run build
cd ..

echo "Installing Python dependencies..."
python3 -m pip install -r requirements.txt

echo "Running Django collectstatic..."
python3 manage.py collectstatic --noinput --clear
