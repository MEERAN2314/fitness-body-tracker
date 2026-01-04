# Tree Pose Detection Testing Guide

## Improvements Made

### 1. **Multi-Criteria Detection**
The model now detects leg lift using THREE methods:
- **Vertical height**: Knee is higher than hip (even by 0.03 units)
- **Horizontal position**: Knee moved inward toward body center
- **Ankle position**: Raised foot is higher than hip level

### 2. **Lower Thresholds**
- Visibility requirement: 0.3 (was 0.4-0.5)
- Minimum height difference: 0.03 (was 0.05-0.08)
- Standing leg angle: 155° is perfect (was 160-170°)

### 3. **Progressive Scoring**
- Any leg movement > 0.01: 10 points
- Small lift > 0.03: 22-28 points
- Medium lift > 0.06: 35 points
- Good lift > 0.12: 40 points

### 4. **Better Feedback**
- Shows which leg is detected as raised
- Gives credit for attempting
- More encouraging messages

## How to Test

### Step 1: Start the Application
```bash
python run.py
```

### Step 2: Open Tree Pose Exercise
Navigate to: http://localhost:8000/exercise/tree-pose

### Step 3: Test Different Positions

#### Test A: Minimal Lift (Should detect)
1. Stand straight
2. Slightly bend one knee (just a few inches off ground)
3. **Expected**: Should get 22-28 points, yellow/green color
4. **Feedback**: "Lift leg higher" or "Keep lifting leg"

#### Test B: Medium Lift (Should detect easily)
1. Lift knee to mid-thigh level
2. **Expected**: Should get 35+ points, green color
3. **Feedback**: "Good leg lift, go higher"

#### Test C: Full Tree Pose (Should detect perfectly)
1. Place foot on inner thigh
2. Knee bent outward
3. **Expected**: Should get 40 points for leg, green color
4. **Feedback**: "Excellent leg lift"

#### Test D: Foot Placement (Alternative detection)
1. Place foot against standing leg (anywhere)
2. Even if knee isn't super high
3. **Expected**: Should detect via ankle position
4. **Feedback**: Should give credit

### Step 4: Check Debug Logs

Watch the terminal for debug output:
```
[DEBUG] Left knee height: 0.045, Right knee height: -0.002
[DEBUG] Left knee vis: 0.85, Right knee vis: 0.92
[DEBUG] Left ankle vis: 0.78, Right ankle vis: 0.88
```

This shows:
- Which leg has positive height (lifted)
- Visibility scores for each landmark
- Helps diagnose detection issues

## Common Issues & Solutions

### Issue: "Lift one leg up" even when leg is raised

**Possible causes:**
1. Leg not visible enough (check visibility in debug logs)
2. Not enough height difference
3. Camera angle too low/high

**Solutions:**
- Step back from camera
- Ensure full body visible
- Improve lighting
- Lift leg a bit higher
- Try moving knee more inward

### Issue: Detection switches between legs

**Cause:** Both legs showing slight movement

**Solution:** 
- Stand more stable on one leg
- Lift the raised leg more clearly
- The model will pick the leg with more height

### Issue: Low accuracy even with good pose

**Check:**
1. Are arms raised? (20 points)
2. Is standing leg straight? (30 points)
3. Is body balanced? (10 points)

## Expected Behavior

### Minimum to get GREEN (75%):
- Leg lifted (22-40 points)
- Standing leg reasonably straight (15-30 points)
- Arms raised (12-20 points)
- Some balance (0-10 points)
- **Total: 75+ points**

### What triggers countdown:
- Accuracy >= 75%
- Color = green
- Hold for 5 seconds

## Troubleshooting Commands

### If detection still not working:

1. **Check MediaPipe version:**
```bash
pip show mediapipe
```
Should be 0.10.14

2. **Check protobuf version:**
```bash
pip show protobuf
```
Should be 4.25.3

3. **Restart with clean environment:**
```bash
deactivate
source venv_fitness/bin/activate
python run.py
```

4. **Test with better lighting:**
- Face a window or light source
- Avoid backlighting
- Use well-lit room

## Debug Mode

To see more detailed detection info, the console will show:
- Knee heights for both legs
- Visibility scores
- Which leg is detected as raised
- Angle calculations

Watch the terminal while testing to understand what the model sees.

## Success Criteria

✅ Detects leg lift with minimal movement (3cm height)
✅ Gives progressive feedback as you lift higher
✅ Works with different tree pose variations
✅ Reaches green status achievably
✅ Provides clear, actionable feedback

If you're still having issues, share the debug output and I'll tune it further!
