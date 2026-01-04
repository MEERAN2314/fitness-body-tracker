#!/bin/bash

echo "🏋️ Setting up Exercise Body Tracker..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Not in a virtual environment. Creating one..."
    
    # Create virtual environment
    python3 -m venv venv_fitness
    
    echo "✓ Virtual environment created: venv_fitness"
    echo ""
    echo "Please activate it and run this script again:"
    echo "  source venv_fitness/bin/activate"
    echo "  bash setup.sh"
    echo ""
    exit 0
fi

echo "✓ Virtual environment detected: $VIRTUAL_ENV"
echo ""

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
echo "  python run.py"
echo ""
echo "Then open browser: http://localhost:8000"
echo ""
