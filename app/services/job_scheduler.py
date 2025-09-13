from app.models.job import SessionLocal, Job, JobStatus
from app.services import email_service
from app.image_processing.pipeline import run_image_pipeline
from app.core.config import settings

async def check_for_jobs():
    """
    The main worker function that runs on a schedule.
    It processes one pending job and sends notifications for all completed jobs.
    """
    print("⏰ Worker checking for jobs...")
    await process_one_pending_job()
    await send_completed_notifications()

async def process_one_pending_job():
    """Finds the oldest pending job and runs the image pipeline on it."""
    db = SessionLocal()
    try:
        # Find the oldest job that is still pending
        job_to_process = db.query(Job).filter(Job.status == JobStatus.PENDING).order_by(Job.id).first()
        
        if job_to_process:
            print(f"Found pending job #{job_to_process.id}. Starting pipeline...")
            # Mark job as PROCESSING so another worker doesn't pick it up
            job_to_process.status = JobStatus.PROCESSING
            db.commit()
            # Run the main pipeline
            await run_image_pipeline(job_to_process.id)
    finally:
        db.close()

async def send_completed_notifications():
    """Finds completed jobs that haven't received an email and sends notifications."""
    db = SessionLocal()
    try:
        jobs_to_notify = db.query(Job).filter(
            Job.status == JobStatus.COMPLETED,
            Job.email_sent == False
        ).all()

        if not jobs_to_notify:
            return

        for job in jobs_to_notify:
            print(f"Found completed job #{job.id}. Preparing to send email notification.")
            results_url = f"{settings.BASE_URL}/api/results/{job.id}"
            try:
                await email_service.send_email_notification(
                    recipient_email=job.email,
                    query=job.query,
                    results_url=results_url
                )
                # If successful, mark the email as sent to prevent re-sending
                job.email_sent = True
                db.commit()
                print(f"✅ Email for job #{job.id} sent successfully.")
            except Exception as e:
                print(f"❌ FAILED to send email for job #{job.id}. Error: {e}")
    finally:
        db.close()

