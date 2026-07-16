from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import traceback
import cv2
from fastapi import FastAPI
import json
import os
from ultralytics import YOLO


from btcas_pipeline import (
    process_video,
    _run_inference
)
import btcas_pipeline
from btcas_pipeline import _run_inference

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

# @app.post("/inspect")
# async def inspect_video(file: UploadFile = File(...)):
#     try:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
#             tmp.write(await file.read())
#             video_path = tmp.name

#         print("Video saved:", video_path)

#         result = process_video(video_path, camera_side="LEFT")

#         print("Processing completed")

#         return {
#             "success": True,
#             "inspection": result
#         }

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         raise e

@app.post("/inspect")
async def inspect_video(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
            tmp.write(await file.read())
            video_path = tmp.name

        result = process_video(video_path, camera_side="LEFT")

        return {
            "success": True,
            "inspection": result
        }

    except Exception as e:
        import traceback
        traceback.print_exc()

        return {
            "success": False,
            "error": str(e)
        }

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

@app.get("/debug")
def debug():
    return {
        "resize_exists": "_resize_for_inference" in globals(),
        "load_model_exists": "_load_model" in globals(),
        "run_inference_exists": "_run_inference" in globals(),
    }
@app.get("/debug-model")
def debug_model():
    try:
        from btcas_pipeline import _load_model

        model = _load_model()

        return {
            "success": True,
            "model_loaded": True
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
@app.get("/model-check")
def model_check():
    import os

    return {
        "exists": os.path.exists("btcas_yolov8s_v2_best.pt"),
        "cwd": os.getcwd()
    }

@app.post("/inspect-debug-2")
async def inspect_debug_2(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        video_path = tmp.name

    cap = cv2.VideoCapture(video_path)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return {"error": "Cannot read frame"}

    boxes = _run_inference(frame)

    return {
        "success": True,
        "detections": len(boxes)
    }
@app.get("/model-info")
def model_info():
    from ultralytics import YOLO

    model = YOLO("btcas_yolov8s_v2_best.pt")

    return {
        "names": model.names,
        "classes": len(model.names)
    }
@app.get("/single-test")
def single_test():
    from ultralytics import YOLO
    import cv2

    model = YOLO("btcas_yolov8s_v2_best.pt")

    img = cv2.imread("test.jpg")   # put a known training image in project

    results = model(img)

    total = 0

    for r in results:
        if r.boxes is not None:
            total += len(r.boxes)

    return {"detections": total}



@app.get("/latest-result")
def latest_result():
    try:
        file_path = "latest_result.json"

        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": "No inspection result available"
            }

        with open(file_path, "r") as f:
            data = json.load(f)

        return {
            "success": True,
            "inspection": data
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }



model = YOLO("btcas_yolov8s_v2_best.pt")

@app.get("/live-inspection")
def live_inspection():

    cap = cv2.VideoCapture(0)

    ret, frame = cap.read()

    cap.release()

    if not ret:
        return {"success": False, "error": "Camera not working"}

    results = model(frame)

    detections = []

    for r in results:
        if r.boxes is None:
            continue

        for b in r.boxes:
            detections.append({
                "class": int(b.cls[0]),
                "confidence": float(b.conf[0])
            })

    return {
        "success": True,
        "detections": detections
    }