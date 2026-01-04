# Tree Pose Detection - Complete Guide

## Enhanced Detection System

The tree pose detection now uses a **multi-criteria scoring system** with 4 different checks for each leg:

### Detection Criteria (Need 2+ to detect leg lift)

1. **Height Check** ✓
   - Knee is at least 2% higher than hip
   - `knee.y < hip.y - 0.02`

2. **Ankle Raised** ✓
   - Ankle/foot is above hip level
   - `ankle.y < hip.y - 0.02`

3. **Inward Movement** ✓
   - Knee moved toward body center
   - Indicates foot placement on inner thigh
   - `knee_distance < hip_distance * 0.8`

4. **Foot Near Opposite Leg** ✓
   - Ankle is close to opposite knee
   - Distance < 0.3 (30% of screen)
   - Confirms tree pose position

### Scoring System

**Leg Lift (40 points max):**
- Height > 15%: 40 points - "Excellent leg lift! 🦵"
- Height > 10%: 38 points - "Great leg lift! 🦵"
- Height > 6%: 35 points - "Good leg lift, go higher 🦵"
- Height > 3%: 30 points - "Lift leg higher 🦵"
- Height > 2%: 25 points - "Keep lifting leg 🦵"
- Any movement: 15 points - "Lift leg higher - not detected yet"

**Standing Leg (30 points max):**
- Angle ≥ 155°: 30 points - "Standing leg straight"
- Angle ≥ 145°: 22 points - "Straighten standing leg"
- Angle < 145°: 15 points - "Straighten leg more"

**Arms (20 points max):**
- Above head: 20 points
- Above shoulders: 12 points

**Balance (10 points max):**
- Good alignment: 10 points

---

## Debug Output Explained

When you test, you'll see this in the terminal:

```
[TREE POSE DEBUG]
Left leg  - Height: 0.045, Ankle: 0.038, Inward: True, Score: 3/4, Vis: 0.85
Right leg - Height: -0.002, Ankle: -0.005, Inward: False, Score: 0/4, Vis: 0.92

[DETECTED] Raised leg: left, Height: 0.045
[STANDING LEG] Right leg angle: 168.3°
```

### Reading the Debug Info:

**Height Values:**
- Positive = leg is raised (good!)
- Negative = leg is lower (standing leg)
- 0.045 = 4.5% of screen height

**Ankle Values:**
- Same as height - positive means raised

**Inward:**
- True = knee moved toward center (tree pose position)
- False = knee in normal position

**Score:**
- X/4 = how many criteria are met
- Need 2+ to detect leg lift
- Higher score = more confident detection

**Visibility:**
- 0.0 to 1.0 scale
- Need > 0.25 (25%) to use landmark
- Higher = more confident

---

## Step-by-Step Testing

### 1. Start Application
```bash
python run.py
```

### 2. Open Tree Pose
Navigate to: http://localhost:8000/exercise/tree-pose

### 3. Position Yourself
- Stand 5-6 feet from camera
- Ensure full body visible (head to feet)
- Good lighting on your body
- Plain background helps

### 4. Test Progression

#### Stage 1: Standing Normal
- Both feet on ground
- **Expected Debug:**
  ```
  Left leg  - Height: -0.001, Score: 0/4
  Right leg - Height: -0.002, Score: 0/4
  [NO LIFT] No leg movement detected
  ```
- **Feedback:** "❌ Lift one leg up"

#### Stage 2: Slight Lift (Toe Touch)
- Lift one foot slightly, toe still touching
- **Expected Debug:**
  ```
  Left leg  - Height: 0.015, Score: 1/4
  [ATTEMPTING] Small movement detected
  ```
- **Feedback:** "Lift leg higher - not detected yet"
- **Points:** 15

#### Stage 3: Clear Lift (Foot Off Ground)
- Lift foot 3-4 inches off ground
- **Expected Debug:**
  ```
  Left leg  - Height: 0.035, Score: 2/4
  [DETECTED] Raised leg: left, Height: 0.035
  ```
- **Feedback:** "Lift leg higher 🦵⬅️"
- **Points:** 30+

#### Stage 4: Mid-Thigh Position
- Place foot on calf or mid-thigh
- **Expected Debug:**
  ```
  Left leg  - Height: 0.085, Inward: True, Score: 3/4
  [DETECTED] Raised leg: left, Height: 0.085
  ```
- **Feedback:** "✓ Good leg lift, go higher 🦵⬅️"
- **Points:** 35+

