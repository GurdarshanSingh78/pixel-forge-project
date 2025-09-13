from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.models.job import create_db_and_tables
from app.routes import images
from app.core.paths import TEMPLATES_DIR, DOWNLOADS_DIR, DATABASE_FILE
from app.services.email_scheduler import check_and_send_notifications

app = FastAPI()

# Define scheduler BEFORE using it
scheduler = AsyncIOScheduler()

# --- Ensure directories & services are ready at startup ---
@app.on_event("startup")
def on_startup():
    print("INFO:     Starting up...")

    # Ensure downloads folder exists
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure database parent directory exists
    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Create database tables
    create_db_and_tables()

    # Start background scheduler
    scheduler.add_job(
        check_and_send_notifications,
        "interval",
        seconds=30,
        id="email_scheduler_job",
        replace_existing=True,
    )
    scheduler.start()

    print("INFO:     Startup complete.")

# --- Mount static and downloads ---
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- Routes ---
app.include_router(images.router, prefix="/api")

templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
