#!/bin/bash
# Render startup script
echo "Starting Pong Royale server..."
pip install --upgrade pip
pip install -r requirements.txt
gunicorn --worker-class gevent -w 1 --bind 0.0.0.0:$PORT wsgi:app