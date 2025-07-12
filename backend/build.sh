#!/usr/bin/env bash
# Build script pro Render

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating uploads directory..."
mkdir -p uploads

echo "Build completed successfully!" 