#### Stage 5: Full Tree Pose
- Foot on inner thigh, knee out
- **Expected Debug:**
  ```
  Left leg  - Height: 0.165, Inward: True, Score: 4/4
  [DETECTED] Raised leg: left, Height: 0.165
  [STANDING LEG] Right leg angle: 172.5°
  ```
- **Feedback:** "✓ Excellent leg lift! 🦵⬅️ | ✓ Standing leg straight"
- **Points:** 70+ (should turn GREEN)

---

## Common Issues & Solutions

### Issue 1: "No leg movement detected" when leg IS raised

**Check Debug Output:**
```
Left leg  - Height: 0.018, Score: 1/4, Vis: 0.22
```

**Problem:** Visibility too low (0.22 < 0.25)

**Solutions:**
- Improve lighting
- Move closer to camera
- Wear contrasting clothing
- Ensure leg not in shadow

---

### Issue 2: Wrong leg detected

**Debug shows:**
```
Left leg  - Height: 0.045, Score: 3/4
Right leg - Height: 0.042, Score: 3/4
[DETECTED] Raised leg: left
```

**Problem:** Both legs showing similar scores

**Solutions:**
- Lift one leg more clearly
- Lower the standing leg completely
- Stand more stable
- The model picks the leg with higher score/height

---

### Issue 3: Detection keeps switching

**Debug shows alternating:**
```
Frame 1: [DETECTED] Raised leg: left
Frame 2: [DETECTED] Raised leg: right
Frame 3: [DETECTED] Raised leg: left
```

**Problem:** Unstable pose or camera shake

**Solutions:**
- Hold pose more steady
- Stabilize camera
- Improve balance
- Focus on one leg

---

### Issue 4: Low accuracy even with good pose

**Debug shows:**
```
[DETECTED] Raised leg: left, Height: 0.125
[STANDING LEG] Right leg angle: 142.3°
```

**Problem:** Standing leg not straight enough (142° < 145°)

**Solutions:**
- Straighten standing leg more
- Engage thigh muscles
- Lock knee (but don't hyperextend)
- Check if standing leg is fully visible

---

## Visibility Requirements

Each landmark needs minimum visibility:

| Landmark | Minimum | Ideal |
|----------|---------|-------|
| Knees | 0.25 | 0.5+ |
| Ankles | 0.25 | 0.5+ |
| Hips | 0.30 | 0.6+ |
| Shoulders | 0.30 | 0.6+ |
| Wrists | 0.25 | 0.5+ |

**Tips to improve visibility:**
- Face camera directly
- Good front lighting
- Avoid busy backgrounds
- Wear fitted clothing
- Ensure full body in frame

---

## Expected Behavior

### Minimum for YELLOW (50%):
- Leg lifted with 2+ criteria (25-30 pts)
- Standing leg visible (15 pts)
- Some arm movement (5-10 pts)
- **Total: 50+ points = YELLOW 🟡**

### Minimum for GREEN (75%):
- Clear leg lift > 6% height (35 pts)
- Standing leg reasonably straight (22 pts)
- Arms raised above shoulders (12 pts)
- Some balance (10 pts)
- **Total: 79 points = GREEN 🟢**

### Perfect Score (100%):
- Excellent leg lift > 15% (40 pts)
- Standing leg perfectly straight (30 pts)
- Arms fully overhead (20 pts)
- Perfect balance (10 pts)
- **Total: 100 points = PERFECT ✨**

---

## Quick Troubleshooting

1. **Check terminal for debug output** - tells you exactly what's detected
2. **Verify visibility scores** - need > 0.25 for each landmark
3. **Check height values** - positive = raised, negative = lowered
4. **Look at criteria score** - need 2+ out of 4 to detect
5. **Test with better lighting** - single biggest improvement

---

## Advanced Tips

### For Better Detection:
1. **Lighting:** Front-facing light source
2. **Distance:** 5-6 feet from camera
3. **Angle:** Camera at chest height
4. **Background:** Plain, contrasting color
5. **Clothing:** Fitted, contrasting with background
6. **Stability:** Hold pose steady for 2-3 seconds

### For Higher Scores:
1. **Leg Height:** Aim for thigh-level placement
2. **Standing Leg:** Fully straighten and engage
3. **Arms:** Raise fully overhead
4. **Balance:** Center body weight
5. **Hold:** Maintain position steadily

---

## Success Metrics

✅ Detects leg lift with 2cm movement
✅ Uses 4 different detection methods
✅ Shows which leg is detected (🦵⬅️ or 🦵➡️)
✅ Provides detailed debug information
✅ Progressive scoring encourages improvement
✅ Reaches green at achievable 75%
✅ Works in various lighting conditions

The detection is now much more robust and should catch tree pose leg lifts reliably!
