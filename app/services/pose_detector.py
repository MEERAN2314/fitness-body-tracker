import mediapipe as mp
import numpy as np
import cv2
import base64
import json

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        # Optimized MediaPipe configuration for better detection
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,  # Balance between speed and accuracy
            smooth_landmarks=True,
            enable_segmentation=False,  # Disable for better performance
            min_detection_confidence=0.5,  # Lower for better initial detection
            min_tracking_confidence=0.5    # Lower for continuous tracking
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def get_landmark_coords(self, landmarks, index):
        """Get landmark coordinates with visibility"""
        if index < len(landmarks):
            lm = landmarks[index]
            return [lm.x, lm.y, lm.z], lm.visibility
        return None, 0.0
    
    def is_visible(self, landmarks, index, threshold=0.5):
        """Check if landmark is visible"""
        if index < len(landmarks):
            return landmarks[index].visibility > threshold
        return False
    
    def check_pose_accuracy(self, landmarks, exercise_id):
        """Check pose accuracy with improved detection logic"""
        if not landmarks:
            return {"accuracy": 0, "feedback": "No pose detected", "color": "red"}
        
        # Key body landmarks
        key_points = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        visible = sum(1 for idx in key_points if self.is_visible(landmarks, idx, 0.4))
        
        if visible < len(key_points) * 0.6:
            return {
                "accuracy": 0,
                "feedback": "⚠️ Step back and ensure full body is visible",
                "color": "red"
            }
        
        # Extract landmarks
        left_shoulder, ls_v = self.get_landmark_coords(landmarks, 11)
        right_shoulder, rs_v = self.get_landmark_coords(landmarks, 12)
        left_elbow, le_v = self.get_landmark_coords(landmarks, 13)
        right_elbow, re_v = self.get_landmark_coords(landmarks, 14)
        left_wrist, lw_v = self.get_landmark_coords(landmarks, 15)
        right_wrist, rw_v = self.get_landmark_coords(landmarks, 16)
        left_hip, lh_v = self.get_landmark_coords(landmarks, 23)
        right_hip, rh_v = self.get_landmark_coords(landmarks, 24)
        left_knee, lk_v = self.get_landmark_coords(landmarks, 25)
        right_knee, rk_v = self.get_landmark_coords(landmarks, 26)
        left_ankle, la_v = self.get_landmark_coords(landmarks, 27)
        right_ankle, ra_v = self.get_landmark_coords(landmarks, 28)
        nose, n_v = self.get_landmark_coords(landmarks, 0)
        
        accuracy = 0
        feedback = []
        
        # Exercise-specific detection
        if exercise_id == "tree-pose":
            # ENHANCED TREE POSE LEG DETECTION
            
            # Calculate heights (negative means lower, positive means higher)
            left_knee_height = left_hip[1] - left_knee[1]
            right_knee_height = right_hip[1] - right_knee[1]
            left_ankle_height = left_hip[1] - left_ankle[1]
            right_ankle_height = right_hip[1] - right_ankle[1]
            
            # Calculate knee distances from body center
            hip_center_x = (left_hip[0] + right_hip[0]) / 2
            left_knee_dist = abs(left_knee[0] - hip_center_x)
            right_knee_dist = abs(right_knee[0] - hip_center_x)
            left_hip_dist = abs(left_hip[0] - hip_center_x)
            right_hip_dist = abs(right_hip[0] - hip_center_x)
            
            # Check if knee moved inward (toward center) - indicates tree pose
            left_knee_inward = left_knee_dist < left_hip_dist * 0.8
            right_knee_inward = right_knee_dist < right_hip_dist * 0.8
            
            # Calculate ankle-knee distance (foot placement)
            left_ankle_knee_dist = abs(left_ankle[0] - left_knee[0]) + abs(left_ankle[1] - left_knee[1])
            right_ankle_knee_dist = abs(right_ankle[0] - right_knee[0]) + abs(right_ankle[1] - right_knee[1])
            
            # Multi-criteria detection for each leg
            left_criteria = {
                'height': left_knee_height > 0.0200,  # Calibrated  # Very low threshold
                'ankle_raised': left_ankle_height > 0.0200,  # Calibrated
                'inward': left_knee_inward,
                'visible': lk_v > 0.25 and la_v > 0.25,
                'ankle_near_knee': left_ankle_knee_dist < 0.3  # Foot near opposite leg
            }
            
            right_criteria = {
                'height': right_knee_height > 0.0200,  # Calibrated
                'ankle_raised': right_ankle_height > 0.0200,  # Calibrated
                'inward': right_knee_inward,
                'visible': rk_v > 0.25 and ra_v > 0.25,
                'ankle_near_knee': right_ankle_knee_dist < 0.3
            }
            
            # Count criteria met for each leg
            left_score = sum([
                left_criteria['height'],
                left_criteria['ankle_raised'],
                left_criteria['inward'],
                left_criteria['ankle_near_knee']
            ])
            
            right_score = sum([
                right_criteria['height'],
                right_criteria['ankle_raised'],
                right_criteria['inward'],
                right_criteria['ankle_near_knee']
            ])
            
            # Debug output
            print(f"\n[TREE POSE DEBUG]")
            print(f"Left leg  - Height: {left_knee_height:.3f}, Ankle: {left_ankle_height:.3f}, Inward: {left_knee_inward}, Score: {left_score}/4, Vis: {lk_v:.2f}")
            print(f"Right leg - Height: {right_knee_height:.3f}, Ankle: {right_ankle_height:.3f}, Inward: {right_knee_inward}, Score: {right_score}/4, Vis: {rk_v:.2f}")
            
            # Determine which leg is raised (need at least 2 criteria)
            left_leg_lifted = left_score >= 2 and left_criteria['visible']
            right_leg_lifted = right_score >= 2 and right_criteria['visible']
            
            if left_leg_lifted or right_leg_lifted:
                # Determine which leg is more clearly raised
                if left_leg_lifted and not right_leg_lifted:
                    knee_height = left_knee_height
                    ankle_height = left_ankle_height
                    raised_side = "left"
                    standing_side = "right"
                elif right_leg_lifted and not left_leg_lifted:
                    knee_height = right_knee_height
                    ankle_height = right_ankle_height
                    raised_side = "right"
                    standing_side = "left"
                else:
                    # Both detected, use the one with higher score
                    if left_score > right_score:
                        knee_height = left_knee_height
                        ankle_height = left_ankle_height
                        raised_side = "left"
                        standing_side = "right"
                    elif right_score > left_score:
                        knee_height = right_knee_height
                        ankle_height = right_ankle_height
                        raised_side = "right"
                        standing_side = "left"
                    else:
                        # Equal scores, use height
                        if left_knee_height > right_knee_height:
                            knee_height = left_knee_height
                            ankle_height = left_ankle_height
                            raised_side = "left"
                            standing_side = "right"
                        else:
                            knee_height = right_knee_height
                            ankle_height = right_ankle_height
                            raised_side = "right"
                            standing_side = "left"
                
                print(f"[DETECTED] Raised leg: {raised_side}, Height: {knee_height:.3f}")
                
                # Score based on height (use max of knee or ankle height)
                max_height = max(knee_height, ankle_height)
                
                # Add visual indicator of which leg
                leg_emoji = "🦵⬅️" if raised_side == "left" else "🦵➡️"
                
                if max_height > -0.0804:  # Calibrated: excellent
                    accuracy += 40
                    feedback.append(f"✓ Excellent leg lift! {leg_emoji}")
                elif max_height > -0.0731:  # Calibrated: ideal
                    accuracy += 38
                    feedback.append(f"✓ Great leg lift! {leg_emoji}")
                elif max_height > -0.0438:  # Calibrated: good
                    accuracy += 35
                    feedback.append(f"✓ Good leg lift, go higher {leg_emoji}")
                elif max_height > 0.0300:  # Calibrated: fair
                    accuracy += 30
                    feedback.append(f"Lift leg higher {leg_emoji}")
                else:
                    accuracy += 25
                    feedback.append(f"Keep lifting leg {leg_emoji}")
                
                # 2. Standing leg straight (30 points)
                if standing_side == "right" and rk_v > 0.3 and ra_v > 0.3:
                    angle = self.calculate_angle(right_hip, right_knee, right_ankle)
                    print(f"[STANDING LEG] Right leg angle: {angle:.1f}°")
                    if angle >= 159.0:  # Calibrated: ideal
                        accuracy += 30
                        feedback.append("✓ Standing leg straight")
                    elif angle >= 145.0:  # Calibrated: minimum
                        accuracy += 22
                        feedback.append("Straighten standing leg")
                    else:
                        accuracy += 15
                        feedback.append("Straighten leg more")
                        
                elif standing_side == "left" and lk_v > 0.3 and la_v > 0.3:
                    angle = self.calculate_angle(left_hip, left_knee, left_ankle)
                    print(f"[STANDING LEG] Left leg angle: {angle:.1f}°")
                    if angle >= 159.0:  # Calibrated: ideal
                        accuracy += 30
                        feedback.append("✓ Standing leg straight")
                    elif angle >= 145.0:  # Calibrated: minimum
                        accuracy += 22
                        feedback.append("Straighten standing leg")
                    else:
                        accuracy += 15
                        feedback.append("Straighten leg more")
                else:
                    # Give partial credit
                    accuracy += 15
                    feedback.append("Keep standing leg straight")
            else:
                # No clear leg lift detected
                # Check if there's ANY indication of movement
                if (left_knee_height > 0.01 or right_knee_height > 0.01 or 
                    left_ankle_height > 0.01 or right_ankle_height > 0.01):
                    accuracy += 15
                    feedback.append("Lift leg higher - not detected yet")
                    print(f"[ATTEMPTING] Small movement detected but not enough criteria")
                else:
                    feedback.append("❌ Lift one leg up")
                    print(f"[NO LIFT] No leg movement detected")
            
            # 3. Arms raised (20 points)
            if lw_v > 0.4 and rw_v > 0.4:
                arms_up = (left_wrist[1] < left_shoulder[1] - 0.05 and 
                          right_wrist[1] < right_shoulder[1] - 0.05)
                if arms_up:
                    if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
                        accuracy += 20
                        feedback.append("✓ Arms perfect")
                    else:
                        accuracy += 12
                        feedback.append("Raise arms higher")
                else:
                    feedback.append("❌ Raise both arms")
            
            # 4. Balance (10 points)
            shoulder_x = (left_shoulder[0] + right_shoulder[0]) / 2
            hip_x = (left_hip[0] + right_hip[0]) / 2
            if abs(shoulder_x - hip_x) < 0.05:
                accuracy += 10
                feedback.append("✓ Good balance")
                
        elif exercise_id == "warrior-two":
            # 1. Front knee bend (40 points)
            left_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            front_angle = min(left_angle, right_angle)
            back_angle = max(left_angle, right_angle)
            
            if 80 <= front_angle <= 100:
                accuracy += 40
                feedback.append("✓ Perfect knee bend")
            elif 70 <= front_angle <= 110:
                accuracy += 30
                feedback.append("Good, adjust to 90°")
            elif 60 <= front_angle <= 120:
                accuracy += 20
                feedback.append("Bend knee to 90°")
            else:
                feedback.append("❌ Bend front knee")
            
            # 2. Back leg straight (30 points)
            if back_angle >= 160:
                accuracy += 30
                feedback.append("✓ Back leg straight")
            elif back_angle >= 150:
                accuracy += 20
                feedback.append("Straighten back leg")
            else:
                feedback.append("❌ Straighten back leg")
            
            # 3. Arms extended (20 points)
            if lw_v > 0.4 and rw_v > 0.4:
                left_arm = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_arm = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                if left_arm >= 160 and right_arm >= 160:
                    shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
                    wrist_y = (left_wrist[1] + right_wrist[1]) / 2
                    
                    if abs(shoulder_y - wrist_y) < 0.1:
                        accuracy += 20
                        feedback.append("✓ Arms perfect")
                    else:
                        accuracy += 12
                        feedback.append("Level arms")
                else:
                    feedback.append("Straighten arms")
            
            # 4. Torso upright (10 points)
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y = (left_hip[1] + right_hip[1]) / 2
            if shoulder_y < hip_y:
                accuracy += 10
                feedback.append("✓ Torso upright")
                
        elif exercise_id == "plank":
            # 1. Body alignment (50 points)
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y = (left_hip[1] + right_hip[1]) / 2
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            
            shoulder_hip = abs(shoulder_y - hip_y)
            hip_ankle = abs(hip_y - ankle_y)
            
            if shoulder_hip < 0.05 and hip_ankle < 0.05:
                accuracy += 50
                feedback.append("✓ Perfect alignment")
            elif shoulder_hip < 0.08 and hip_ankle < 0.08:
                accuracy += 35
                feedback.append("Good, keep straighter")
            else:
                if hip_y > shoulder_y + 0.05:
                    feedback.append("❌ Lower hips")
                elif hip_y < shoulder_y - 0.05:
                    feedback.append("❌ Lift hips")
                else:
                    feedback.append("❌ Straighten body")
            
            # 2. Arms straight (25 points)
            if le_v > 0.4 and re_v > 0.4:
                left_arm = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_arm = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                if left_arm >= 160 and right_arm >= 160:
                    accuracy += 25
                    feedback.append("✓ Arms straight")
                elif left_arm >= 150 and right_arm >= 150:
                    accuracy += 18
                    feedback.append("Straighten arms")
                else:
                    feedback.append("❌ Extend arms")
            
            # 3. Position (25 points)
            if 0.3 < shoulder_y < 0.7:
                accuracy += 25
                feedback.append("✓ Good height")
        else:
            accuracy = 50
            feedback.append("Hold pose steady")
        
        # Determine color
        if accuracy >= 70:
            color = "green"
        elif accuracy >= 50:
            color = "yellow"
        else:
            color = "red"
        
        return {
            "accuracy": min(accuracy, 100),
            "feedback": " | ".join(feedback) if feedback else "Position yourself",
            "color": color
        }
    
    def process_pose(self, data):
        """Process incoming frame data"""
        try:
            # Decode base64 image
            image_data = data['image'].split(',')[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {
                    "success": False,
                    "message": "Failed to decode image"
                }
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process with MediaPipe
            results = self.pose.process(image_rgb)
            
            if not results.pose_landmarks:
                return {
                    "success": False,
                    "message": "No person detected. Step back to show full body."
                }
            
            # Extract landmarks
            landmarks = results.pose_landmarks.landmark
            
            # Convert to list format
            landmarks_list = []
            for lm in landmarks:
                landmarks_list.append([lm.x, lm.y, lm.z, lm.visibility])
            
            # Check pose accuracy
            exercise_id = data.get('exercise_id', 'tree-pose')
            pose_result = self.check_pose_accuracy(landmarks, exercise_id)
            
            return {
                "success": True,
                "landmarks": landmarks_list,
                "accuracy": pose_result["accuracy"],
                "feedback": pose_result["feedback"],
                "color": pose_result["color"]
            }
            
        except Exception as e:
            print(f"Error in process_pose: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": f"Processing error: {str(e)}"
            }
