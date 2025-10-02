import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles
from app.config import settings


async def save_upload_file(upload_file: UploadFile, directory: str = "images") -> str:
    """Save uploaded file and return the file path."""
    
    # Validate file size
    if upload_file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large")
    
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if upload_file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Generate unique filename
    file_extension = upload_file.filename.split(".")[-1].lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Create directory if it doesn't exist
    upload_dir = os.path.join(settings.UPLOAD_DIR, directory)
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        content = await upload_file.read()
        await f.write(content)
    
    # Optimize image if it's an image file
    if upload_file.content_type.startswith("image/"):
        optimize_image(file_path)
    
    # Return relative path for URL generation
    return f"/{directory}/{unique_filename}"


def optimize_image(file_path: str, max_width: int = 1200, quality: int = 85):
    """Optimize image file size and dimensions."""
    try:
        with Image.open(file_path) as img:
            # Convert to RGB if necessary
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            img.save(file_path, optimize=True, quality=quality)
    except Exception as e:
        # If optimization fails, keep original file
        print(f"Image optimization failed: {e}")


def delete_file(file_path: str) -> bool:
    """Delete a file from the filesystem."""
    try:
        full_path = os.path.join(settings.UPLOAD_DIR, file_path.lstrip("/"))
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False
    except Exception:
        return False


def generate_file_url(file_path: str, base_url: str = "") -> str:
    """Generate full URL for a file."""
    if not file_path:
        return ""
    
    if file_path.startswith("http"):
        return file_path
    
    return f"{base_url}/uploads{file_path}"


class FileManager:
    """File management utility class."""
    
    @staticmethod
    async def upload_image(upload_file: UploadFile, directory: str = "images") -> str:
        """Upload and save an image file."""
        return await save_upload_file(upload_file, directory)
    
    @staticmethod
    def delete_image(file_path: str) -> bool:
        """Delete an image file."""
        return delete_file(file_path)
    
    @staticmethod
    def get_file_url(file_path: str, request_url: str = "") -> str:
        """Get full URL for a file."""
        return generate_file_url(file_path, request_url)
