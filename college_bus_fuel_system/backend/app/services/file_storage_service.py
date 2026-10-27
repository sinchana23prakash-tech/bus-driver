import os
import uuid
import hashlib
from werkzeug.utils import secure_filename
from PIL import Image
import imagehash
from config import Config

def allowed_file(filename: str) -> bool:
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in Config.ALLOWED_EXTENSIONS

def compute_image_hash(filepath: str) -> str:
    """Computes perceptual difference hash (dhash) for duplicate screening."""
    try:
        with Image.open(filepath) as img:
            # Convert to RGB to support RGBA/P
            img_rgb = img.convert('RGB')
            # 64-bit dhash
            return str(imagehash.dhash(img_rgb))
    except Exception:
        # Fallback to sha256 of file bytes if image hashing fails
        try:
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()[:16]
        except Exception:
            return None

def save_uploaded_bill(file_storage) -> dict:
    """
    Saves uploaded bill file safely outside the web root with a cryptographically
    unique UUID filename. Computes perceptual hash for duplicate detection.
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided")

    original_filename = secure_filename(file_storage.filename)
    if not allowed_file(original_filename):
        raise ValueError("Invalid file extension. Allowed: png, jpg, jpeg, webp, pdf")

    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"bill_{uuid.uuid4().hex}.{ext}"
    
    upload_dir = Config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)
    destination_path = os.path.join(upload_dir, unique_filename)

    file_storage.save(destination_path)
    
    # Compute image hash
    bill_hash = compute_image_hash(destination_path)

    return {
        'filename': unique_filename,
        'filepath': destination_path,
        'original_name': original_filename,
        'image_hash': bill_hash
    }
