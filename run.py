#!/usr/bin/env python3
"""
Run script for Exercise Body Tracker
This ensures proper Python path setup
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    print("🏋️ Starting Exercise Body Tracker...")
    print(f"📁 Project root: {project_root}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("Press CTRL+C to stop\n")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
