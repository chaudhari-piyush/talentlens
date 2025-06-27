#!/usr/bin/env bash
# Build script for Render deployment

set -e

echo "Starting build process..."

# Install Python dependencies using pip
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements-render.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Build completed successfully!"