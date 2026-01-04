# Quick Start Guide

## The Problem
You're seeing dependency conflicts because your system has TensorFlow and other packages that require different protobuf versions than MediaPipe needs.

## The Solution
Create an isolated virtual environment for this project.

## Steps

### 1. Create and activate a virtual environment

```bash
# Create virtual environment
python3 -m venv venv_fitness

# Activate it
source venv_fitness/bin/activate
```

### 2. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run the application

```bash
python run.py
```

### 4. Open in browser

Navigate to: http://localhost:8000

### 5. When done, deactivate

```bash
deactivate
```

## Alternative: Use the setup script

```bash
# Run setup (it will create venv if needed)
bash setup.sh

# If it creates a new venv, activate it:
source venv_fitness/bin/activate

# Run setup again to install dependencies
bash setup.sh

# Start the app
python run.py
```

## Troubleshooting

**Still seeing protobuf errors?**
- Make sure you're in the virtual environment (you should see `(venv_fitness)` in your prompt)
- Try: `pip list | grep protobuf` - should show version 4.25.3
- If not, run: `pip install protobuf==4.25.3 --force-reinstall`

**Camera not working?**
- Grant camera permissions in your browser
- Make sure no other app is using the camera
- Try refreshing the page

**WebSocket connection failed?**
- Check if port 8000 is available
- Try restarting the server
