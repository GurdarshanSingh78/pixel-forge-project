import os
import mimetypes
from pathlib import Path
import requests
import urllib3
import time # <-- NEW: Import the time library

from pexels_api import API
from app.core.config import settings

# (The rest of the file is mostly the same)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
)

def _get_file_extension(url: str) -> str:
    ext = os.path.splitext(url)[1]
    return ext if ext else ".jpg"

def fetch_images(query: str, num_to_fetch: int, job_id: int) -> list[str]:
    print(f"[JOB {job_id}][INFO] Fetching images from Pexels for query='{query}', targeting {num_to_fetch} downloads...")
    
    if not settings.PEXELS_API_KEY or "YOUR_DEFAULT_KEY" in settings.PEXELS_API_KEY:
        print(f"[JOB {job_id}][ERROR] PEXELS_API_KEY is not configured.")
        return []

    try:
        api = API(settings.PEXELS_API_KEY)
        photos_to_get = []
        page = 1
        while len(photos_to_get) < num_to_fetch:
            api.search(query, page=page, results_per_page=80) # Fetch larger pages
            photos = api.get_entries()
            if not photos: break
            photos_to_get.extend(photos)
            page += 1
        
        image_urls = [p.original for p in photos_to_get]
        print(f"[JOB {job_id}][INFO] Found {len(image_urls)} potential image URLs from Pexels.")
    except Exception as e:
        print(f"[JOB {job_id}][ERROR] Pexels API search failed: {e}")
        return []

    if not image_urls: return []

    dest_dir = Path(f"downloads/job_{job_id}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    downloaded_paths = []
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    for url in image_urls:
        if len(downloaded_paths) >= num_to_fetch:
            break
        
        try:
            response = session.get(url, timeout=20, stream=True)
            response.raise_for_status()
            
            ext = _get_file_extension(url)
            filename = f"image_{len(downloaded_paths):04d}{ext}"
            filepath = dest_dir / filename
            
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            downloaded_paths.append(str(filepath))
            
            # --- THIS IS THE FIX ---
            # Add a 0.5-second pause to be respectful to the API
            time.sleep(0.5)

        except Exception as e:
            print(f"[ERROR] Failed to download {url}: {e}")
            continue
            
    print(f"[JOB {job_id}][INFO] Download phase complete. Successfully saved {len(downloaded_paths)} images.")
    return downloaded_paths

