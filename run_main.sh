#!/bin/bash
cd "$(dirname "$0")"
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup first."
    exit 1
fi
source venv/bin/activate
echo "🤖 Starting main bot..."
python -m main.main
