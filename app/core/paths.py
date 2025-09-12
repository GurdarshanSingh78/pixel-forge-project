from pathlib import Path
import os
 
DATA_ROOT = Path(os.environ.get("RENDER_DISK_PATH", Path(__file__).parent.parent.parent))

    # All data paths are now relative to this configurable root
TEMPLATES_DIR = Path(__file__).parent.parent / "app" / "templates"
DOWNLOADS_DIR = DATA_ROOT / "downloads"
DATABASE_FILE = DATA_ROOT / "jobs.db"
    