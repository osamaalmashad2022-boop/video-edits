"""
Remove Watermark - Web Application
====================================
Flask-based web interface for removing the Gemini Notebook 
watermark from videos by trimming the last 3.1 seconds.
"""

import os
import sys
import json
import uuid
import subprocess
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory

# ============================================================
# CONFIGURATION
# ============================================================
TRIM_SECONDS = 3.1
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "processed")
STATIC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 * 1024  # 2 GB max upload

VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v", ".ts", ".mts"}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

# ============================================================
# APP SETUP
# ============================================================
app = Flask(__name__, static_folder=STATIC_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

# In-memory job tracker
jobs = {}  # job_id -> { status, progress, filename, original_name, output_path, error, duration, new_duration }


# ============================================================
# VIDEO PROCESSING
# ============================================================
def get_video_duration(filepath: str) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", filepath],
            capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except Exception:
        return -1


def get_video_info(filepath: str) -> dict:
    """Get detailed video info using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration,size:stream=codec_type,width,height,r_frame_rate",
                "-of", "json", filepath
            ],
            capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        return json.loads(result.stdout)
    except Exception:
        return {}


def process_video(job_id: str, input_path: str, output_path: str):
    """Process a single video - runs in background thread."""
    job = jobs[job_id]
    job["status"] = "processing"
    job["progress"] = 10

    try:
        # Step 1: Get duration
        duration = get_video_duration(input_path)
        if duration <= 0:
            job["status"] = "error"
            job["error"] = "Could not read video duration"
            return

        if duration <= TRIM_SECONDS:
            job["status"] = "error"
            job["error"] = f"Video too short ({duration:.1f}s <= {TRIM_SECONDS}s)"
            return

        new_duration = duration - TRIM_SECONDS
        job["duration"] = round(duration, 2)
        job["new_duration"] = round(new_duration, 2)
        job["progress"] = 30

        # Step 2: Get video info
        info = get_video_info(input_path)
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                job["width"] = stream.get("width", 0)
                job["height"] = stream.get("height", 0)
                break

        job["progress"] = 50

        # Step 3: Trim video using ffmpeg (stream copy - no re-encoding)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", input_path,
                "-t", str(new_duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                output_path
            ],
            capture_output=True, text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )

        job["progress"] = 90

        if result.returncode == 0 and os.path.exists(output_path):
            input_size = os.path.getsize(input_path)
            output_size = os.path.getsize(output_path)
            job["input_size"] = input_size
            job["output_size"] = output_size
            job["status"] = "done"
            job["progress"] = 100
        else:
            job["status"] = "error"
            job["error"] = "FFmpeg processing failed"

    except Exception as e:
        job["status"] = "error"
        job["error"] = str(e)
    finally:
        # Clean up uploaded file after processing
        try:
            if os.path.exists(input_path):
                os.remove(input_path)
        except Exception:
            pass


# ============================================================
# ROUTES
# ============================================================
@app.route("/")
def index():
    return send_from_directory(STATIC_FOLDER, "index.html")


@app.route("/api/upload", methods=["POST"])
def upload_video():
    """Handle video upload and start processing."""
    if "video" not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    file = request.files["video"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in VIDEO_EXTENSIONS:
        return jsonify({"error": f"Unsupported format: {ext}"}), 400

    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]

    # Save uploaded file
    safe_filename = f"{job_id}{ext}"
    input_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    output_path = os.path.join(OUTPUT_FOLDER, safe_filename)
    file.save(input_path)

    # Create job entry
    jobs[job_id] = {
        "status": "uploading",
        "progress": 0,
        "filename": safe_filename,
        "original_name": file.filename,
        "output_path": output_path,
        "error": None,
        "duration": 0,
        "new_duration": 0,
        "input_size": os.path.getsize(input_path),
        "output_size": 0,
        "width": 0,
        "height": 0,
    }

    # Start processing in background thread
    thread = threading.Thread(target=process_video, args=(job_id, input_path, output_path))
    thread.daemon = True
    thread.start()

    return jsonify({"job_id": job_id, "filename": file.filename})


@app.route("/api/status/<job_id>")
def job_status(job_id):
    """Check job processing status."""
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404
    return jsonify(jobs[job_id])


@app.route("/api/download/<job_id>")
def download_video(job_id):
    """Download the processed video."""
    if job_id not in jobs:
        return jsonify({"error": "Job not found"}), 404

    job = jobs[job_id]
    if job["status"] != "done":
        return jsonify({"error": "Video not ready yet"}), 400

    output_path = job["output_path"]
    if not os.path.exists(output_path):
        return jsonify({"error": "Output file not found"}), 404

    # Use original filename for download
    original_name = job["original_name"]
    name_stem = Path(original_name).stem
    name_ext = Path(original_name).suffix
    download_name = f"{name_stem}_trimmed{name_ext}"

    return send_file(output_path, as_attachment=True, download_name=download_name)


@app.route("/api/cleanup/<job_id>", methods=["DELETE"])
def cleanup_job(job_id):
    """Clean up processed files and remove job."""
    if job_id in jobs:
        job = jobs[job_id]
        # Remove output file
        try:
            if os.path.exists(job.get("output_path", "")):
                os.remove(job["output_path"])
        except Exception:
            pass
        del jobs[job_id]
    return jsonify({"ok": True})


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print()
    print("  +=============================================+")
    print("  |   Remove Watermark - Web App                |")
    print("  |   Open: http://localhost:5000                |")
    print("  +=============================================+")
    print()
    
    import webbrowser
    webbrowser.open("http://localhost:5000")
    
    app.run(host="0.0.0.0", port=5000, debug=False)
