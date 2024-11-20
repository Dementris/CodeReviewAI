#!/bin/sh
set -e

# Run custom management command
echo "Running custom management command..."
poetry lock --no-update
poetry install --without dev
# Run the WSGI server
echo "Starting ASGI server..."
exec "$@"