#!/bin/bash

echo "🏋️ Setting up Exercise Body Tracker..."

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate beep sound (optional)
echo "Generating beep sound..."
pip install scipy 2>/dev/null
python generate_beep.py 2>/dev/null || echo "Skipping beep generation (scipy not available)"

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Run the server: python app/main.py"
echo "  2. Open browser: http://localhost:8000"
echo ""
