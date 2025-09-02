from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import uuid
import requests

# folders for local storage (fallback or dev)
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
RESULT_FOLDER = os.path.join(os.getcwd(), "results")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB

API_URL = "http://127.0.0.1:8000/jobs"  # FastAPI backend

# simple in-memory job tracking for dev
jobs_status = {}

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    # generate unique job ID
    job_id = str(uuid.uuid4())

    # save to local uploads folder (optional)
    filename = f"{job_id}_{file.filename}"
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # enqueue the job in FastAPI/Celery
    files = {"file": (file.filename, open(filepath, "rb"), file.mimetype)}
    r = requests.post(API_URL, files=files)
    job_id = r.json().get("job_id", job_id)

    # mark as pending in local tracking
    jobs_status[job_id] = "Pending"

    return redirect(url_for("status", job_id=job_id))

@app.route("/status/<job_id>")
def status(job_id):
    # poll FastAPI for actual job status
    try:
        r = requests.get(f"{API_URL}/{job_id}")
        status = r.json().get("status", "Unknown")
    except:
        status = jobs_status.get(job_id, "Unknown")
    return render_template("status.html", job_id=job_id, status=status)

@app.route("/download/<job_id>")
def download(job_id):
    # try FastAPI download URL first
    try:
        r = requests.get(f"{API_URL}/{job_id}")
        if r.json().get("status") == "Completed":
            download_url = r.json()["download_url"]
            return redirect(download_url)
    except:
        pass

    # fallback local file
    files = [f for f in os.listdir(app.config["RESULT_FOLDER"]) if f.startswith(job_id)]
    if not files:
        return "File not ready", 404
    return send_from_directory(app.config["RESULT_FOLDER"], files[0], as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
