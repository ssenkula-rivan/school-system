#!/bin/bash

echo "Starting School Management System in Production Mode..."

# Activate virtual environment
source venv/bin/activate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Start Gunicorn server
echo "Starting Gunicorn server..."
gunicorn workplace_system.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --daemon

echo "Server started successfully!"
echo "Access the system at: http://localhost:8000"
echo "To stop the server, run: pkill gunicorn"
