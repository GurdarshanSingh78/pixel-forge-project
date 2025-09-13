from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# --- FIX: Import the scheduler from the correct library ---
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.models.job import create_db_and_tables
from app.routes import images
from app.core.paths import TEMPLATES_DIR, DOWNLOADS_DIR, DATABASE_FILE
from app.services.email_scheduler import check_and_send_notifications

app = FastAPI()

# --- FIX: Ensure data directories exist on startup ---
@app.on_event("startup")
def on_startup():
    print("INFO:     Server starting up...")
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    create_db_and_tables()
    
    scheduler.add_job(check_and_send_notifications, "interval", seconds=30, id="email_scheduler_job", replace_existing=True)
    scheduler.start()
    print("INFO:     Startup complete.")

# Mount static and download directories
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

scheduler = AsyncIOScheduler()

# Include API routes
app.include_router(images.router, prefix="/api")

# Serve the main page
templates = Jinja2Templates(directory=TEMPLATES_DIR)
@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})