from pathlib import Path
from app.models.job import SessionLocal, Job, JobStatus, JobImage
from app.image_processing import fetch, deduplicate, filter

def run_image_pipeline(job_id: int):
    """The main background task. Its only job is to process images."""
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job: return

        job.status = JobStatus.PROCESSING; db.commit()

        num_to_fetch = job.image_count * 2
        downloaded_paths = fetch.fetch_images(job.query, num_to_fetch, job.id)
        if not downloaded_paths:
            job.status = JobStatus.FAILED; db.commit(); return
        
        unique_paths = deduplicate.deduplicate_images(downloaded_paths, job_id=job.id)
        if not unique_paths:
            job.status = JobStatus.FAILED; db.commit(); return

        filtered_paths = filter.filter_images(unique_paths, query=job.query, job_id=job.id)
        if not filtered_paths:
            job.status = JobStatus.FAILED; db.commit(); return

        print(f"[JOB {job_id}] 💾 Saving {len(filtered_paths)} final image paths to DB...")
        for path in filtered_paths:
            db.add(JobImage(job_id=job.id, file_path=path))
        
        job.status = JobStatus.COMPLETED
        db.commit()
        print(f"🎉 [JOB {job_id}] Pipeline finished successfully. Awaiting email dispatch.")
    finally:
        db.close()

