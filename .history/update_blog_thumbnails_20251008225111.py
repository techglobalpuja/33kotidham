#!/usr/bin/env python3
"""
Script to update existing blogs with thumbnail images
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Blog
import requests
from PIL import Image
import uuid

def download_and_save_thumbnail(url: str, filename: str) -> str:
    """Download thumbnail image from URL and save locally"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            # Create uploads/images directory if not exists
            os.makedirs("uploads/images", exist_ok=True)
            
            file_path = f"uploads/images/{filename}"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            # Optimize image as thumbnail (smaller size)
            with Image.open(file_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Create thumbnail (300x200 for blog cards)
                thumbnail_size = (300, 200)
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                
                # Save optimized thumbnail
                img.save(file_path, optimize=True, quality=85)
            
            return file_path
    except Exception as e:
        print(f"Error downloading thumbnail {url}: {e}")
        return None

def update_blog_thumbnails():
    """Update existing blogs with thumbnail images"""
    print("🖼️ Updating blog thumbnails...")
    
    # Sample thumbnail images for spiritual content
    thumbnail_urls = [
        "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=300&h=200&fit=crop",  # Temple
        "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=300&h=200&fit=crop",  # Prayer
        "https://images.unsplash.com/photo-1509233725247-49e657c54213?w=300&h=200&fit=crop",  # Ganga Aarti
        "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=300&h=200&fit=crop",  # Hindu Temple
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=200&fit=crop",  # Meditation
    ]
    
    db = next(get_db())
    
    try:
        # Get all blogs without thumbnail images
        blogs = db.query(Blog).filter(
            (Blog.thumbnail_image.is_(None)) | (Blog.thumbnail_image == "")
        ).all()
        
        if not blogs:
            print("✅ All blogs already have thumbnail images!")
            return
        
        for i, blog in enumerate(blogs):
            if i < len(thumbnail_urls):
                # Download and save thumbnail
                thumbnail_filename = f"blog-thumb-{blog.id}-{uuid.uuid4()}.jpg"
                thumbnail_path = download_and_save_thumbnail(thumbnail_urls[i], thumbnail_filename)
                
                if thumbnail_path:
                    # Update blog with thumbnail path
                    blog.thumbnail_image = thumbnail_path
                    print(f"✅ Updated thumbnail for: {blog.title}")
                else:
                    print(f"❌ Failed to update thumbnail for: {blog.title}")
        
        db.commit()
        print(f"🎉 Successfully updated thumbnails for {len(blogs)} blogs!")
        
    except Exception as e:
        print(f"❌ Error updating thumbnails: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_blog_thumbnails()