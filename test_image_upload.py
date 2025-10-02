#!/usr/bin/env python3
"""
Simple test script for image upload functionality.
Tests uploading the specific images you mentioned.
"""

import requests
import os
from PIL import Image
import tempfile

BASE_URL = "http://localhost:8000/api/v1"

# Real image URLs from the internet
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

def download_image(image_info: dict) -> str:
    """Download an image from URL and save to temp file."""
    url = image_info["url"]
    filename = image_info["filename"]
    
    print(f"📥 Downloading: {filename}")
    print(f"   URL: {url}")
    
    try:
        # Download image with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # Get file size and verify it's a valid image
        file_size = os.path.getsize(temp_path)
        
        # Verify it's a valid image by opening it
        try:
            img = Image.open(temp_path)
            width, height = img.size
            img.close()  # Explicitly close to release file handle
            print(f"   ✅ Downloaded: {filename} ({width}x{height}, {file_size} bytes)")
        except Exception as e:
            print(f"   ⚠️  Downloaded but may not be a valid image: {e}")
        
        return temp_path
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Download failed: {e}")
        # Fallback: create a simple colored image
        print(f"   🔄 Creating fallback image...")
        return create_fallback_image(filename)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return create_fallback_image(filename)

def create_fallback_image(filename: str) -> str:
    """Create a fallback image if download fails."""
    # Create a simple colored image as fallback
    colors = {
        "GettyImages": (255, 215, 0),  # Gold
        "rudrabhishek": (255, 140, 0),  # Dark orange
        "504997": (255, 69, 0)  # Red orange
    }
    
    # Determine color and size based on filename
    color = (255, 215, 0)  # Default gold
    size = (800, 600)  # Default size
    
    for key, col in colors.items():
        if key.lower() in filename.lower():
            color = col
            break
    
    if "GettyImages" in filename:
        size = (2123, 1412)
    elif "rudrabhishek" in filename:
        size = (1200, 700)
    elif "504997" in filename:
        size = (1920, 1080)
    
    # Create image with visual elements
    img = Image.new('RGB', size, color)
    
    # Add some visual elements to make it look more realistic
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([50, 50, size[0]-50, size[1]-50], outline=(0, 0, 0), width=5)
        
        # Add text
        draw.text((size[0]//2-100, size[1]//2), f"Fallback: {filename}", fill=(0, 0, 0))
    except:
        pass
    
    # Save to temp file
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    img.save(temp_path, 'JPEG', quality=85)
    
    # Get file size
    file_size = os.path.getsize(temp_path)
    print(f"   ✅ Created fallback: {filename} ({size[0]}x{size[1]}, {file_size} bytes)")
    
    return temp_path

def get_admin_token():
    """Get admin token for authentication."""
    print("🔑 Getting admin token...")
    
    # Setup admin if needed
    admin_data = {
        "name": "Super Admin",
        "email": "admin@33kotidham.com", 
        "mobile": "9999999999",
        "password": "admin123"
    }
    
    try:
        requests.post(f"{BASE_URL}/auth/setup-super-admin", json=admin_data)
    except:
        pass
    
    # Login
    login_data = {
        "username": "admin@33kotidham.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Admin authenticated successfully!")
            return token
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_image_uploads():
    """Test uploading the specified images."""
    print("🖼️  Testing Image Upload API")
    print("=" * 40)
    
    # Get authentication
    token = get_admin_token()
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create and upload each image
    uploaded_files = []
    
    for image_info in SAMPLE_IMAGES:
        print(f"\n📤 Processing: {image_info['filename']}")
        
        # Download real image
        image_path = download_image(image_info)
        
        try:
            # Upload image
            with open(image_path, 'rb') as f:
                files = {"file": (image_info['filename'], f, "image/jpeg")}
                response = requests.post(f"{BASE_URL}/uploads/images", headers=headers, files=files)
            
            if response.status_code == 200:
                result = response.json()
                uploaded_files.append(result)
                print(f"✅ Upload successful!")
                print(f"   Filename: {result['filename']}")
                print(f"   URL: {result['file_url']}")
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.json()}")
        
        except Exception as e:
            print(f"❌ Upload error: {e}")
        
        finally:
            # Clean up temp file
            try:
                os.remove(image_path)
            except:
                pass
    
    # Summary
    print(f"\n📊 UPLOAD SUMMARY:")
    print(f"   Total images processed: {len(SAMPLE_IMAGES)}")
    print(f"   Successfully uploaded: {len(uploaded_files)}")
    
    if uploaded_files:
        print(f"\n📋 UPLOADED FILES:")
        for i, file_info in enumerate(uploaded_files, 1):
            print(f"   {i}. {file_info['filename']}")
            print(f"      URL: {file_info['file_url']}")
    
    return len(uploaded_files) > 0

def test_puja_image_upload():
    """Test uploading images directly to a puja."""
    print(f"\n🕉️  Testing Puja-Specific Image Upload")
    print("=" * 45)
    
    token = get_admin_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First create a test puja
    puja_data = {
        "name": "Test Puja for Images",
        "sub_heading": "Testing image upload functionality",
        "description": "This puja is created specifically to test image upload functionality",
        "category": "Test"
    }
    
    print("📝 Creating test puja...")
    response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=puja_data)
    
    if response.status_code != 200:
        print(f"❌ Failed to create test puja: {response.status_code}")
        return False
    
    puja = response.json()
    puja_id = puja["id"]
    print(f"✅ Test puja created with ID: {puja_id}")
    
    # Upload images to this puja
    headers_upload = {"Authorization": f"Bearer {token}"}
    
    for image_info in SAMPLE_IMAGES[:2]:  # Upload first 2 images
        print(f"\n📤 Uploading to puja: {image_info['filename']}")
        
        # Download real image
        image_path = download_image(image_info)
        
        try:
            with open(image_path, 'rb') as f:
                files = {"file": (image_info['filename'], f, "image/jpeg")}
                response = requests.post(
                    f"{BASE_URL}/uploads/puja-images/{puja_id}", 
                    headers=headers_upload, 
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Puja image uploaded!")
                print(f"   Image ID: {result['image_id']}")
                print(f"   URL: {result['file_url']}")
            else:
                print(f"❌ Puja image upload failed: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            try:
                os.remove(image_path)
            except:
                pass
    
    # Verify images were attached to puja
    print(f"\n🔍 Verifying puja images...")
    try:
        response = requests.get(f"{BASE_URL}/pujas/{puja_id}")
        if response.status_code == 200:
            puja_with_images = response.json()
            images = puja_with_images.get('images', [])
            print(f"✅ Puja now has {len(images)} images attached")
            
            for i, img in enumerate(images, 1):
                print(f"   {i}. Image ID: {img['id']}, URL: {img['image_url']}")
        else:
            print(f"❌ Failed to retrieve puja: {response.status_code}")
    except Exception as e:
        print(f"❌ Error retrieving puja: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Image Upload Tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000\n")
    
    # Test general image upload
    success1 = test_image_uploads()
    
    if success1:
        # Test puja-specific image upload
        success2 = test_puja_image_upload()
    
    print("\n✨ Image upload tests completed!")
    print("\n💡 Next steps:")
    print("   • Check the uploaded images in your uploads directory")
    print("   • View the API documentation at http://localhost:8000/docs")
    print("   • Test the puja creation with real images")
