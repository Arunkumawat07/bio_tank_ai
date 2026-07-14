from fastapi import FastAPI, UploadFile, File
import tempfile
import os

from btcas_pipeline import process_video

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/inspect")
async def inspect_video(file: UploadFile = File(...)):
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        video_path = tmp.name

    try:
        result = process_video(video_path, camera_side="LEFT")

        return {
            "success": True,
            "inspection": result
        }

    finally:
        os.remove(video_path)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)