# Tree Pose (Vrksasana) - Detection Reference

## Official Definition (from poses.json)

**Description:** "Stand on one leg with the other foot placed on the inner thigh"

**Instructions:**
1. Stand straight with feet together
2. Shift weight to your right foot (or left)
3. Place left foot on right inner thigh
4. Bring hands together at chest or raise above head
5. Hold the position steady

**Original Keypoints:**
- Standing leg angle: 170-180° (straight)
- Bent knee angle: 80-100° (bent outward)
- Arms raised: true
- Balance tolerance: 0.15

---

## What the Model Currently Detects

### 1. **Raised Leg Detection (40 points)**

The model looks for THREE indicators that a leg is raised:

#### A. Vertical Height
```
knee.y < hip.y - 0.03
```
- Knee is at least 3% higher than hip in screen coordinates
- Works for any height of leg lift

#### B. Horizontal Position (Inward Movement)
```
knee is closer to body center than hip
```
- Detects when knee moves inward (toward center line)
- Key for tree pose where foot is on inner thigh

#### C. Ankle Position
```
ankle.y < hip.y
```
- Raised foot/ankle is above hip level
- Catches cases where knee detection is occluded

**Scoring:**
- Height > 0.12 (12% of screen): 40 points - "Excellent leg lift"
- Height > 0.06 (6% of screen): 35 points - "Good leg lift, go higher"
- Height > 0.03 (3% of screen): 28 points - "Lift leg higher"
- Any movement > 0.01: 10 points - "Keep lifting leg"

### 2. **Standing Leg Straight (30 points)**

```
angle(hip -> knee -> ankle) >= 155°
```

- Measures if standing leg is straight
- 155° or more: 30 points - "Standing leg straight"
- 145-155°: 22 points - "Straighten standing leg"
- Less than 145°: 15 points - "Straighten leg more"

### 3. **Arms Raised (20 points)**

```
wrist.y < shoulder.y - 0.05
AND
wrist.y < nose.y (for full credit)
```

- Both wrists above shoulders
- Above head level: 20 points - "Arms perfect"
- Above shoulders: 12 points - "Raise arms higher"

### 4. **Balance/Alignment (10 points)**

```
|shoulder_center.x - hip_center.x| < 0.05
```

- Body centered and balanced
- Good alignment: 10 points - "Good balance"

---

## Visual Reference

```
        🙏 (hands above head - 20 pts)
         |
    👁️ (nose - reference point)
         |
    _____|_____
   |           |  (shoulders)
   |           |
   |     ❤️    |  (torso)
   |           |
   |_____ _____|
        |       (hips - reference line)
        |
        |🦵 (raised knee - must be above hip)
        |    \
        |     🦶 (foot on inner thigh)
        |
        |
       🦵 (standing leg - must be straight 155°+)
        |
        |
       🦶 (standing foot)
```

---

## Coordinate System

MediaPipe uses normalized coordinates:
- **X-axis**: 0.0 (left) to 1.0 (right)
- **Y-axis**: 0.0 (top) to 1.0 (bottom)
- **Z-axis**: depth (not heavily used)

**Important:** Lower Y value = higher on screen!

So for tree pose:
- `knee.y < hip.y` means knee is HIGHER than hip
- `wrist.y < shoulder.y` means wrist is HIGHER than shoulder

---

## Detection Variations Supported

### Classic Tree Pose
- Foot on inner thigh (high)
- Knee bent 90° outward
- Arms overhead
- **Detection:** All three methods work

### Modified Tree Pose (Easier)
- Foot on calf or ankle
- Knee slightly bent
- Arms at chest
- **Detection:** Vertical height + ankle position

### Beginner Tree Pose
- Toe touching ground
- Heel against standing leg
- Arms at sides
- **Detection:** May get partial credit (10-28 points)

---

## Key Differences from Original Spec

| Aspect | Original Spec | Current Detection |
|--------|--------------|-------------------|
| Standing leg angle | 170-180° | 155°+ (more forgiving) |
| Bent knee angle | 80-100° | Not directly checked |
| Minimum height | Not specified | 0.03 (3% of screen) |
| Detection method | Single check | Triple check (height/position/ankle) |
| Visibility threshold | Not specified | 0.3 (30%) |
| Arms requirement | Must be raised | Partial credit if not |

---

## Why These Changes?

1. **Lower thresholds**: Real-world poses vary, especially for beginners
2. **Multiple detection methods**: More robust, catches different variations
3. **Progressive scoring**: Encourages improvement rather than all-or-nothing
4. **Visibility tolerance**: Works in various lighting/camera conditions
5. **Partial credit**: Motivates users even with imperfect form

---

## Testing Your Tree Pose

### Minimum for GREEN (75%):
- Lift leg at least 6cm (35 pts)
- Keep standing leg reasonably straight (22 pts)
- Raise arms above shoulders (12 pts)
- Maintain some balance (10 pts)
- **Total: 79 points = GREEN ✅**

### Perfect Score (100%):
- Lift leg to thigh level (40 pts)
- Standing leg perfectly straight (30 pts)
- Arms fully overhead (20 pts)
- Perfect balance (10 pts)
- **Total: 100 points = PERFECT ✅**

---

## Debug Information

When you test, the terminal shows:
```
[DEBUG] Left knee height: 0.045, Right knee height: -0.002
[DEBUG] Left knee vis: 0.85, Right knee vis: 0.92
[DEBUG] Left ankle vis: 0.78, Right ankle vis: 0.88
```

**Reading this:**
- Positive height = leg is raised
- Negative height = leg is lower (standing leg)
- Visibility > 0.3 = landmark is detected
- Higher visibility = more confident detection

---

## Reference Images

The classic Tree Pose (Vrksasana) in yoga:
- Standing leg: Completely straight, engaged
- Raised leg: Foot on inner thigh, knee pointing outward
- Hips: Level and square
- Arms: Overhead in prayer position or extended
- Gaze: Forward or upward
- Balance: Weight centered on standing foot

This is a **balance pose** that:
- Strengthens legs and core
- Improves balance and focus
- Opens hips
- Requires concentration

The model is designed to detect this pose while being forgiving enough for beginners and various body types.
