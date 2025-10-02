#!/usr/bin/env python3
"""
Add images to the existing test puja (ID: 1).
"""

import requests
import os
import tempfile
from PIL import Image

BASE_URL = "http://localhost:8000/api/v1"
PUJA_ID = 1  # The existing test puja

# Real image URLs
SAMPLE_IMAGES = [
    {
        "url": "https://www.tripsavvy.com/thmb/FW00bGmyhQ_cHIMw50A00WnTXIU=/2123x1412/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-172596980-5b7d710fc9e77c00503345ba.jpg",
        "filename": "GettyImages-172596980-5b7d710fc9e77c00503345ba.jpg"
    },
    {
        "url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1200&h=700&fit=crop",
        "filename": "rudrabhishek-puja-at-home-FEATURE-compressed.jpg"
    },
    {
        "url": "https://wallpaperaccess.com/full/504997.jpg",
        "filename": "504997.jpg"
    }
]

def download_image(image_info):
    """Download an image from URL."""
    url = image_info["url"]
    filename = image_info["filename"]
    
    print(f"📥 Downloading: {filename}")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # Verify image
        img = Image.open(temp_path)
        width, height = img.size
        img.close()
        
        file_size = os.path.getsize(temp_path)
        print(f"   ✅ Downloaded: {width}x{height}, {file_size:,} bytes")
        
        return temp_path
        
    except Exception as e:
        print(f"   ❌ Download failed: {e}")
        return None

def get_admin_token():
    """Get admin token."""
    print("🔐 Getting admin token...")
    
    login_data = {
        "username": "admin@33kotidham.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Admin login successful!")
            return token
        else:
            print(f"❌ Login failed: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def upload_puja_image(token, puja_id, image_path):
    """Upload image to specific puja."""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(image_path, 'rb') as f:
            files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
            response = requests.post(
                f"{BASE_URL}/uploads/puja-images/{puja_id}", 
                headers=headers, 
                files=files
            )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image uploaded to puja!")
            print(f"   Image ID: {result['image_id']}")
            print(f"   URL: {result['file_url']}")
            return result
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def main():
    """Add images to existing puja."""
    print("🖼️  Adding Images to Existing Puja")
    print("=" * 40)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        return
    
    # Check if puja exists
    print(f"\n🔍 Checking puja ID {PUJA_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/pujas/{PUJA_ID}")
        if response.status_code == 200:
            puja = response.json()
            print(f"✅ Found puja: {puja['name']}")
            print(f"   Current images: {len(puja['images'])}")
        else:
            print(f"❌ Puja not found: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error checking puja: {e}")
        return
    
    # Download and upload images
    print(f"\n📸 Processing images...")
    uploaded_count = 0
    
    for i, image_info in enumerate(SAMPLE_IMAGES, 1):
        print(f"\n🖼️  Image {i}/{len(SAMPLE_IMAGES)}: {image_info['filename']}")
        
        # Download image
        image_path = download_image(image_info)
        if not image_path:
            continue
        
        # Upload to puja
        result = upload_puja_image(token, PUJA_ID, image_path)
        if result:
            uploaded_count += 1
        
        # Cleanup
        try:
            os.remove(image_path)
        except:
            pass
    
    # Verify final result
    print(f"\n📋 Final verification...")
    try:
        response = requests.get(f"{BASE_URL}/pujas/{PUJA_ID}")
        if response.status_code == 200:
            updated_puja = response.json()
            print(f"✅ Puja now has {len(updated_puja['images'])} images!")
            
            for i, img in enumerate(updated_puja['images'], 1):
                print(f"   {i}. Image ID: {img['id']}")
                print(f"      URL: {img['image_url']}")
        else:
            print(f"❌ Verification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Verification error: {e}")
    
    print(f"\n🎉 Process completed!")
    print(f"   Images uploaded: {uploaded_count}/{len(SAMPLE_IMAGES)}")
    print(f"\n💡 Now try the GET request again:")
    print(f"   curl -X 'GET' 'http://127.0.0.1:8000/api/v1/pujas/{PUJA_ID}' -H 'accept: application/json'")

if __name__ == "__main__":
    main()
