#!/usr/bin/env bash
# Build script for Render deployment

# Upgrade pip and install wheel
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

# Run any initialization scripts if needed
echo "Build completed successfully"