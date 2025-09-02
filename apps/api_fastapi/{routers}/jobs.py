from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from core.storage import put_obj, get_obj_url
from pipeline.task import process_docx
import uuid

router = APIRouter()
JOB_STATUS = {}  # in-memory job tracking; replace with Redis in prod

@router.post("/")
async def submit_job(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    key_in = f"uploads/{job_id}_{file.filename}"
    content = await file.read()
    put_obj(key_in, content)

    # enqueue Celery task
    process_docx.delay(job_id, key_in)

    JOB_STATUS[job_id] = "Pending"
    return {"job_id": job_id}

@router.get("/{job_id}")
def get_job_status(job_id: str):
    status = JOB_STATUS.get(job_id, "Unknown")
    download_url = None
    if status == "Completed":
        download_url = get_obj_url(f"results/{job_id}.docx")
    return {"status": status, "download_url": download_url}
