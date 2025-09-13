from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field, computed_field
from sqlalchemy.orm import Session
from datetime import datetime
import os
import io
import zipfile

from app.models.job import Job, JobType, JobStatus, JobImage, SessionLocal
from app.image_processing.pipeline import run_image_pipeline
from app.core.paths import TEMPLATES_DIR

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# --- Pydantic Models for Data Validation and Serialization ---

class ImageRequest(BaseModel):
    """Data model for the incoming form submission."""
    query: str
    email: EmailStr
    count: int = Field(..., gt=0, le=1000)

class JobCreationResponse(BaseModel):
    """Response model after a job is successfully created."""
    message: str
    job_id: int

class JobImageResponse(BaseModel):
    """Data model for a single image record in the database."""
    id: int
    file_path: str
    
    @computed_field
    @property
    def filename(self) -> str:
        return os.path.basename(self.file_path)

    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    """Data model for a single job, including its final images."""
    id: int
    query: str
    email: EmailStr
    image_count: int
    job_type: JobType
    status: JobStatus
    created_at: datetime
    images: List[JobImageResponse] = []
    class Config:
        from_attributes = True

# --- Database Dependency ---

def get_db():
    """Dependency function to get a DB session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- API Endpoints ---

@router.post("/request-images", response_model=JobCreationResponse, status_code=202)
async def handle_image_request(
    req: Request,
    request_data: ImageRequest,
    db: Session = Depends(get_db)
):
    """
    Accepts an image request and saves it to the database as PENDING.
    The background scheduler will pick it up and process it.
    """
    try:
        job_type = JobType.FREE if request_data.count <= 50 else JobType.PAID
        new_job = Job(
            query=request_data.query.strip(),
            email=request_data.email,
            image_count=request_data.count,
            job_type=job_type,
            status=JobStatus.PENDING
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        return {
            "message": "Job Accepted",
            "job_id": new_job.id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@router.get("/jobs", response_model=List[JobResponse])
async def get_all_jobs(db: Session = Depends(get_db), limit: int = Query(20, ge=1, le=100)):
    """Returns a list of recent jobs from the database."""
    return db.query(Job).order_by(Job.id.desc()).limit(limit).all()

@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_by_id(job_id: int, db: Session = Depends(get_db)):
    """Fetches a single job by ID, including its final images."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/results/{job_id}", name="get_job_results")
async def get_job_results(request: Request, job_id: int, db: Session = Depends(get_db)):
    """Fetches a job and its images and renders the results HTML page."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return templates.TemplateResponse("results.html", {"request": request, "job": job})

@router.get("/download/{job_id}", name="download_zip")
async def download_job_images_as_zip(job_id: int, db: Session = Depends(get_db)):
    """Finds a job, zips its final images, and streams the download."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job or not job.images:
        raise HTTPException(status_code=404, detail="No completed job or images found to download.")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for image in job.images:
            if os.path.exists(image.file_path):
                zf.write(image.file_path, os.path.basename(image.file_path))

    zip_buffer.seek(0)
    
    headers = {'Content-Disposition': f'attachment; filename="job_{job_id}_{job.query}.zip"'}
    return StreamingResponse(zip_buffer, media_type="application/x-zip-compressed", headers=headers)

