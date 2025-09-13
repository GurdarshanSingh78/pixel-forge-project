from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.models.job import create_db_and_tables
from app.routes import images
from app.core.paths import TEMPLATES_DIR, DOWNLOADS_DIR, DATABASE_FILE
from app.services.email_scheduler import check_and_send_notifications

app = FastAPI()

# --- THIS IS THE FIX ---
# We ensure that the necessary directories exist before the app tries to use them.
@app.on_event("startup")
def on_startup():
    print("INFO:     Starting up...")
    # Create the downloads directory if it doesn't exist
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    # Ensure the parent directory for the database exists
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Create the database tables
    create_db_and_tables()
    
    # Start the email scheduler
    scheduler.add_job(check_and_send_notifications, "interval", seconds=30, id="email_scheduler_job", replace_existing=True)
    scheduler.start()
    print("INFO:     Startup complete.")

# --- The rest of the file is now correct ---
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

scheduler = AsyncIOScheduler()

app.include_router(images.router, prefix="/api")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
    