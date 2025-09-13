from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.routes import images
from app.core.paths import TEMPLATES_DIR, DOWNLOADS_DIR
from app.services.email_scheduler import check_and_send_notifications

app = FastAPI()

# Mount static and download directories
app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

scheduler = AsyncIOScheduler()

@app.on_event("startup")
def on_startup():
    # --- FIX: Removed all setup logic from here ---
    print("INFO:     Starting email scheduler...")
    scheduler.add_job(check_and_send_notifications, "interval", seconds=30, id="email_scheduler_job", replace_existing=True)
    scheduler.start()
    print("INFO:     Startup complete.")

# Include API routes
app.include_router(images.router, prefix="/api")

# Serve the main page
templates = Jinja2Templates(directory=TEMPLATES_DIR)
@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})