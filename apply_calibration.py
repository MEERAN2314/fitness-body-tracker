#!/usr/bin/env python3
"""
Apply calibration parameters from reference image to pose detector
"""

import json
import sys
import re

def apply_calibration():
    """Apply calibration parameters to pose detector"""
    
    print("🎯 Applying Tree Pose Calibration")
    print("=" * 60)
    
    # Load calibration parameters
    try:
        with open('tree_pose_calibration.json', 'r') as f:
            params = json.load(f)
    except FileNotFoundError:
        print("❌ Error: tree_pose_calibration.json not found")
        print("Please run: python analyze_reference_pose.py first")
        return False
    
    print("✓ Loaded calibration parameters")
    
    tree_params = params['tree_pose']
    
    # Extract values
    min_height = tree_params['raised_leg']['min_height']
    ideal_height = tree_params['raised_leg']['ideal_height']
    excellent_height = tree_params['raised_leg']['excellent_height']
    min_angle = tree_params['standing_leg']['min_angle']
    ideal_angle = tree_params['standing_leg']['ideal_angle']
    
    print(f"\n📊 Calibration Values:")
    print(f"  Min height:       {min_height:.4f}")
    print(f"  Ideal height:     {ideal_height:.4f}")
    print(f"  Excellent height: {excellent_height:.4f}")
    print(f"  Min angle:        {min_angle:.1f}°")
    print(f"  Ideal angle:      {ideal_angle:.1f}°")
    
    # Read current pose detector
    with open('app/services/pose_detector.py', 'r') as f:
        code = f.read()
    
    # Replace the hardcoded thresholds
    replacements = [
        # Height thresholds in criteria
        (r"'height': left_knee_height > 0\.02,", 
         f"'height': left_knee_height > {min_height:.4f},  # Calibrated"),
        (r"'height': right_knee_height > 0\.02,", 
         f"'height': right_knee_height > {min_height:.4f},  # Calibrated"),
        (r"'ankle_raised': left_ankle_height > 0\.02,", 
         f"'ankle_raised': left_ankle_height > {min_height:.4f},  # Calibrated"),
        (r"'ankle_raised': right_ankle_height > 0\.02,", 
         f"'ankle_raised': right_ankle_height > {min_height:.4f},  # Calibrated"),
        
        # Height scoring thresholds
        (r"if max_height > 0\.15:", 
         f"if max_height > {excellent_height:.4f}:  # Calibrated: excellent"),
        (r"elif max_height > 0\.10:", 
         f"elif max_height > {ideal_height:.4f}:  # Calibrated: ideal"),
        (r"elif max_height > 0\.06:", 
         f"elif max_height > {ideal_height * 0.6:.4f}:  # Calibrated: good"),
        (r"elif max_height > 0\.03:", 
         f"elif max_height > {min_height * 1.5:.4f}:  # Calibrated: fair"),
        
        # Standing leg angle thresholds
        (r"if angle >= 155:", 
         f"if angle >= {ideal_angle:.1f}:  # Calibrated: ideal"),
        (r"elif angle >= 145:", 
         f"elif angle >= {min_angle:.1f}:  # Calibrated: minimum"),
    ]
    
    # Apply replacements
    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, code):
            code = re.sub(pattern, replacement, code)
            modified = True
    
    if modified:
        # Write back
        with open('app/services/pose_detector.py', 'w') as f:
            f.write(code)
        
        print("\n✅ Successfully applied calibration!")
        print("\nUpdated thresholds:")
        print(f"  ✓ Minimum height detection: {min_height:.4f}")
        print(f"  ✓ Ideal height scoring: {ideal_height:.4f}")
        print(f"  ✓ Excellent height scoring: {excellent_height:.4f}")
        print(f"  ✓ Standing leg angles: {min_angle:.1f}° - {ideal_angle:.1f}°")
        
        print("\n🚀 Next steps:")
        print("  1. Restart the application: python run.py")
        print("  2. Test tree pose at: http://localhost:8000/exercise/tree-pose")
        print("  3. Watch terminal for calibrated debug output")
        
        return True
    else:
        print("\n⚠️  Warning: No thresholds were updated")
        print("The pose_detector.py structure may have changed.")
        print("\nYou can manually update these values in pose_detector.py:")
        print(f"  - Change 0.02 to {min_height:.4f}")
        print(f"  - Change 0.15 to {excellent_height:.4f}")
        print(f"  - Change 0.10 to {ideal_height:.4f}")
        print(f"  - Change 155 to {ideal_angle:.1f}")
        print(f"  - Change 145 to {min_angle:.1f}")
        return False

if __name__ == "__main__":
    success = apply_calibration()
    sys.exit(0 if success else 1)
