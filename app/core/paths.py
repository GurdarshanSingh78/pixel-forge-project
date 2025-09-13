from pathlib import Path
import os

# Define the absolute path to the project's main source directory (`app`)
# Path(__file__) is this file's path: /app/core/paths.py
# .parent takes us to /app/core
# .parent takes us to /app
APP_DIR = Path(__file__).parent.parent

# The project root is one level above the 'app' directory
PROJECT_ROOT = APP_DIR.parent

# Now, define all other paths relative to these two constants
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# Handle data storage, respecting the Render Disk environment variable if it exists
# This makes it compatible with both free and paid Render plans.
DATA_ROOT = Path(os.environ.get("RENDER_DISK_PATH", PROJECT_ROOT))
DOWNLOADS_DIR = DATA_ROOT / "downloads"
DATABASE_FILE = DATA_ROOT / "jobs.db"