#!/bin/bash
set -e

echo "📦 Installing maru-deep-pro-search..."
python3 -m pip install --user maru-deep-pro-search

echo "🚀 Running setup wizard..."
maru-deep-pro-search setup

echo "✅ Done! Your AI agent is now configured."
