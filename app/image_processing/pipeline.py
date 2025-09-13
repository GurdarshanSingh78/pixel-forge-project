from app.models.job import SessionLocal, Job, JobStatus, JobImage
from app.image_processing import fetch, deduplicate, filter

# The pipeline is now an async function to be called by the async scheduler
async def run_image_pipeline(job_id: int):
    """
    The main background task. It finds a job and runs the full image processing pipeline.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        # Safety check: ensure the job exists and is in the correct state
        if not job or job.status != JobStatus.PROCESSING:
            print(f"[PIPELINE-WARN] Job #{job_id} not found or not in PROCESSING state. Skipping.")
            return

        # --- 1. Fetch Images ---
        num_to_fetch = job.image_count * 2
        downloaded_paths = fetch.fetch_images(job.query, num_to_fetch, job.id)
        if not downloaded_paths:
            print(f"[JOB {job.id}] ❌ Fetching failed. Marking job as FAILED.")
            job.status = JobStatus.FAILED
            db.commit()
            return
        
        # --- 2. Deduplicate Images ---
        unique_paths = deduplicate.deduplicate_images(downloaded_paths, job_id=job.id)
        if not unique_paths:
            print(f"[JOB {job.id}] ❌ Deduplication resulted in zero images. Marking job as FAILED.")
            job.status = JobStatus.FAILED
            db.commit()
            return

        # --- 3. Filter Images (AI) ---
        filtered_paths = filter.filter_images(unique_paths, query=job.query, job_id=job.id)
        if not filtered_paths:
            print(f"[JOB {job.id}] ❌ AI Filtering resulted in zero images. Marking job as FAILED.")
            job.status = JobStatus.FAILED
            db.commit()
            return

        # --- 4. Save Results ---
        print(f"[JOB {job.id}] 💾 Saving {len(filtered_paths)} final image paths to DB...")
        for path in filtered_paths:
            db.add(JobImage(job_id=job.id, file_path=path))
        
        # --- 5. Mark as Complete ---
        job.status = JobStatus.COMPLETED
        db.commit()
        print(f"🎉 [JOB {job.id}] Pipeline finished successfully. Awaiting email dispatch.")

    finally:
        db.close()

