#!/bin/bash

echo "🏋️ Clean Setup for Exercise Body Tracker"
echo "=========================================="
echo ""

# Check if venv_fitness exists
if [ -d "venv_fitness" ]; then
    echo "⚠️  Found existing venv_fitness directory"
    read -p "Remove it and create fresh? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old virtual environment..."
        rm -rf venv_fitness
    else
        echo "Keeping existing environment. Exiting."
        exit 0
    fi
fi

echo ""
echo "Step 1: Creating fresh virtual environment..."
python3 -m venv venv_fitness

if [ ! -d "venv_fitness" ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created"
echo ""

echo "Step 2: Activating virtual environment..."
source venv_fitness/bin/activate

echo "✓ Activated: $VIRTUAL_ENV"
echo ""

echo "Step 3: Upgrading pip..."
pip install --upgrade pip --quiet

echo "✓ Pip upgraded"
echo ""

echo "Step 4: Installing dependencies..."
echo "This may take a few minutes..."
pip install -r requirements.txt --quiet

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

echo "Step 5: Verifying installation..."
echo ""

# Check critical packages
echo "Checking package versions:"
pip show mediapipe | grep Version
pip show protobuf | grep Version
pip show fastapi | grep Version
pip show opencv-python | grep Version

echo ""
echo "✅ Setup complete!"
echo ""
echo "=========================================="
echo "To start the application:"
echo ""
echo "  1. Activate the environment:"
echo "     source venv_fitness/bin/activate"
echo ""
echo "  2. Run the app:"
echo "     python run.py"
echo ""
echo "  3. Open browser:"
echo "     http://localhost:8000"
echo ""
echo "=========================================="
