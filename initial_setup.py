# This script's only job is to create the database and tables.

from app.models.job import create_db_and_tables
from app.core.paths import DOWNLOADS_DIR, DATABASE_FILE

print("--- Running Initial Setup ---")

# 1. Ensure data directories exist
print("Ensuring data directories exist...")
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)
print("Data directories are ready.")

# 2. Create database tables
print("Creating database tables if they don't exist...")
create_db_and_tables()
print("Database tables are ready.")

print("--- Initial Setup Complete ---")