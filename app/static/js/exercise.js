let video, canvas, ctx;
let ws;
let isTracking = false;
let countdown = 10;
let countdownInterval;
let isInCorrectPose = false;
let processingFrame = false;
let stream = null;
let lastLandmarks = null; // For smoothing
let smoothingFactor = 0.5; // Smoothing between frames (0-1, higher = smoother but more lag)

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
        
        // Request camera with optimal settings
        const constraints = {
            video: {
                width: { ideal: 1280, max: 1920 },
                height: { ideal: 720, max: 1080 },
                facingMode: 'user',
                frameRate: { ideal: 30, max: 60 }
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
        
        // Capture frame as base64 (reduced quality for performance)
        const imageData = canvas.toDataURL('image/jpeg', 0.7);
        
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
    
    // Schedule next frame (30 FPS for smooth performance)
    setTimeout(() => {
        requestAnimationFrame(processFrame);
    }, 33);
}

function handlePoseData(data) {
    if (!data.success) {
        feedback.textContent = data.message || 'No pose detected';
        updateStatusIndicator('red', 0);
        resetCountdown();
        return;
    }
    
    const { landmarks, accuracy, feedback: feedbackText, color } = data;
    
    // Update UI
    accuracyScore.textContent = `${Math.round(accuracy)}%`;
    feedback.textContent = feedbackText;
    updateStatusIndicator(color, accuracy);
    
    // Draw skeleton
    drawSkeleton(landmarks, color);
    
    // Handle countdown
    if (accuracy >= 90 && color === 'green') {
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

function updateStatusIndicator(color, accuracy) {
    statusIndicator.className = `status-indicator ${color}`;
}

function drawSkeleton(landmarks, color) {
    if (!landmarks || landmarks.length === 0) return;
    
    // Apply smoothing to landmarks
    if (lastLandmarks && lastLandmarks.length === landmarks.length) {
        landmarks = landmarks.map((landmark, i) => {
            return [
                lastLandmarks[i][0] * smoothingFactor + landmark[0] * (1 - smoothingFactor),
                lastLandmarks[i][1] * smoothingFactor + landmark[1] * (1 - smoothingFactor),
                landmark[2],
                landmark[3]
            ];
        });
    }
    lastLandmarks = landmarks;
    
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Set color based on pose accuracy
    let drawColor;
    if (color === 'green') {
        drawColor = '#10b981';
    } else if (color === 'yellow') {
        drawColor = '#f59e0b';
    } else {
        drawColor = '#ef4444';
    }
    
    // Draw connections with thicker lines
    const connections = [
        [11, 12], [11, 13], [13, 15], [12, 14], [14, 16], // Arms
        [11, 23], [12, 24], [23, 24], // Torso
        [23, 25], [25, 27], [24, 26], [26, 28], // Legs
        [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5], [5, 6], [6, 8] // Face
    ];
    
    // Draw thicker lines with glow effect
    ctx.lineWidth = 6;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = drawColor;
    
    // Add shadow/glow effect
    ctx.shadowBlur = 8;
    ctx.shadowColor = drawColor;
    
    connections.forEach(([start, end]) => {
        if (landmarks[start] && landmarks[end]) {
            const startX = landmarks[start][0] * canvas.width;
            const startY = landmarks[start][1] * canvas.height;
            const endX = landmarks[end][0] * canvas.width;
            const endY = landmarks[end][1] * canvas.height;
            
            ctx.beginPath();
            ctx.moveTo(startX, startY);
            ctx.lineTo(endX, endY);
            ctx.stroke();
        }
    });
    
    // Draw joints with larger circles
    ctx.shadowBlur = 10;
    ctx.fillStyle = drawColor;
    
    landmarks.forEach((landmark) => {
        const x = landmark[0] * canvas.width;
        const y = landmark[1] * canvas.height;
        
        ctx.beginPath();
        ctx.arc(x, y, 8, 0, 2 * Math.PI);
        ctx.fill();
        
        // Add white center for better visibility
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fill();
        
        ctx.fillStyle = drawColor;
    });
    
    // Reset shadow
    ctx.shadowBlur = 0;
}

function startCountdown() {
    countdown = exerciseDuration;
    countdownDisplay.textContent = countdown;
    countdownContainer.style.display = 'block';
    
    countdownInterval = setInterval(() => {
        countdown--;
        countdownDisplay.textContent = countdown;
        
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
