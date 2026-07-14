import traceback

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
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

    finally:
        if 'video_path' in locals() and os.path.exists(video_path):
            os.remove(video_path)