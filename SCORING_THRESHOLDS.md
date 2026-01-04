# Scoring Thresholds

## Color Indicators

### 🔴 Red (0-49%)
- Incorrect form or pose not detected
- No countdown starts
- User needs to adjust position

### 🟡 Yellow (50-69%)
- Close to correct form
- Getting there but not quite right
- No countdown yet
- Keep adjusting

### 🟢 Green (70-100%)
- Correct form achieved!
- Countdown starts automatically
- Hold for 5 seconds to complete
- Exercise will finish when countdown reaches 0

## Countdown Trigger

**Countdown starts when:**
- Accuracy ≥ 70%
- Color = Green
- User must hold this position for 5 seconds

**Countdown stops when:**
- Accuracy drops below 70%
- Color changes from green
- User loses correct form

## Exercise-Specific Scoring

### Tree Pose (100 points total)

**Raised Leg (40 points):**
- Excellent lift (>15% height): 40 pts
- Great lift (>10% height): 38 pts
- Good lift (>6% height): 35 pts
- Fair lift (>3% height): 30 pts
- Minimal lift (>2% height): 25 pts

**Standing Leg (30 points):**
- Perfect straight (≥155°): 30 pts
- Almost straight (≥145°): 22 pts
- Needs work (<145°): 15 pts

**Arms Raised (20 points):**
- Above head: 20 pts
- Above shoulders: 12 pts

**Balance (10 points):**
- Good alignment: 10 pts

**Minimum for GREEN (70%):**
- Leg lifted decently (30-35 pts)
- Standing leg reasonably straight (22 pts)
- Arms raised (12 pts)
- Some balance (10 pts)
- **Total: 74 points = GREEN ✅**

### Warrior II (100 points total)

**Front Knee Bend (40 points):**
- Perfect 90° (80-100°): 40 pts
- Excellent (70-110°): 30 pts
- Good (60-120°): 20 pts

**Back Leg Straight (30 points):**
- Perfect (≥160°): 30 pts
- Good (≥150°): 20 pts

**Arms Extended (20 points):**
- Perfect horizontal: 20 pts
- Arms straight: 12 pts

**Torso Upright (10 points):**
- Good posture: 10 pts

**Minimum for GREEN (70%):**
- Good knee bend (30 pts)
- Back leg straight (20 pts)
- Arms extended (12 pts)
- Upright torso (10 pts)
- **Total: 72 points = GREEN ✅**

### Plank (100 points total)

**Body Alignment (50 points):**
- Perfect straight line: 50 pts
- Good alignment: 35 pts

**Arms Straight (25 points):**
- Perfect (≥160°): 25 pts
- Good (≥150°): 18 pts

**Position (25 points):**
- Good height: 25 pts

**Minimum for GREEN (70%):**
- Good alignment (35 pts)
- Arms straight (25 pts)
- Good position (25 pts)
- **Total: 85 points = GREEN ✅**

## Tips to Reach Green

### For Tree Pose:
1. Lift leg to at least calf height (gets you 30+ pts)
2. Straighten standing leg fully (22-30 pts)
3. Raise arms above shoulders (12-20 pts)
4. Keep body centered (10 pts)

### For Warrior II:
1. Bend front knee to ~90° (30-40 pts)
2. Keep back leg straight (20-30 pts)
3. Extend arms horizontally (12-20 pts)
4. Keep torso upright (10 pts)

### For Plank:
1. Keep body in straight line (35-50 pts)
2. Straighten arms (18-25 pts)
3. Maintain proper height (25 pts)

## Calibration

If you've run the calibration script with your reference image:
- Thresholds are adjusted to match your reference
- Scoring is based on your specific pose
- Green threshold remains at 70%

## Summary

✅ **70% = GREEN** = Countdown starts
🟡 **50-69% = YELLOW** = Keep adjusting
🔴 **0-49% = RED** = Incorrect form

The 70% threshold makes it achievable while still requiring proper form!
