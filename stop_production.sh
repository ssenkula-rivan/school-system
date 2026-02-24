#!/bin/bash

echo "Stopping School Management System..."

# Kill all gunicorn processes
pkill -f gunicorn

echo "Server stopped successfully!"
