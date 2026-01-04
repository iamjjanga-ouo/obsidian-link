#!/bin/bash
set -e

# Cloudflare setup script execution helper

# Move to current script directory
cd "$(dirname "$0")"

# Check environment variables
if [ -z "$CF_API_TOKEN" ] || [ -z "$CF_ZONE_ID" ]; then
    echo "⚠️  Environment variables are not set."
    echo ""
    echo "Set environment variables with the following commands:"
    echo "  export CF_API_TOKEN='your-token'"
    echo "  export CF_ZONE_ID='your-zone-id'"
    echo ""
    echo "Or create a .env file:"
    echo "  cp .env.example .env"
    echo "  # Edit .env file and enter values"
    echo ""

    if [ -f .env ]; then
        echo "✓ Found .env file. Loading environment variables..."
        set -a
        source .env
        set +a
    else
        echo "❌ .env file not found."
        exit 1
    fi
fi

# Check dependencies
if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Running uv sync..."
    uv sync
fi

# Run script
echo "Running Cloudflare setup script..."
echo ""
uv run python setup_cloudflare.py
