from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.routes import images
from app.core.paths import TEMPLATES_DIR, DOWNLOADS_DIR
# --- FIX: Import the new job scheduler function ---
from app.services.job_scheduler import check_for_jobs

app = FastAPI()

# Mount static and download directories
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

scheduler = AsyncIOScheduler()

@app.on_event("startup")
def on_startup():
    # The startup logic is now very clean.
    print("INFO:     Starting background job scheduler...")
    scheduler.add_job(check_for_jobs, "interval", seconds=30, id="main_job_worker", replace_existing=True)
    scheduler.start()
    print("INFO:     Startup complete.")

# Include API routes
app.include_router(images.router, prefix="/api")

# Serve the main page
templates = Jinja2Templates(directory=TEMPLATES_DIR)
@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

