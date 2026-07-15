from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import traceback

from btcas_pipeline import process_video

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/inspect")
async def inspect_video(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            video_path = tmp.name

        print("Video saved:", video_path)

        result = process_video(video_path, camera_side="LEFT")

        print("Processing completed")

        return {
            "success": True,
            "inspection": result
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise e

@app.get("/test-model")
def test_model():
    try:
        from btcas_pipeline import process_video
        return {"status": "import_ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/inspect-test")
async def inspect_test(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type
    }

@app.post("/inspect-debug")
async def inspect_debug(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        video_path = tmp.name

    try:
        print("Video saved:", video_path)

        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return {"error": "OpenCV cannot open video"}

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        cap.release()

        return {
            "success": True,
            "frames": total_frames,
            "fps": fps
        }

    except Exception as e:
        return {"error": str(e)}