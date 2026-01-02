from fastapi import FastAPI, WebSocket, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(title="Exercise Body Tracker")

# Setup templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Load exercises
with open("exercises/poses.json", "r") as f:
    exercises_data = json.load(f)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "exercises": exercises_data["exercises"]
    })

@app.get("/exercise/{exercise_id}", response_class=HTMLResponse)
async def exercise_page(request: Request, exercise_id: str):
    exercise = next((ex for ex in exercises_data["exercises"] if ex["id"] == exercise_id), None)
    if not exercise:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "exercises": exercises_data["exercises"],
            "error": "Exercise not found"
        })
    
    return templates.TemplateResponse("exercise.html", {
        "request": request,
        "exercise": exercise
    })

@app.websocket("/ws/pose")
async def websocket_pose(websocket: WebSocket):
    await websocket.accept()
    
    try:
        from app.services.pose_detector import PoseDetector
        detector = PoseDetector()
        
        while True:
            data = await websocket.receive_json()
            
            if data.get("type") == "frame":
                # Process the frame data
                result = detector.process_pose(data)
                await websocket.send_json(result)
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
