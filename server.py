import os
import uuid
import asyncio
from typing import Dict, List
from fastapi import FastAPI, BackgroundTasks, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from config import STORAGE_DIR, OUTPUT_DIR, PREVIEWS_DIR
from core.state import DeckState
from core.orchestrator import run_presentation_pipeline
from core.logger import logger

if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="AI Presentation Designer Agent API")

# Enable CORS for React Frontend (Vite default port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for active tasks and WebSocket connections
tasks_db: Dict[str, Dict] = {}
websocket_connections: Dict[str, List[WebSocket]] = {}

class PresentationRequest(BaseModel):
    prompt: str
    background_notes: str = ""
    theme_color: str = "#0D6EFD"

# WebSocket Connection Manager
async def notify_task_update(task_id: str, step: str, message: str, data: dict = None):
    if task_id in tasks_db:
        tasks_db[task_id]["current_step"] = step
        tasks_db[task_id]["logs"].append(message)
        if data:
            tasks_db[task_id]["data"] = data
            
    if task_id in websocket_connections:
        payload = {
            "task_id": task_id,
            "step": step,
            "message": message,
            "data": data or {}
        }
        for ws in websocket_connections[task_id]:
            try:
                await ws.send_json(payload)
            except Exception:
                pass

def background_pipeline_worker(task_id: str, prompt: str, notes: str, theme_color: str):
    """Executes the LangGraph presentation pipeline in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(notify_task_update(task_id, "CONTENT_DRAFT", "Content Agent drafting slide plan..."))
        
        def sync_update_callback(step: str, msg: str):
            loop.run_until_complete(notify_task_update(task_id, step, msg))
            
        # Execute LangGraph pipeline
        deck_state = run_presentation_pipeline(
            user_prompt=prompt, 
            background_material=notes,
            theme_color=theme_color,
            update_callback=sync_update_callback
        )
        
        output_path = deck_state.pptx_output_path
        filename = os.path.basename(output_path) if output_path else "presentation_deck.pptx"
        
        slides_summary = [
            {
                "slide_number": s.slide_number,
                "title": s.title,
                "layout_type": s.layout_type,
                "preview_url": f"/api/previews/{task_id}/slide_preview_{s.slide_number}.png"
            }
            for s in deck_state.slides
        ]
        
        loop.run_until_complete(notify_task_update(
            task_id,
            "COMPLETE",
            "Presentation complete and ready for download!",
            {
                "download_url": f"/api/download/{task_id}",
                "slides": slides_summary,
                "total_slides": len(deck_state.slides)
            }
        ))
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        loop.run_until_complete(notify_task_update(task_id, "ERROR", f"Pipeline failed: {str(e)}"))

@app.post("/api/generate")
def generate_presentation(req: PresentationRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "task_id": task_id,
        "prompt": req.prompt,
        "current_step": "INITIATED",
        "logs": ["Job created. Initializing AI Agent pipeline..."],
        "data": {}
    }
    
    background_tasks.add_task(background_pipeline_worker, task_id, req.prompt, req.background_notes, req.theme_color)
    return {"task_id": task_id, "status": "started", "websocket_url": f"/ws/status/{task_id}"}

@app.get("/api/status/{task_id}")
def get_task_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks_db[task_id]

@app.websocket("/ws/status/{task_id}")
async def websocket_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    if task_id not in websocket_connections:
        websocket_connections[task_id] = []
    websocket_connections[task_id].append(websocket)
    
    # Send current state immediately on connect
    if task_id in tasks_db:
        await websocket.send_json({
            "task_id": task_id,
            "step": tasks_db[task_id]["current_step"],
            "message": "Connected to live stream.",
            "data": tasks_db[task_id].get("data", {})
        })
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if task_id in websocket_connections and websocket in websocket_connections[task_id]:
            websocket_connections[task_id].remove(websocket)

@app.get("/api/download/{task_id}")
def download_presentation(task_id: str):
    pptx_path = os.path.join(OUTPUT_DIR, "presentation_deck.pptx")
    if not os.path.exists(pptx_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=pptx_path,
        filename="AI_Presentation_Deck.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )

@app.get("/api/previews/{task_id}/{filename}")
def get_preview_file(task_id: str, filename: str):
    file_path = os.path.join(PREVIEWS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Preview file not found")
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
