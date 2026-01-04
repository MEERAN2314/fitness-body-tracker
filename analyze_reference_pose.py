#!/usr/bin/env python3
"""
Analyze reference tree pose image to extract exact pose parameters
This will be used to calibrate the detection model
"""

import cv2
import mediapipe as mp
import numpy as np
import json

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle

def analyze_tree_pose_image(image_path):
    """Analyze the reference tree pose image"""
    
    print(f"🔍 Analyzing reference image: {image_path}")
    print("=" * 60)
    
    # Initialize MediaPipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=True,
        model_complexity=2,
        min_detection_confidence=0.5
    )
    
    # Read image
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Error: Could not read image from {image_path}")
        return None
    
    print(f"✓ Image loaded: {image.shape[1]}x{image.shape[0]} pixels")
    
    # Convert to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process image
    results = pose.process(image_rgb)
    
    if not results.pose_landmarks:
        print("❌ Error: No pose detected in image")
        return None
    
    print("✓ Pose detected successfully")
    print()
    
    landmarks = results.pose_landmarks.landmark
    
    # Extract key landmarks
    def get_coords(idx):
        lm = landmarks[idx]
        return [lm.x, lm.y, lm.z], lm.visibility
    
    left_shoulder, ls_v = get_coords(11)
    right_shoulder, rs_v = get_coords(12)
    left_elbow, le_v = get_coords(13)
    right_elbow, re_v = get_coords(14)
    left_wrist, lw_v = get_coords(15)
    right_wrist, rw_v = get_coords(16)
    left_hip, lh_v = get_coords(23)
    right_hip, rh_v = get_coords(24)
    left_knee, lk_v = get_coords(25)
    right_knee, rk_v = get_coords(26)
    left_ankle, la_v = get_coords(27)
    right_ankle, ra_v = get_coords(28)
    nose, n_v = get_coords(0)
    
    # Analyze pose parameters
    print("📊 POSE ANALYSIS")
    print("=" * 60)
    
    # 1. Leg Analysis
    print("\n1️⃣  LEG ANALYSIS:")
    print("-" * 60)
    
    left_knee_height = left_hip[1] - left_knee[1]
    right_knee_height = right_hip[1] - right_knee[1]
    left_ankle_height = left_hip[1] - left_ankle[1]
    right_ankle_height = right_hip[1] - right_ankle[1]
    
    print(f"Left knee height:   {left_knee_height:+.4f} (vis: {lk_v:.2f})")
    print(f"Right knee height:  {right_knee_height:+.4f} (vis: {rk_v:.2f})")
    print(f"Left ankle height:  {left_ankle_height:+.4f} (vis: {la_v:.2f})")
    print(f"Right ankle height: {right_ankle_height:+.4f} (vis: {ra_v:.2f})")
    
    # Determine raised leg
    if left_knee_height > right_knee_height:
        raised_leg = "LEFT"
        raised_height = left_knee_height
        standing_leg = "RIGHT"
    else:
        raised_leg = "RIGHT"
        raised_height = right_knee_height
        standing_leg = "LEFT"
    
    print(f"\n✓ Raised leg: {raised_leg}")
    print(f"✓ Raised height: {raised_height:.4f} ({raised_height*100:.1f}% of screen)")
    
    # 2. Standing Leg Angle
    print(f"\n2️⃣  STANDING LEG ANGLE:")
    print("-" * 60)
    
    if standing_leg == "LEFT":
        standing_angle = calculate_angle(left_hip, left_knee, left_ankle)
        print(f"Left leg angle: {standing_angle:.1f}°")
    else:
        standing_angle = calculate_angle(right_hip, right_knee, right_ankle)
        print(f"Right leg angle: {standing_angle:.1f}°")
    
    # 3. Knee Position (Inward/Outward)
    print(f"\n3️⃣  KNEE POSITION:")
    print("-" * 60)
    
    hip_center_x = (left_hip[0] + right_hip[0]) / 2
    left_knee_dist = abs(left_knee[0] - hip_center_x)
    right_knee_dist = abs(right_knee[0] - hip_center_x)
    left_hip_dist = abs(left_hip[0] - hip_center_x)
    right_hip_dist = abs(right_hip[0] - hip_center_x)
    
    if raised_leg == "LEFT":
        knee_ratio = left_knee_dist / left_hip_dist if left_hip_dist > 0 else 0
        print(f"Left knee distance from center: {left_knee_dist:.4f}")
        print(f"Left hip distance from center:  {left_hip_dist:.4f}")
        print(f"Ratio (knee/hip): {knee_ratio:.2f}")
        if knee_ratio < 0.8:
            print("✓ Knee is INWARD (toward center) - typical tree pose")
        else:
            print("✓ Knee is OUTWARD (away from center)")
    else:
        knee_ratio = right_knee_dist / right_hip_dist if right_hip_dist > 0 else 0
        print(f"Right knee distance from center: {right_knee_dist:.4f}")
        print(f"Right hip distance from center:  {right_hip_dist:.4f}")
        print(f"Ratio (knee/hip): {knee_ratio:.2f}")
        if knee_ratio < 0.8:
            print("✓ Knee is INWARD (toward center) - typical tree pose")
        else:
            print("✓ Knee is OUTWARD (away from center)")
    
    # 4. Arm Position
    print(f"\n4️⃣  ARM POSITION:")
    print("-" * 60)
    
    left_arm_raised = left_wrist[1] < left_shoulder[1]
    right_arm_raised = right_wrist[1] < right_shoulder[1]
    left_arm_height = left_shoulder[1] - left_wrist[1]
    right_arm_height = right_shoulder[1] - right_wrist[1]
    
    print(f"Left wrist height:  {left_arm_height:+.4f} (vis: {lw_v:.2f})")
    print(f"Right wrist height: {right_arm_height:+.4f} (vis: {rw_v:.2f})")
    
    if left_arm_raised and right_arm_raised:
        print("✓ Both arms RAISED")
        if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
            print("✓ Arms are ABOVE HEAD")
        else:
            print("✓ Arms are above shoulders but below head")
    else:
        print("⚠️  Arms not fully raised")
    
    # 5. Balance/Alignment
    print(f"\n5️⃣  BALANCE & ALIGNMENT:")
    print("-" * 60)
    
    shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
    hip_center_x = (left_hip[0] + right_hip[0]) / 2
    alignment = abs(shoulder_center_x - hip_center_x)
    
    print(f"Shoulder center X: {shoulder_center_x:.4f}")
    print(f"Hip center X:      {hip_center_x:.4f}")
    print(f"Alignment offset:  {alignment:.4f}")
    
    if alignment < 0.05:
        print("✓ Excellent balance and alignment")
    elif alignment < 0.10:
        print("✓ Good balance")
    else:
        print("⚠️  Body slightly off-center")
    
    # Generate calibration parameters
    print(f"\n" + "=" * 60)
    print("🎯 RECOMMENDED DETECTION PARAMETERS")
    print("=" * 60)
    
    params = {
        "tree_pose": {
            "raised_leg": {
                "min_height": max(0.02, raised_height * 0.5),  # 50% of reference
                "ideal_height": raised_height,
                "excellent_height": raised_height * 1.1
            },
            "standing_leg": {
                "min_angle": max(145, standing_angle - 15),
                "ideal_angle": standing_angle,
                "max_angle": 180
            },
            "knee_position": {
                "inward_ratio": knee_ratio,
                "inward_threshold": 0.8
            },
            "arms": {
                "min_raise": max(0.03, min(left_arm_height, right_arm_height) * 0.8),
                "ideal_raise": max(left_arm_height, right_arm_height),
                "above_head": left_wrist[1] < nose[1] and right_wrist[1] < nose[1]
            },
            "balance": {
                "max_offset": max(0.05, alignment * 1.5)
            }
        }
    }
    
    print(f"\nRaised Leg Height:")
    print(f"  Minimum:   {params['tree_pose']['raised_leg']['min_height']:.4f}")
    print(f"  Ideal:     {params['tree_pose']['raised_leg']['ideal_height']:.4f}")
    print(f"  Excellent: {params['tree_pose']['raised_leg']['excellent_height']:.4f}")
    
    print(f"\nStanding Leg Angle:")
    print(f"  Minimum: {params['tree_pose']['standing_leg']['min_angle']:.1f}°")
    print(f"  Ideal:   {params['tree_pose']['standing_leg']['ideal_angle']:.1f}°")
    
    print(f"\nKnee Position:")
    print(f"  Inward ratio: {params['tree_pose']['knee_position']['inward_ratio']:.2f}")
    print(f"  Threshold:    {params['tree_pose']['knee_position']['inward_threshold']:.2f}")
    
    print(f"\nArms:")
    print(f"  Min raise: {params['tree_pose']['arms']['min_raise']:.4f}")
    print(f"  Ideal:     {params['tree_pose']['arms']['ideal_raise']:.4f}")
    print(f"  Above head: {params['tree_pose']['arms']['above_head']}")
    
    print(f"\nBalance:")
    print(f"  Max offset: {params['tree_pose']['balance']['max_offset']:.4f}")
    
    # Save parameters
    with open('tree_pose_calibration.json', 'w') as f:
        json.dump(params, f, indent=2)
    
    print(f"\n✓ Parameters saved to: tree_pose_calibration.json")
    
    # Draw skeleton on image
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    annotated_image = image.copy()
    mp_drawing.draw_landmarks(
        annotated_image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )
    
    # Save annotated image
    output_path = 'tree_pose_analyzed.jpg'
    cv2.imwrite(output_path, annotated_image)
    print(f"✓ Annotated image saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")
    print("=" * 60)
    
    return params

if __name__ == "__main__":
    import sys
    
    image_path = "tree pose.jpg"
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    
    params = analyze_tree_pose_image(image_path)
    
    if params:
        print("\n💡 Next steps:")
        print("1. Review the calibration parameters above")
        print("2. Run: python apply_calibration.py")
        print("3. This will update the pose detector with these parameters")
