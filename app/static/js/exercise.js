let video, canvas, ctx;
let ws;
let isTracking = false;
let countdown = 5;
let countdownInterval;
let isInCorrectPose = false;
let processingFrame = false;
let stream = null;
let lastLandmarks = null; // For smoothing
let smoothingFactor = 0.5; // Reduced for 60fps (less lag, still smooth)
let landmarkHistory = []; // Store multiple frames for better smoothing
let maxHistoryFrames = 3; // Reduced for 60fps (less latency)

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusIndicator = document.getElementById('statusIndicator');
const accuracyScore = document.getElementById('accuracyScore');
const feedback = document.getElementById('feedback');
const countdownDisplay = document.getElementById('countdown');
const countdownContainer = document.getElementById('countdownContainer');
const completionMessage = document.getElementById('completionMessage');
const beepSound = document.getElementById('beepSound');

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    video = document.getElementById('video');
    canvas = document.getElementById('canvas');
    ctx = canvas.getContext('2d');
    
    startBtn.addEventListener('click', startCamera);
    stopBtn.addEventListener('click', stopCamera);
    
    // Check camera availability
    checkCameraAvailability();
});

async function checkCameraAvailability() {
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const videoDevices = devices.filter(device => device.kind === 'videoinput');
        
        if (videoDevices.length === 0) {
            feedback.textContent = '⚠️ No camera detected. Please connect a camera.';
            startBtn.disabled = true;
        } else {
            console.log(`Found ${videoDevices.length} camera(s)`);
        }
    } catch (error) {
        console.error('Error checking camera:', error);
    }
}

async function startCamera() {
    try {
        feedback.textContent = '📹 Starting camera...';
        startBtn.disabled = true;
        
        // Request camera with square aspect ratio for better mobile view
        const constraints = {
            video: {
                width: { ideal: 1080, max: 1920 },
                height: { ideal: 1080, max: 1920 },
                facingMode: 'user',
                frameRate: { ideal: 60, max: 60 },
                aspectRatio: { ideal: 1 } // Square ratio
            },
            audio: false
        };
        
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        
        video.srcObject = stream;
        
        // Wait for video to be ready
        await new Promise((resolve) => {
            video.onloadedmetadata = () => {
                video.play();
                resolve();
            };
        });
        
        // Set canvas size to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Hide placeholder
        const placeholder = document.getElementById('cameraPlaceholder');
        if (placeholder) {
            placeholder.classList.add('hidden');
        }
        
        console.log(`Camera started: ${video.videoWidth}x${video.videoHeight}`);
        
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-block';
        
        // Connect WebSocket
        connectWebSocket();
        
        feedback.textContent = '✓ Camera ready! Position yourself for the exercise.';
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        startBtn.disabled = false;
        
        if (error.name === 'NotAllowedError') {
            feedback.textContent = '❌ Camera access denied. Please allow camera permissions and refresh.';
        } else if (error.name === 'NotFoundError') {
            feedback.textContent = '❌ No camera found. Please connect a camera.';
        } else if (error.name === 'NotReadableError') {
            feedback.textContent = '❌ Camera is in use by another application.';
        } else {
            feedback.textContent = `❌ Camera error: ${error.message}`;
        }
    }
}

function stopCamera() {
    isTracking = false;
    processingFrame = false;
    lastLandmarks = null; // Reset smoothing
    landmarkHistory = []; // Clear history
    
    // Stop video stream
    if (stream) {
        stream.getTracks().forEach(track => {
            track.stop();
            console.log('Camera track stopped');
        });
        stream = null;
    }
    
    if (video) {
        video.srcObject = null;
    }
    
    // Close WebSocket
    if (ws) {
        ws.close();
        ws = null;
    }
    
    // Clear countdown
    if (countdownInterval) {
        clearInterval(countdownInterval);
        countdownInterval = null;
    }
    
    // Reset UI
    startBtn.style.display = 'inline-block';
    startBtn.disabled = false;
    stopBtn.style.display = 'none';
    
    // Show placeholder
    const placeholder = document.getElementById('cameraPlaceholder');
    if (placeholder) {
        placeholder.classList.remove('hidden');
    }
    
    if (ctx) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    
    feedback.textContent = 'Camera stopped.';
    console.log('Camera stopped successfully');
}

