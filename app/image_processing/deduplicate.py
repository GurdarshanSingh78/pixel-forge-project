import os
from PIL import Image
import imagehash

def deduplicate_images(image_paths: list[str], job_id: int) -> list[str]:
    """
    Finds and removes duplicate images using perceptual hashing.
    """
    print(f"[JOB {job_id}] 🔎 Starting deduplication process for {len(image_paths)} images...")
    
    seen_hashes = set()
    unique_image_paths = []

    if not image_paths:
        return []

    for image_path in image_paths:
        try:
            with Image.open(image_path) as img:
                hash_value = imagehash.phash(img)
            
            if hash_value in seen_hashes:
                continue
            
            seen_hashes.add(hash_value)
            unique_image_paths.append(image_path)

        except Exception as e:
            print(f"[JOB {job_id}] ⚠️ WARNING: Could not process file {os.path.basename(image_path)}. Error: {e}. Skipping.")
            continue
    
    num_duplicates = len(image_paths) - len(unique_image_paths)
    print(f"[JOB {job_id}] ✨ Deduplication complete. Removed {num_duplicates} duplicates, {len(unique_image_paths)} unique images remain.")
    
    return unique_image_paths

