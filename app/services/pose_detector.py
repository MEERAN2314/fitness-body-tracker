import mediapipe as mp
import numpy as np
import cv2
import base64
import json

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,  # Highest accuracy model
            smooth_landmarks=True,
            enable_segmentation=True,  # Enable segmentation for better limb detection
            min_detection_confidence=0.7,  # Lowered slightly for better lower body detection
            min_tracking_confidence=0.7    # Lowered slightly for better lower body tracking
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Landmark indices for better reference
        self.POSE_LANDMARKS = {
            'NOSE': 0,
            'LEFT_EYE_INNER': 1, 'LEFT_EYE': 2, 'LEFT_EYE_OUTER': 3,
            'RIGHT_EYE_INNER': 4, 'RIGHT_EYE': 5, 'RIGHT_EYE_OUTER': 6,
            'LEFT_EAR': 7, 'RIGHT_EAR': 8,
            'MOUTH_LEFT': 9, 'MOUTH_RIGHT': 10,
            'LEFT_SHOULDER': 11, 'RIGHT_SHOULDER': 12,
            'LEFT_ELBOW': 13, 'RIGHT_ELBOW': 14,
            'LEFT_WRIST': 15, 'RIGHT_WRIST': 16,
            'LEFT_PINKY': 17, 'RIGHT_PINKY': 18,
            'LEFT_INDEX': 19, 'RIGHT_INDEX': 20,
            'LEFT_THUMB': 21, 'RIGHT_THUMB': 22,
            'LEFT_HIP': 23, 'RIGHT_HIP': 24,
            'LEFT_KNEE': 25, 'RIGHT_KNEE': 26,
            'LEFT_ANKLE': 27, 'RIGHT_ANKLE': 28,
            'LEFT_HEEL': 29, 'RIGHT_HEEL': 30,
            'LEFT_FOOT_INDEX': 31, 'RIGHT_FOOT_INDEX': 32
        }
        
        # Lower body landmark indices for focused tracking
        self.LOWER_BODY_LANDMARKS = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points with improved accuracy"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        # Calculate vectors
        ba = a - b
        bc = c - b
        
        # Calculate angle using dot product
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        cosine_angle = np.clip(cosine_angle, -1.0, 1.0)  # Prevent numerical errors
        angle = np.degrees(np.arccos(cosine_angle))
        
        return angle
    
    def get_landmark_coords(self, landmarks, index):
        """Get landmark coordinates with visibility check"""
        if index < len(landmarks):
            lm = landmarks[index]
            return [lm.x, lm.y], lm.visibility
        return None, 0.0
    
    def is_landmark_visible(self, landmarks, index, threshold=0.5):
        """Check if landmark is visible enough for accurate tracking"""
        if index < len(landmarks):
            return landmarks[index].visibility > threshold
        return False
    
    def get_lower_body_visibility_score(self, landmarks):
        """Calculate visibility score for lower body landmarks"""
        lower_body_indices = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        visible_count = sum(1 for idx in lower_body_indices if self.is_landmark_visible(landmarks, idx, 0.5))
        return (visible_count / len(lower_body_indices)) * 100
    
    def check_pose_accuracy(self, landmarks, exercise_id):
        """Check if the current pose matches the target exercise with improved lower body detection"""
        if not landmarks:
            return {"accuracy": 0, "feedback": "No pose detected", "color": "red"}
        
        # Check if key landmarks are visible (especially lower body)
        key_landmarks = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        lower_body_landmarks = [23, 24, 25, 26, 27, 28, 29, 30, 31, 32]
        
        visible_count = sum(1 for idx in key_landmarks if self.is_landmark_visible(landmarks, idx, 0.5))
        lower_body_visible = sum(1 for idx in lower_body_landmarks if self.is_landmark_visible(landmarks, idx, 0.5))
        
        if visible_count < len(key_landmarks) * 0.65:  # At least 65% visible
            return {
                "accuracy": 0,
                "feedback": "⚠️ Move to better lighting or adjust position for full body visibility",
                "color": "red"
            }
        
        if lower_body_visible < len(lower_body_landmarks) * 0.5:  # At least 50% of lower body visible
            return {
                "accuracy": 0,
                "feedback": "⚠️ Ensure legs and feet are fully visible in frame",
                "color": "red"
            }
        
        # Extract key landmarks with visibility
        left_shoulder, ls_vis = self.get_landmark_coords(landmarks, 11)
        right_shoulder, rs_vis = self.get_landmark_coords(landmarks, 12)
        left_elbow, le_vis = self.get_landmark_coords(landmarks, 13)
        right_elbow, re_vis = self.get_landmark_coords(landmarks, 14)
        left_wrist, lw_vis = self.get_landmark_coords(landmarks, 15)
        right_wrist, rw_vis = self.get_landmark_coords(landmarks, 16)
        left_hip, lh_vis = self.get_landmark_coords(landmarks, 23)
        right_hip, rh_vis = self.get_landmark_coords(landmarks, 24)
        left_knee, lk_vis = self.get_landmark_coords(landmarks, 25)
        right_knee, rk_vis = self.get_landmark_coords(landmarks, 26)
        left_ankle, la_vis = self.get_landmark_coords(landmarks, 27)
        right_ankle, ra_vis = self.get_landmark_coords(landmarks, 28)
        left_heel, lhe_vis = self.get_landmark_coords(landmarks, 29)
        right_heel, rhe_vis = self.get_landmark_coords(landmarks, 30)
        left_foot, lf_vis = self.get_landmark_coords(landmarks, 31)
        right_foot, rf_vis = self.get_landmark_coords(landmarks, 32)
        nose, n_vis = self.get_landmark_coords(landmarks, 0)
        
        accuracy = 0
        feedback = []
        max_score = 0
        
        # Improved pose checking logic with enhanced lower body detection
        if exercise_id == "tree-pose":
            max_score = 100
            
            # Check lower body visibility first
            if not (lk_vis > 0.5 and rk_vis > 0.5 and la_vis > 0.5 and ra_vis > 0.5):
                feedback.append("⚠️ Ensure both legs are fully visible")
            
            # 1. Check if one leg is raised (40 points)
            left_knee_raised = left_knee[1] < left_hip[1] - 0.08 and lk_vis > 0.5
            right_knee_raised = right_knee[1] < right_hip[1] - 0.08 and rk_vis > 0.5
            
            if left_knee_raised or right_knee_raised:
                # Check how high the knee is raised
                if left_knee_raised:
                    knee_height = left_hip[1] - left_knee[1]
                    standing_leg_vis = rk_vis > 0.5 and ra_vis > 0.5
                    standing_foot_vis = rf_vis > 0.5 or rhe_vis > 0.5
                else:
                    knee_height = right_hip[1] - right_knee[1]
                    standing_leg_vis = lk_vis > 0.5 and la_vis > 0.5
                    standing_foot_vis = lf_vis > 0.5 or lhe_vis > 0.5
                
                if knee_height > 0.22:
                    accuracy += 40
                    feedback.append("✓ Excellent leg lift")
                elif knee_height > 0.12:
                    accuracy += 30
                    feedback.append("Good leg position, lift a bit higher")
                else:
                    accuracy += 20
                    feedback.append("Raise your leg higher")
                
                # Bonus for foot visibility
                if standing_foot_vis:
                    feedback.append("✓ Standing foot stable")
            else:
                feedback.append("❌ Lift one leg up")
            
            # 2. Check standing leg is straight (25 points - increased importance)
            if left_knee_raised and rk_vis > 0.5 and ra_vis > 0.5:
                standing_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
                
                if 170 <= standing_leg_angle <= 180:
                    accuracy += 25
                    feedback.append("✓ Standing leg perfectly straight")
                elif 165 <= standing_leg_angle < 170:
                    accuracy += 20
                    feedback.append("Standing leg almost straight")
                elif 160 <= standing_leg_angle < 165:
                    accuracy += 15
                    feedback.append("Straighten standing leg more")
                else:
                    feedback.append("❌ Straighten your standing leg")
                    
            elif right_knee_raised and lk_vis > 0.5 and la_vis > 0.5:
                standing_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
                
                if 170 <= standing_leg_angle <= 180:
                    accuracy += 25
                    feedback.append("✓ Standing leg perfectly straight")
                elif 165 <= standing_leg_angle < 170:
                    accuracy += 20
                    feedback.append("Standing leg almost straight")
                elif 160 <= standing_leg_angle < 165:
                    accuracy += 15
                    feedback.append("Straighten standing leg more")
                else:
                    feedback.append("❌ Straighten your standing leg")
            else:
                feedback.append("⚠️ Standing leg not clearly visible")
            
            # 3. Check arm position (20 points)
            if lw_vis > 0.5 and rw_vis > 0.5:
                left_arm_raised = left_wrist[1] < left_shoulder[1] - 0.08
                right_arm_raised = right_wrist[1] < right_shoulder[1] - 0.08
                
                if left_arm_raised and right_arm_raised:
                    if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
                        accuracy += 20
                        feedback.append("✓ Perfect arm position")
                    else:
                        accuracy += 12
                        feedback.append("Raise arms higher above head")
                else:
                    feedback.append("❌ Raise both arms")
            else:
                feedback.append("⚠️ Arms not clearly visible")
            
            # 4. Check balance/alignment (15 points)
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            hip_center_x = (left_hip[0] + right_hip[0]) / 2
            alignment = abs(shoulder_center_x - hip_center_x)
            
            if alignment < 0.04:
                accuracy += 15
                feedback.append("✓ Perfect balance")
            elif alignment < 0.08:
                accuracy += 10
                feedback.append("Good balance")
            else:
                feedback.append("Center your body for better balance")
                
        elif exercise_id == "warrior-two":
            max_score = 100
            
            # Check lower body visibility
            if not all([lk_vis > 0.5, rk_vis > 0.5, la_vis > 0.5, ra_vis > 0.5]):
                feedback.append("⚠️ Ensure both legs are fully visible")
                return {
                    "accuracy": 0,
                    "feedback": " | ".join(feedback),
                    "color": "red"
                }
            
            # 1. Check front knee bend (40 points - increased importance)
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            front_knee_angle = min(left_knee_angle, right_knee_angle)
            back_knee_angle = max(left_knee_angle, right_knee_angle)
            
            if 85 <= front_knee_angle <= 95:
                accuracy += 40
                feedback.append("✓ Perfect 90° knee bend")
            elif 80 <= front_knee_angle <= 100:
                accuracy += 35
                feedback.append("Excellent knee bend")
            elif 75 <= front_knee_angle <= 105:
                accuracy += 28
                feedback.append("Good knee bend, adjust slightly")
            elif 65 <= front_knee_angle <= 115:
                accuracy += 20
                feedback.append("Bend knee closer to 90°")
            else:
                feedback.append("❌ Bend front knee to 90 degrees")
            
            # 2. Check back leg straight (30 points - increased importance)
            if back_knee_angle >= 170:
                accuracy += 30
                feedback.append("✓ Back leg perfectly straight")
            elif back_knee_angle >= 165:
                accuracy += 25
                feedback.append("Back leg almost straight")
            elif back_knee_angle >= 160:
                accuracy += 20
                feedback.append("Straighten back leg more")
            else:
                feedback.append("❌ Straighten your back leg")
            
            # Check foot positioning
            if (lf_vis > 0.5 or lhe_vis > 0.5) and (rf_vis > 0.5 or rhe_vis > 0.5):
                feedback.append("✓ Feet positioned well")
            
            # 3. Check arms extended horizontally (20 points)
            if lw_vis > 0.5 and rw_vis > 0.5:
                left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                arms_straight = left_arm_angle >= 165 and right_arm_angle >= 165
                
                shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
                wrist_y_avg = (left_wrist[1] + right_wrist[1]) / 2
                arms_horizontal = abs(shoulder_y - wrist_y_avg) < 0.08
                
                if arms_straight and arms_horizontal:
                    accuracy += 20
                    feedback.append("✓ Perfect arm extension")
                elif arms_straight:
                    accuracy += 15
                    feedback.append("Arms straight, adjust to horizontal")
                else:
                    feedback.append("Extend arms parallel to ground")
            
            # 4. Check torso upright (10 points)
            shoulder_y_avg = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y_avg = (left_hip[1] + right_hip[1]) / 2
            
            if shoulder_y_avg < hip_y_avg - 0.02:
                accuracy += 10
                feedback.append("✓ Torso upright")
                
        elif exercise_id == "plank":
            max_score = 100
            
            # Check if all body parts are visible (especially lower body)
            if not all([ls_vis > 0.5, rs_vis > 0.5, lh_vis > 0.5, rh_vis > 0.5, 
                       lk_vis > 0.5, rk_vis > 0.5, la_vis > 0.5, ra_vis > 0.5]):
                feedback.append("⚠️ Ensure full body is visible")
                return {
                    "accuracy": 0,
                    "feedback": " | ".join(feedback),
                    "color": "red"
                }
            
            # 1. Check body alignment (50 points)
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y = (left_hip[1] + right_hip[1]) / 2
            knee_y = (left_knee[1] + right_knee[1]) / 2
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            
            # Calculate how straight the body is (including knees)
            shoulder_hip_diff = abs(shoulder_y - hip_y)
            hip_knee_diff = abs(hip_y - knee_y)
            knee_ankle_diff = abs(knee_y - ankle_y)
            
            if shoulder_hip_diff < 0.04 and hip_knee_diff < 0.04 and knee_ankle_diff < 0.04:
                accuracy += 50
                feedback.append("✓ Perfect body alignment")
            elif shoulder_hip_diff < 0.06 and hip_knee_diff < 0.06:
                accuracy += 40
                feedback.append("Excellent alignment")
            elif shoulder_hip_diff < 0.08 and hip_knee_diff < 0.08:
                accuracy += 30
                feedback.append("Good alignment, keep body straighter")
            else:
                if hip_y > shoulder_y + 0.05:
                    feedback.append("❌ Hips too high, lower them")
                elif hip_y < shoulder_y - 0.05:
                    feedback.append("❌ Hips sagging, lift them up")
                else:
                    feedback.append("❌ Keep body in straight line")
            
            # Check leg straightness
            left_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            if left_leg_angle >= 170 and right_leg_angle >= 170:
                feedback.append("✓ Legs perfectly straight")
            elif left_leg_angle >= 165 and right_leg_angle >= 165:
                feedback.append("Legs almost straight")
            else:
                feedback.append("Straighten your legs")
            
            # 2. Check arm position (25 points)
            if le_vis > 0.5 and re_vis > 0.5:
                left_elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_elbow_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                if left_elbow_angle >= 170 and right_elbow_angle >= 170:
                    accuracy += 25
                    feedback.append("✓ Arms perfectly straight")
                elif left_elbow_angle >= 165 and right_elbow_angle >= 165:
                    accuracy += 20
                    feedback.append("Arms almost straight")
                else:
                    feedback.append("Straighten your arms more")
            
            # 3. Check if body is horizontal (25 points)
            if 0.35 < shoulder_y < 0.65:
                accuracy += 25
                feedback.append("✓ Good plank height")
                
        else:
            max_score = 100
            accuracy = 50
            feedback.append("Hold the pose steady")
        
        # Normalize accuracy to 0-100
        accuracy = min(accuracy, max_score)
        
        # Determine color based on accuracy
        if accuracy >= 80:
            color = "green"
        elif accuracy >= 58:
            color = "yellow"
        else:
            color = "red"
        
        return {
            "accuracy": accuracy,
            "feedback": " | ".join(feedback) if feedback else "Position yourself",
            "color": color
        }
        """Check if the current pose matches the target exercise with improved limb detection"""
        if not landmarks:
            return {"accuracy": 0, "feedback": "No pose detected", "color": "red"}
        
        # Check if key landmarks are visible
        key_landmarks = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
        visible_count = sum(1 for idx in key_landmarks if self.is_landmark_visible(landmarks, idx, 0.6))
        
        if visible_count < len(key_landmarks) * 0.7:  # At least 70% visible
            return {
                "accuracy": 0,
                "feedback": "⚠️ Move to better lighting or adjust position for full body visibility",
                "color": "red"
            }
        
        # Extract key landmarks with visibility
        left_shoulder, ls_vis = self.get_landmark_coords(landmarks, 11)
        right_shoulder, rs_vis = self.get_landmark_coords(landmarks, 12)
        left_elbow, le_vis = self.get_landmark_coords(landmarks, 13)
        right_elbow, re_vis = self.get_landmark_coords(landmarks, 14)
        left_wrist, lw_vis = self.get_landmark_coords(landmarks, 15)
        right_wrist, rw_vis = self.get_landmark_coords(landmarks, 16)
        left_hip, lh_vis = self.get_landmark_coords(landmarks, 23)
        right_hip, rh_vis = self.get_landmark_coords(landmarks, 24)
        left_knee, lk_vis = self.get_landmark_coords(landmarks, 25)
        right_knee, rk_vis = self.get_landmark_coords(landmarks, 26)
        left_ankle, la_vis = self.get_landmark_coords(landmarks, 27)
        right_ankle, ra_vis = self.get_landmark_coords(landmarks, 28)
        nose, n_vis = self.get_landmark_coords(landmarks, 0)
        
        accuracy = 0
        feedback = []
        max_score = 0
        
        # Improved pose checking logic with better limb detection
        if exercise_id == "tree-pose":
            max_score = 100
            
            # 1. Check if one leg is raised (40 points)
            left_knee_raised = left_knee[1] < left_hip[1] - 0.08 and lk_vis > 0.6
            right_knee_raised = right_knee[1] < right_hip[1] - 0.08 and rk_vis > 0.6
            
            if left_knee_raised or right_knee_raised:
                # Check how high the knee is raised
                if left_knee_raised:
                    knee_height = left_hip[1] - left_knee[1]
                    standing_leg_vis = rk_vis and ra_vis
                else:
                    knee_height = right_hip[1] - right_knee[1]
                    standing_leg_vis = lk_vis and la_vis
                
                if knee_height > 0.22:
                    accuracy += 40
                    feedback.append("✓ Excellent leg lift")
                elif knee_height > 0.12:
                    accuracy += 30
                    feedback.append("Good leg position, lift a bit higher")
                else:
                    accuracy += 20
                    feedback.append("Raise your leg higher")
            else:
                feedback.append("❌ Lift one leg up")
            
            # 2. Check standing leg is straight (20 points)
            if left_knee_raised and standing_leg_vis:
                standing_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            elif right_knee_raised and standing_leg_vis:
                standing_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            else:
                standing_leg_angle = 0
            
            if 165 <= standing_leg_angle <= 180:
                accuracy += 20
                feedback.append("✓ Standing leg straight")
            elif 155 <= standing_leg_angle < 165:
                accuracy += 15
                feedback.append("Almost straight, extend more")
            else:
                feedback.append("Straighten your standing leg")
            
            # 3. Check arm position (25 points)
            if lw_vis > 0.6 and rw_vis > 0.6:
                left_arm_raised = left_wrist[1] < left_shoulder[1] - 0.08
                right_arm_raised = right_wrist[1] < right_shoulder[1] - 0.08
                
                if left_arm_raised and right_arm_raised:
                    # Check if arms are above head
                    if left_wrist[1] < nose[1] and right_wrist[1] < nose[1]:
                        accuracy += 25
                        feedback.append("✓ Perfect arm position")
                    else:
                        accuracy += 15
                        feedback.append("Raise arms higher above head")
                else:
                    feedback.append("❌ Raise both arms")
            else:
                feedback.append("⚠️ Arms not clearly visible")
            
            # 4. Check balance/alignment (15 points)
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            hip_center_x = (left_hip[0] + right_hip[0]) / 2
            alignment = abs(shoulder_center_x - hip_center_x)
            
            if alignment < 0.04:
                accuracy += 15
                feedback.append("✓ Perfect balance")
            elif alignment < 0.08:
                accuracy += 10
                feedback.append("Good balance")
            else:
                feedback.append("Center your body for better balance")
                
        elif exercise_id == "warrior-two":
            max_score = 100
            
            # Check limb visibility
            if not all([lk_vis > 0.6, rk_vis > 0.6, la_vis > 0.6, ra_vis > 0.6]):
                feedback.append("⚠️ Ensure legs are fully visible")
            
            # 1. Check front knee bend (35 points)
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            front_knee_angle = min(left_knee_angle, right_knee_angle)
            
            if 85 <= front_knee_angle <= 95:
                accuracy += 35
                feedback.append("✓ Perfect 90° knee bend")
            elif 75 <= front_knee_angle <= 105:
                accuracy += 28
                feedback.append("Good knee bend, adjust slightly")
            elif 65 <= front_knee_angle <= 115:
                accuracy += 20
                feedback.append("Bend knee closer to 90°")
            else:
                feedback.append("❌ Bend front knee to 90 degrees")
            
            # 2. Check back leg straight (25 points)
            back_knee_angle = max(left_knee_angle, right_knee_angle)
            
            if back_knee_angle >= 165:
                accuracy += 25
                feedback.append("✓ Back leg perfectly straight")
            elif back_knee_angle >= 155:
                accuracy += 20
                feedback.append("Back leg almost straight")
            else:
                feedback.append("Straighten your back leg more")
            
            # 3. Check arms extended horizontally (30 points)
            if lw_vis > 0.6 and rw_vis > 0.6:
                left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                arms_straight = left_arm_angle >= 165 and right_arm_angle >= 165
                
                # Check if arms are horizontal
                shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
                wrist_y_avg = (left_wrist[1] + right_wrist[1]) / 2
                arms_horizontal = abs(shoulder_y - wrist_y_avg) < 0.08
                
                if arms_straight and arms_horizontal:
                    accuracy += 30
                    feedback.append("✓ Perfect arm extension")
                elif arms_straight:
                    accuracy += 22
                    feedback.append("Arms straight, adjust to horizontal")
                else:
                    feedback.append("❌ Extend arms parallel to ground")
            else:
                feedback.append("⚠️ Arms not clearly visible")
            
            # 4. Check torso upright (10 points)
            shoulder_y_avg = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y_avg = (left_hip[1] + right_hip[1]) / 2
            
            if shoulder_y_avg < hip_y_avg - 0.02:
                accuracy += 10
                feedback.append("✓ Torso upright")
            else:
                feedback.append("Keep torso upright")
                
        elif exercise_id == "plank":
            max_score = 100
            
            # Check if all body parts are visible
            if not all([ls_vis > 0.6, rs_vis > 0.6, lh_vis > 0.6, rh_vis > 0.6, la_vis > 0.6, ra_vis > 0.6]):
                feedback.append("⚠️ Ensure full body is visible")
            
            # 1. Check body alignment (50 points)
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y = (left_hip[1] + right_hip[1]) / 2
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            
            # Calculate how straight the body is
            shoulder_hip_diff = abs(shoulder_y - hip_y)
            hip_ankle_diff = abs(hip_y - ankle_y)
            
            if shoulder_hip_diff < 0.04 and hip_ankle_diff < 0.04:
                accuracy += 50
                feedback.append("✓ Perfect body alignment")
            elif shoulder_hip_diff < 0.08 and hip_ankle_diff < 0.08:
                accuracy += 38
                feedback.append("Good alignment, keep body straighter")
            else:
                if hip_y > shoulder_y + 0.05:
                    feedback.append("❌ Hips too high, lower them")
                elif hip_y < shoulder_y - 0.05:
                    feedback.append("❌ Hips sagging, lift them up")
                else:
                    feedback.append("❌ Keep body in straight line")
            
            # 2. Check arm position (25 points)
            if le_vis > 0.6 and re_vis > 0.6:
                left_elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
                right_elbow_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
                
                if left_elbow_angle >= 165 and right_elbow_angle >= 165:
                    accuracy += 25
                    feedback.append("✓ Arms perfectly straight")
                elif left_elbow_angle >= 155 and right_elbow_angle >= 155:
                    accuracy += 20
                    feedback.append("Arms almost straight")
                else:
                    feedback.append("Straighten your arms more")
            else:
                feedback.append("⚠️ Arms not clearly visible")
            
            # 3. Check if body is horizontal (25 points)
            if 0.35 < shoulder_y < 0.65:
                accuracy += 25
                feedback.append("✓ Good plank height")
            else:
                feedback.append("Adjust body position")
                
        else:
            # Default checking
            max_score = 100
            accuracy = 50
            feedback.append("Hold the pose steady")
        
        # Normalize accuracy to 0-100
        accuracy = min(accuracy, max_score)
        
        # Determine color based on accuracy
        if accuracy >= 82:
            color = "green"
        elif accuracy >= 60:
            color = "yellow"
        else:
            color = "red"
        
        return {
            "accuracy": accuracy,
            "feedback": " | ".join(feedback) if feedback else "Position yourself",
            "color": color
        }
    
    def process_pose(self, data):
        """Process pose from frame data with optimized settings"""
        try:
            # Decode base64 image
            image_data = data.get("image", "").split(",")[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return {"success": False, "message": "Failed to decode image"}
            
            # Get original dimensions
            height, width = image.shape[:2]
            
            # Optimize image for MediaPipe with focus on full body detection
            target_width = 1280  # Increased further for better lower body detection
            if width != target_width:
                scale = target_width / width
                new_width = target_width
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            # Apply bilateral filter to preserve edges (better for limb boundaries)
            image = cv2.bilateralFilter(image, 5, 75, 75)
            
            # Enhance image quality for better limb detection (especially lower body)
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            image = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            # Sharpen image for better edge detection (helps with lower limbs)
            kernel = np.array([[-1,-1,-1],
                              [-1, 9,-1],
                              [-1,-1,-1]])
            image = cv2.filter2D(image, -1, kernel)
            
            # Slight brightness boost
            image = cv2.convertScaleAbs(image, alpha=1.08, beta=8)
            
            # Convert to RGB (MediaPipe requirement)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Improve image quality
            image_rgb.flags.writeable = False
            
            # Process pose with MediaPipe
            results = self.pose.process(image_rgb)
            
            image_rgb.flags.writeable = True
            
            if results.pose_landmarks:
                # Extract landmarks with high confidence
                landmarks = results.pose_landmarks.landmark
                
                # Filter and normalize landmarks
                landmarks_list = []
                for lm in landmarks:
                    # Only include landmarks with good visibility
                    landmarks_list.append([
                        float(lm.x), 
                        float(lm.y), 
                        float(lm.z), 
                        float(lm.visibility)
                    ])
                
                # Check pose accuracy
                exercise_id = data.get("exercise_id", "")
                pose_check = self.check_pose_accuracy(landmarks, exercise_id)
                
                return {
                    "success": True,
                    "landmarks": landmarks_list,
                    "accuracy": pose_check["accuracy"],
                    "feedback": pose_check["feedback"],
                    "color": pose_check["color"]
                }
            else:
                return {
                    "success": False,
                    "message": "No body detected. Step back and ensure full body is visible with good lighting."
                }
                
        except Exception as e:
            print(f"Error in process_pose: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "message": "Processing error. Please ensure good lighting and full body visibility."
            }
