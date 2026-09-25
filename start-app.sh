#!/bin/bash
set -e  # Exit immediately on error

python manage.py migrate
python manage.py collectstatic --noinput

# Run using uvicorn for ASGI production
uvicorn buildiq.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --loop uvloop \
    --http httptools \
    --workers 1 \
    --log-level info
