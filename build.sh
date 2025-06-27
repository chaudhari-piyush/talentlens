#!/usr/bin/env bash
# Build script for Render deployment

set -e

echo "Starting build process..."

# Ensure we're using a clean pip environment
echo "Setting up pip environment..."
pip install --upgrade pip wheel setuptools

# Install dependencies one by one to better handle issues
echo "Installing core dependencies..."

# Install packages that commonly have binary wheels
pip install --upgrade \
    cryptography \
    psycopg2-binary \
    numpy \
    pillow

# Install the rest of the dependencies
echo "Installing remaining dependencies..."
pip install -r requirements-render.txt

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Build completed successfully!"