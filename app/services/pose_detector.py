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
            model_complexity=2,  # Increased for better accuracy
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.7,  # Increased for better detection
            min_tracking_confidence=0.7    # Increased for better tracking
        )
        
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
    
    def check_pose_accuracy(self, landmarks, exercise_id):
        """Check if the current pose matches the target exercise"""
        if not landmarks:
            return {"accuracy": 0, "feedback": "No pose detected", "color": "red"}
        
        # Extract key landmarks
        left_shoulder = [landmarks[11].x, landmarks[11].y]
        right_shoulder = [landmarks[12].x, landmarks[12].y]
        left_elbow = [landmarks[13].x, landmarks[13].y]
        right_elbow = [landmarks[14].x, landmarks[14].y]
        left_wrist = [landmarks[15].x, landmarks[15].y]
        right_wrist = [landmarks[16].x, landmarks[16].y]
        left_hip = [landmarks[23].x, landmarks[23].y]
        right_hip = [landmarks[24].x, landmarks[24].y]
        left_knee = [landmarks[25].x, landmarks[25].y]
        right_knee = [landmarks[26].x, landmarks[26].y]
        left_ankle = [landmarks[27].x, landmarks[27].y]
        right_ankle = [landmarks[28].x, landmarks[28].y]
        nose = [landmarks[0].x, landmarks[0].y]
        
        accuracy = 0
        feedback = []
        max_score = 0
        
        # Improved pose checking logic
        if exercise_id == "tree-pose":
            max_score = 100
            
            # 1. Check if one leg is raised (40 points)
            left_knee_raised = left_knee[1] < left_hip[1] - 0.1
            right_knee_raised = right_knee[1] < right_hip[1] - 0.1
            
            if left_knee_raised or right_knee_raised:
                # Check how high the knee is raised
                if left_knee_raised:
                    knee_height = left_hip[1] - left_knee[1]
                else:
                    knee_height = right_hip[1] - right_knee[1]
                
                if knee_height > 0.25:
                    accuracy += 40
                    feedback.append("✓ Excellent leg lift")
                elif knee_height > 0.15:
                    accuracy += 30
                    feedback.append("Good leg position, lift a bit higher")
                else:
                    accuracy += 20
                    feedback.append("Raise your leg higher")
            else:
                feedback.append("❌ Lift one leg up")
            
            # 2. Check standing leg is straight (20 points)
            if left_knee_raised:
                standing_leg_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            else:
                standing_leg_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            
            if 160 <= standing_leg_angle <= 180:
                accuracy += 20
                feedback.append("✓ Standing leg straight")
            else:
                feedback.append("Straighten your standing leg")
            
            # 3. Check arm position (25 points)
            left_arm_raised = left_wrist[1] < left_shoulder[1] - 0.1
            right_arm_raised = right_wrist[1] < right_shoulder[1] - 0.1
            
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
            
            # 4. Check balance/alignment (15 points)
            shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
            hip_center_x = (left_hip[0] + right_hip[0]) / 2
            alignment = abs(shoulder_center_x - hip_center_x)
            
            if alignment < 0.05:
                accuracy += 15
                feedback.append("✓ Perfect balance")
            elif alignment < 0.1:
                accuracy += 10
                feedback.append("Good balance")
            else:
                feedback.append("Center your body for better balance")
                
        elif exercise_id == "warrior-two":
            max_score = 100
            
            # 1. Check front knee bend (35 points)
            left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
            right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)
            
            front_knee_angle = min(left_knee_angle, right_knee_angle)
            
            if 80 <= front_knee_angle <= 100:
                accuracy += 35
                feedback.append("✓ Perfect knee bend")
            elif 70 <= front_knee_angle <= 110:
                accuracy += 25
                feedback.append("Good knee bend, adjust slightly")
            else:
                feedback.append("❌ Bend front knee to 90 degrees")
            
            # 2. Check back leg straight (25 points)
            back_knee_angle = max(left_knee_angle, right_knee_angle)
            
            if back_knee_angle >= 160:
                accuracy += 25
                feedback.append("✓ Back leg straight")
            else:
                feedback.append("Straighten your back leg")
            
            # 3. Check arms extended horizontally (30 points)
            left_arm_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_arm_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            arms_straight = left_arm_angle >= 160 and right_arm_angle >= 160
            
            # Check if arms are horizontal
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
            wrist_y_avg = (left_wrist[1] + right_wrist[1]) / 2
            arms_horizontal = abs(shoulder_y - wrist_y_avg) < 0.1
            
            if arms_straight and arms_horizontal:
                accuracy += 30
                feedback.append("✓ Perfect arm extension")
            elif arms_straight:
                accuracy += 20
                feedback.append("Arms straight, adjust to horizontal")
            else:
                feedback.append("❌ Extend arms parallel to ground")
            
            # 4. Check torso upright (10 points)
            shoulder_y_avg = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y_avg = (left_hip[1] + right_hip[1]) / 2
            
            if shoulder_y_avg < hip_y_avg:
                accuracy += 10
                feedback.append("✓ Torso upright")
            else:
                feedback.append("Keep torso upright")
                
        elif exercise_id == "plank":
            max_score = 100
            
            # 1. Check body alignment (50 points)
            shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
            hip_y = (left_hip[1] + right_hip[1]) / 2
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            
            # Calculate how straight the body is
            shoulder_hip_diff = abs(shoulder_y - hip_y)
            hip_ankle_diff = abs(hip_y - ankle_y)
            
            if shoulder_hip_diff < 0.05 and hip_ankle_diff < 0.05:
                accuracy += 50
                feedback.append("✓ Perfect body alignment")
            elif shoulder_hip_diff < 0.1 and hip_ankle_diff < 0.1:
                accuracy += 35
                feedback.append("Good alignment, keep body straighter")
            else:
                if hip_y > shoulder_y + 0.05:
                    feedback.append("❌ Hips too high, lower them")
                elif hip_y < shoulder_y - 0.05:
                    feedback.append("❌ Hips sagging, lift them up")
                else:
                    feedback.append("❌ Keep body in straight line")
            
            # 2. Check arm position (25 points)
            left_elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_elbow_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            if left_elbow_angle >= 160 and right_elbow_angle >= 160:
                accuracy += 25
                feedback.append("✓ Arms straight")
            else:
                feedback.append("Straighten your arms")
            
            # 3. Check if body is horizontal (25 points)
            if 0.3 < shoulder_y < 0.7:
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
        if accuracy >= 85:
            color = "green"
        elif accuracy >= 65:
            color = "yellow"
        else:
            color = "red"
        
        return {
            "accuracy": accuracy,
            "feedback": " | ".join(feedback) if feedback else "Position yourself",
            "color": color
        }
    
    def process_pose(self, data):
        """Process pose from frame data"""
        try:
            # Decode base64 image
            image_data = data.get("image", "").split(",")[1]
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Convert to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process pose
            results = self.pose.process(image_rgb)
            
            if results.pose_landmarks:
                # Extract landmarks
                landmarks = results.pose_landmarks.landmark
                landmarks_list = [[lm.x, lm.y, lm.z, lm.visibility] for lm in landmarks]
                
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
                    "message": "No pose detected. Please ensure you're fully visible in the camera."
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing pose: {str(e)}"
            }
