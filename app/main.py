from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# --- THIS IS THE FIX ---
# Import the scheduler class from the main 'apscheduler' library
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.models.job import create_db_and_tables
from app.routes import images
from app.core.paths import TEMPLATES_DIR, DOWNLOADS_DIR
from app.services.email_scheduler import check_and_send_notifications

app = FastAPI()

app.mount("/downloads", StaticFiles(directory=DOWNLOADS_DIR), name="downloads")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# We create an instance of the scheduler we just imported
scheduler = AsyncIOScheduler()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # The rest of the code works perfectly with the corrected import
    scheduler.add_job(check_and_send_notifications, "interval", seconds=30, id="email_scheduler_job", replace_existing=True)
    scheduler.start()

app.include_router(images.router, prefix="/api")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
@app.get("/", include_in_schema=False)
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

