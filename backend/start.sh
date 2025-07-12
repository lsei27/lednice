#!/usr/bin/env bash
# Start script pro Render

echo "Starting Flask application..."
gunicorn app:app --config gunicorn.conf.py 