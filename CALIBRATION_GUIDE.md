# Tree Pose Calibration Guide

## Overview

This process analyzes your reference image `tree pose.jpg` to extract exact pose parameters and calibrates the detection model to match it.

## Steps

### 1. Analyze Reference Image

```bash
python analyze_reference_pose.py
```

This will:
- Load `tree pose.jpg`
- Detect the pose using MediaPipe
- Extract all key measurements:
  - Raised leg height
  - Standing leg angle
  - Knee position (inward/outward)
  - Arm positions
  - Body alignment
- Generate calibration parameters
- Save to `tree_pose_calibration.json`
- Create annotated image `tree_pose_analyzed.jpg`

### 2. Review Analysis

Check the terminal output for:
- Which leg is raised
- Exact height measurements
- Standing leg angle
- Recommended thresholds

Example output:
```
📊 POSE ANALYSIS
================================================================

1️⃣  LEG ANALYSIS:
------------------------------------------------------------
Left knee height:   +0.1234 (vis: 0.95)
Right knee height:  -0.0012 (vis: 0.98)

✓ Raised leg: LEFT
✓ Raised height: 0.1234 (12.3% of screen)

2️⃣  STANDING LEG ANGLE:
------------------------------------------------------------
Right leg angle: 168.5°

🎯 RECOMMENDED DETECTION PARAMETERS
================================================================
Raised Leg Height:
  Minimum:   0.0617
  Ideal:     0.1234
  Excellent: 0.1357
```

### 3. Apply Calibration

```bash
python apply_calibration.py
```

This will:
- Load the calibration parameters
- Update `app/services/pose_detector.py`
- Set thresholds based on your reference image
- Configure detection to match the reference pose

### 4. Test

```bash
python run.py
```

Open http://localhost:8000/exercise/tree-pose and test!

The model will now use thresholds calibrated to your reference image.

## What Gets Calibrated

### Raised Leg Height
- **Minimum**: 50% of reference height (to allow beginners)
- **Ideal**: Exact height from reference image
- **Excellent**: 110% of reference height

### Standing Leg Angle
- **Minimum**: Reference angle - 15°
- **Ideal**: Exact angle from reference
- **Maximum**: 180° (perfectly straight)

### Knee Position
- Inward ratio from reference
- Threshold for detecting tree pose position

### Arms
- Minimum raise height
- Ideal raise height
- Whether arms should be above head

### Balance
- Maximum allowed body offset

## Files Generated

1. **tree_pose_calibration.json** - Calibration parameters
2. **tree_pose_analyzed.jpg** - Annotated reference image with skeleton

## Troubleshooting

### "No pose detected in image"
- Ensure full body is visible in image
- Check image quality and lighting
- Try a clearer reference image

### "Could not find tree pose section"
- The pose_detector.py structure may have changed
- Manually update the thresholds using the JSON values

### Detection still not working
- Check terminal debug output
- Compare your pose to the reference
- Verify visibility scores > 0.25
- Ensure good lighting

## Advanced: Manual Calibration

If you want to manually adjust, edit `tree_pose_calibration.json`:

```json
{
  "tree_pose": {
    "raised_leg": {
      "min_height": 0.05,      // Lower = easier detection
      "ideal_height": 0.12,    // Target height
      "excellent_height": 0.15 // Perfect pose
    },
    "standing_leg": {
      "min_angle": 150,        // Minimum straightness
      "ideal_angle": 168       // Target angle
    }
  }
}
```

Then run `python apply_calibration.py` again.

## Benefits

✅ Detection tuned to YOUR reference image
✅ Consistent with your pose standards
✅ Adjustable thresholds
✅ Scientific calibration process
✅ Reproducible results

The model will now detect poses that match your reference image!
