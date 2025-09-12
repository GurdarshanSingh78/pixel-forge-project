from app.models.job import SessionLocal, Job, JobStatus
from app.services import email_service

async def check_and_send_notifications():
    """Queries the DB for completed jobs that need an email, and sends the notification."""
    print("⏰ Email scheduler checking for jobs...")
    db = SessionLocal()
    try:
        jobs_to_notify = db.query(Job).filter(
            Job.status == JobStatus.COMPLETED,
            Job.email_sent == False
        ).all()

        if not jobs_to_notify:
            print("No new jobs to notify.")
            return

        for job in jobs_to_notify:
            print(f"Found completed job #{job.id}. Preparing to send email.")
            results_url = f"http://127.0.0.1:8000/api/results/{job.id}"
            
            # --- THIS IS THE FIX ---
            # The try/except block now correctly wraps the send operation AND the database update.
            try:
                await email_service.send_email_notification(
                    recipient_email=job.email,
                    query=job.query,
                    results_url=results_url
                )
                # This code will ONLY run if the email sending was successful
                job.email_sent = True
                db.commit()
                print(f"✅ Email for job #{job.id} sent successfully.")
            except Exception as e:
                # This will run if send_email_notification fails for any reason
                print(f"❌ FAILED to send email for job #{job.id}. Error: {e}")

    finally:
        db.close()