function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/pose`;
    
    console.log('Connecting to WebSocket:', wsUrl);
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('✓ WebSocket connected');
        isTracking = true;
        processingFrame = false;
        processFrame();
    };
    
    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            handlePoseData(data);
            processingFrame = false; // Ready for next frame
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
            processingFrame = false;
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        feedback.textContent = '❌ Connection error. Please refresh the page.';
        isTracking = false;
    };
    
    ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        isTracking = false;
        
        if (event.code !== 1000) { // Not a normal closure
            feedback.textContent = '⚠️ Connection lost. Please refresh the page.';
        }
    };
}

function processFrame() {
    if (!isTracking) {
        return;
    }
    
    // Check if video is ready
    if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) {
        requestAnimationFrame(processFrame);
        return;
    }
    
    // Skip if still processing previous frame
    if (processingFrame) {
        setTimeout(() => requestAnimationFrame(processFrame), 50);
        return;
    }
    
    // Check WebSocket connection
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.warn('WebSocket not ready');
        setTimeout(() => requestAnimationFrame(processFrame), 100);
        return;
    }
    
    try {
        // Draw current video frame to canvas
        ctx.save();
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        ctx.restore();
        
        // Capture frame as base64 (optimized quality for 60fps)
        const imageData = canvas.toDataURL('image/jpeg', 0.75);
        
        // Send to backend
        processingFrame = true;
        ws.send(JSON.stringify({
            type: 'frame',
            image: imageData,
            exercise_id: exerciseId
        }));
        
    } catch (error) {
        console.error('Error processing frame:', error);
        processingFrame = false;
    }
    
    // Schedule next frame (60 FPS for ultra-smooth performance)
    setTimeout(() => {
        requestAnimationFrame(processFrame);
    }, 16);
}

function handlePoseData(data) {
    if (!data.success) {
        feedback.textContent = data.message || 'No pose detected';
        updateStatusIndicator('red', 0);
        resetCountdown();
        
        // Update mobile UI
        updateMobileUI(0, data.message || 'No pose detected', 'red');
        return;
    }
    
    const { landmarks, accuracy, feedback: feedbackText, color } = data;
    
    // Update desktop UI
    accuracyScore.textContent = `${Math.round(accuracy)}%`;
    feedback.textContent = feedbackText;
    updateStatusIndicator(color, accuracy);
    
    // Update mobile UI
    updateMobileUI(accuracy, feedbackText, color);
    
    // Draw skeleton
    drawSkeleton(landmarks, color);
    
    // Handle countdown - starts at 70% accuracy
    if (accuracy >= 70 && color === 'green') {
        if (!isInCorrectPose) {
            isInCorrectPose = true;
            startCountdown();
        }
    } else {
        if (isInCorrectPose) {
            isInCorrectPose = false;
            resetCountdown();
        }
    }
}

function updateMobileUI(accuracy, feedbackText, color) {
    const mobileAccuracy = document.getElementById('mobileAccuracy');
    const mobileFeedback = document.getElementById('mobileFeedback');
    
    if (mobileAccuracy) {
        mobileAccuracy.textContent = `${Math.round(accuracy)}%`;
        mobileAccuracy.style.color = color === 'green' ? '#10b981' : color === 'yellow' ? '#f59e0b' : '#ef4444';
    }
    
    if (mobileFeedback) {
        mobileFeedback.textContent = feedbackText;
        mobileFeedback.style.borderLeft = `3px solid ${color === 'green' ? '#10b981' : color === 'yellow' ? '#f59e0b' : '#ef4444'}`;
    }
}

function updateStatusIndicator(color, accuracy) {
    statusIndicator.className = `status-indicator ${color}`;
}

function drawSkeleton(landmarks, color) {
    if (!landmarks || landmarks.length === 0) return;
    
    // Advanced multi-frame smoothing with weighted average
    landmarkHistory.push(landmarks);
    if (landmarkHistory.length > maxHistoryFrames) {
        landmarkHistory.shift();
    }
    
    // Weighted average - recent frames have more weight
    if (landmarkHistory.length > 1) {
        landmarks = landmarks.map((landmark, i) => {
            let weightedX = 0, weightedY = 0, totalWeight = 0;
            
            landmarkHistory.forEach((frame, frameIndex) => {
                // More recent frames get higher weight
                const weight = (frameIndex + 1) / landmarkHistory.length;
                weightedX += frame[i][0] * weight;
                weightedY += frame[i][1] * weight;
                totalWeight += weight;
            });
            
            return [
                weightedX / totalWeight,
                weightedY / totalWeight,
                landmark[2],
                landmark[3]
            ];
        });
    }
    
    // Additional exponential smoothing with last frame
    if (lastLandmarks && lastLandmarks.length === landmarks.length) {
        landmarks = landmarks.map((landmark, i) => {
            // Only smooth if visibility is good
            if (landmark[3] > 0.5 && lastLandmarks[i][3] > 0.5) {
                return [
                    lastLandmarks[i][0] * smoothingFactor + landmark[0] * (1 - smoothingFactor),
                    lastLandmarks[i][1] * smoothingFactor + landmark[1] * (1 - smoothingFactor),
                    landmark[2],
                    landmark[3]
                ];
            }
            return landmark;
        });
    }
    lastLandmarks = landmarks;
    
    // Clear and redraw with anti-aliasing
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Enable image smoothing for better quality
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Set color based on pose accuracy with smooth transitions
    let drawColor, glowColor;
    if (color === 'green') {
        drawColor = '#10b981';
        glowColor = 'rgba(16, 185, 129, 0.5)';
    } else if (color === 'yellow') {
        drawColor = '#f59e0b';
        glowColor = 'rgba(245, 158, 11, 0.5)';
    } else {
        drawColor = '#ef4444';
        glowColor = 'rgba(239, 68, 68, 0.5)';
    }
    
    // Define all body connections for complete skeleton
    const connections = [
        // Torso
        [11, 12], [11, 23], [12, 24], [23, 24],
        // Left arm
        [11, 13], [13, 15],
        // Right arm
        [12, 14], [14, 16],
        // Left leg
        [23, 25], [25, 27], [27, 29], [27, 31],
        // Right leg
        [24, 26], [26, 28], [28, 30], [28, 32],
        // Face/head (minimal)
        [0, 1], [1, 2], [2, 3], [3, 7],
        [0, 4], [4, 5], [5, 6], [6, 8]
    ];
    
    // Filter connections based on visibility
    const visibleConnections = connections.filter(([start, end]) => {
        return landmarks[start] && landmarks[end] && 
               landmarks[start][3] > 0.6 && landmarks[end][3] > 0.6;
    });
    
    // Draw outer glow layer for depth
    ctx.lineWidth = 12;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = glowColor;
    ctx.shadowBlur = 20;
    ctx.shadowColor = drawColor;
    
    visibleConnections.forEach(([start, end]) => {
        const startX = landmarks[start][0] * canvas.width;
        const startY = landmarks[start][1] * canvas.height;
        const endX = landmarks[end][0] * canvas.width;
        const endY = landmarks[end][1] * canvas.height;
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    });
    
    // Draw main skeleton lines
    ctx.lineWidth = 8;
    ctx.strokeStyle = drawColor;
    ctx.shadowBlur = 12;
    
    visibleConnections.forEach(([start, end]) => {
        const startX = landmarks[start][0] * canvas.width;
        const startY = landmarks[start][1] * canvas.height;
        const endX = landmarks[end][0] * canvas.width;
        const endY = landmarks[end][1] * canvas.height;
        
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    });
    
    // Draw joints with enhanced visibility
    ctx.shadowBlur = 15;
    
    // Key joints for exercise tracking (larger and more prominent)
    const keyJoints = [
        0,  // Nose
        11, 12, // Shoulders
        13, 14, // Elbows
        15, 16, // Wrists
        23, 24, // Hips
        25, 26, // Knees
        27, 28, // Ankles
        29, 30, 31, 32 // Feet
    ];
    
    keyJoints.forEach(index => {
        if (landmarks[index] && landmarks[index][3] > 0.6) {
            const x = landmarks[index][0] * canvas.width;
            const y = landmarks[index][1] * canvas.height;
            const visibility = landmarks[index][3];
            
            // Size based on visibility
            const baseSize = 10;
            const size = baseSize * visibility;
            
            // Outer glow circle
            ctx.fillStyle = glowColor;
            ctx.beginPath();
            ctx.arc(x, y, size + 4, 0, 2 * Math.PI);
            ctx.fill();
            
            // Main joint circle
            ctx.fillStyle = drawColor;
            ctx.beginPath();
            ctx.arc(x, y, size, 0, 2 * Math.PI);
            ctx.fill();
            
            // White center for contrast
            ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            ctx.beginPath();
            ctx.arc(x, y, size * 0.5, 0, 2 * Math.PI);
            ctx.fill();
        }
    });
    
    // Reset shadow
    ctx.shadowBlur = 0;
}

function startCountdown() {
    countdown = exerciseDuration;
    countdownDisplay.textContent = countdown;
    countdownContainer.style.display = 'block';
    
    // Show mobile countdown
    const mobileCountdownContainer = document.getElementById('mobileCountdownContainer');
    const mobileCountdown = document.getElementById('mobileCountdown');
    if (mobileCountdownContainer) {
        mobileCountdownContainer.style.display = 'block';
        mobileCountdown.textContent = countdown;
    }
    
    countdownInterval = setInterval(() => {
        countdown--;
        countdownDisplay.textContent = countdown;
        if (mobileCountdown) {
            mobileCountdown.textContent = countdown;
        }
        
        if (countdown <= 0) {
            clearInterval(countdownInterval);
            exerciseCompleted();
        }
    }, 1000);
}

function resetCountdown() {
    if (countdownInterval) {
        clearInterval(countdownInterval);
    }
    countdown = exerciseDuration;
    countdownDisplay.textContent = countdown;
    countdownContainer.style.display = 'none';
    
    // Hide mobile countdown
    const mobileCountdownContainer = document.getElementById('mobileCountdownContainer');
    const mobileCountdown = document.getElementById('mobileCountdown');
    if (mobileCountdownContainer) {
        mobileCountdownContainer.style.display = 'none';
        mobileCountdown.textContent = countdown;
    }
}

function exerciseCompleted() {
    // Play beep sound
    beepSound.play();
    
    // Show completion message
    completionMessage.classList.add('show');
    
    // Stop tracking
    stopCamera();
    
    // Confetti effect (simple)
    feedback.textContent = '🎉 Excellent work! Exercise completed successfully!';
}
