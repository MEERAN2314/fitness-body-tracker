# Exercise Body Tracker

An AI-powered web application that tracks your body movements during exercises to ensure proper form and prevent injuries. Uses MediaPipe for real-time pose detection and provides instant feedback with visual indicators.

## Features

- 🎯 Real-time body tracking with skeleton visualization
- ✅ Form accuracy detection (red/yellow/green indicators)
- ⏱️ 10-second hold timer for correct poses
- 🔊 Audio feedback on exercise completion
- 💪 Multiple yoga poses (Tree Pose, Warrior II, Plank)
- 📱 Responsive design with blue/white theme
- 🎨 Professional UI with smooth animations

## Tech Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **AI/ML**: MediaPipe, OpenCV, NumPy
- **Real-time Communication**: WebSockets
- **Templating**: Jinja2

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd exercise-tracker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI server:
```bash
python app/main.py
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

3. Allow camera permissions when prompted

## How to Use

1. **Choose an Exercise**: Select from available yoga poses on the home page
2. **Start Camera**: Click "Start Camera" to begin tracking
3. **Position Yourself**: Ensure you're fully visible in the camera frame
4. **Follow Instructions**: Read the exercise instructions on the right panel
5. **Match the Pose**: Your skeleton will turn:
   - 🔴 **Red**: Incorrect form (< 70% accuracy)
   - 🟡 **Yellow**: Close (70-90% accuracy)
   - 🟢 **Green**: Correct form (> 90% accuracy)
6. **Hold the Pose**: When green, hold for 10 seconds
7. **Complete**: Hear a beep sound when finished!

## Project Structure

```
exercise-tracker/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── services/
│   │   └── pose_detector.py    # MediaPipe pose detection logic
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css       # Styling
│   │   ├── js/
│   │   │   └── exercise.js     # Frontend logic
│   │   └── sounds/
│   │       └── beep.mp3        # Completion sound
│   └── templates/
│       ├── base.html           # Base template
│       ├── index.html          # Home page
│       └── exercise.html       # Exercise tracking page
├── exercises/
│   └── poses.json              # Exercise definitions
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Adding New Exercises

Edit `exercises/poses.json` to add new exercises:

```json
{
  "id": "your-exercise-id",
  "name": "Exercise Name",
  "description": "Brief description",
  "difficulty": "beginner|intermediate|advanced",
  "duration": 10,
  "instructions": [
    "Step 1",
    "Step 2"
  ]
}
```

Then update the pose detection logic in `app/services/pose_detector.py` to add custom validation for your exercise.

## Browser Compatibility

- Chrome/Edge: ✅ Fully supported
- Firefox: ✅ Fully supported
- Safari: ✅ Supported (requires HTTPS for camera access)

## Requirements

- Python 3.9 or higher
- Webcam
- Modern web browser with WebRTC support
- Good lighting conditions for best tracking results

## Troubleshooting

**Camera not working?**
- Ensure camera permissions are granted
- Check if another application is using the camera
- Try refreshing the page

**Pose not detected?**
- Ensure you're fully visible in the frame
- Improve lighting conditions
- Stand 3-6 feet away from the camera

**Slow performance?**
- Close other applications
- Reduce video quality in the code if needed
- Ensure good internet connection for WebSocket

## Future Enhancements

- [ ] Add more exercise types (strength training, stretching)
- [ ] User accounts and progress tracking
- [ ] Exercise history and statistics
- [ ] Custom workout routines
- [ ] Mobile app version
- [ ] Multi-language support
- [ ] Voice guidance

## License

MIT License - Feel free to use this project for learning and development.

## Credits

- MediaPipe by Google
- FastAPI framework
- OpenCV library

---

Stay safe, stay fit! 💪
