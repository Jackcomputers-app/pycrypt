#!/bin/bash

echo "Activating virtual environment..."
source venv/bin/activate

# Start Gunicorn with config
echo "Starting Gunicorn with SSL for domain: $DOMAIN"
venv/bin/gunicorn app:app -c gunicorn_config.py

# Optional: log file (uncomment to enable)
# >> logs/gunicorn.log 2>&1
