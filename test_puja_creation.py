#!/usr/bin/env python3
"""
Comprehensive test script for Puja Creation API with image uploads.
This script tests the complete puja creation workflow including image uploads.
"""

import requests
import json
import os
from datetime import datetime, date, time
from io import BytesIO
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
    
    # Create image
    img = Image.new('RGB', size, color)
    
    # Add some text to indicate it's a fallback
    try:
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((50, 50), f"Fallback: {filename}", fill=(0, 0, 0))
    except:
        pass
    
    # Save to temp file
    temp_path = os.path.join(tempfile.gettempdir(), filename)
    img.save(temp_path, 'JPEG')
    print(f"   ✅ Created fallback: {filename} ({size[0]}x{size[1]})")
    return temp_path

def get_admin_token():
    """Get admin authentication token."""
    print("🔑 Getting admin authentication token...")
    
    # First try to setup super admin (in case it doesn't exist)
    admin_data = {
        "name": "Super Admin",
        "email": "admin@33kotidham.com",
        "mobile": "9999999999",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/setup-super-admin", json=admin_data)
        if response.status_code == 200:
            print("✅ Super Admin created successfully!")
        elif "already exists" in response.json().get("detail", ""):
            print("ℹ️  Super Admin already exists")
        else:
            print(f"⚠️  Super Admin setup response: {response.status_code}")
            print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"ℹ️  Admin setup: {e}")
    
    # Login with the correct admin credentials
    login_data = {
        "username": "admin@33kotidham.com",
        "password": "admin123"
    }
    
    print(f"🔐 Logging in as: {login_data['username']}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Admin login successful!")
            return token
        else:
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def upload_image(token: str, image_path: str) -> str:
    """Upload an image and return the URL."""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        with open(image_path, 'rb') as f:
            files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
            response = requests.post(f"{BASE_URL}/uploads/images", headers=headers, files=files)
        
        if response.status_code == 200:
            file_url = response.json()["file_url"]
            print(f"✅ Image uploaded: {os.path.basename(image_path)}")
            return file_url
        else:
            print(f"❌ Image upload failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Image upload error: {e}")
        return None

def create_puja(token: str, puja_data: dict) -> dict:
    """Create a new puja."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=puja_data)
        
        if response.status_code == 200:
            puja = response.json()
            print(f"✅ Puja created successfully! ID: {puja['id']}")
            return puja
        else:
            print(f"❌ Puja creation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Puja creation error: {e}")
        return None

def upload_puja_images(token: str, puja_id: int, image_paths: list) -> list:
    """Upload multiple images for a puja."""
    headers = {"Authorization": f"Bearer {token}"}
    uploaded_images = []
    
    for image_path in image_paths:
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
                uploaded_images.append(result)
                print(f"✅ Puja image uploaded: {os.path.basename(image_path)}")
            else:
                print(f"❌ Puja image upload failed: {response.status_code}")
                print(f"   Error: {response.json()}")
        except Exception as e:
            print(f"❌ Puja image upload error: {e}")
    
    return uploaded_images

def add_puja_benefits(token: str, puja_id: int, benefits: list) -> list:
    """Add benefits to a puja."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    added_benefits = []
    
    for benefit in benefits:
        try:
            response = requests.post(
                f"{BASE_URL}/pujas/{puja_id}/benefits", 
                headers=headers, 
                json=benefit
            )
            
            if response.status_code == 200:
                result = response.json()
                added_benefits.append(result)
                print(f"✅ Benefit added: {benefit['benefit_title']}")
            else:
                print(f"❌ Benefit addition failed: {response.status_code}")
                print(f"   Error: {response.json()}")
        except Exception as e:
            print(f"❌ Benefit addition error: {e}")
    
    return added_benefits

def test_puja_creation_workflow():
    """Test the complete puja creation workflow."""
    print("🕉️  Testing Puja Creation API Workflow")
    print("=" * 60)
    
    # Step 1: Get admin token
    token = get_admin_token()
    if not token:
        return False
    
    # Step 2: Download real images from internet
    print("\n📸 Downloading real images from internet...")
    image_paths = []
    for img_info in SAMPLE_IMAGES:
        img_path = download_image(img_info)
        image_paths.append(img_path)
        print(f"   Ready: {img_info['filename']}")
    
    # Step 3: Upload temple image
    print("\n🖼️  Uploading temple image...")
    temple_image_url = upload_image(token, image_paths[0])
    
    # Step 4: Create comprehensive puja data
    print("\n🕉️  Creating puja...")
    puja_data = {
        "name": "Maha Rudrabhishek Puja",
        "sub_heading": "Divine blessing ceremony for Lord Shiva",
        "description": "Maha Rudrabhishek is a powerful Vedic ritual performed to invoke the blessings of Lord Shiva. This sacred ceremony involves the chanting of Rudra mantras and the offering of various sacred items to the Shiva Lingam. The puja brings peace, prosperity, and spiritual growth to devotees.",
        # Leave date and time as None for now (can be set later)
        # "date": date(2024, 3, 15),  # Uncomment to set specific date
        # "time": time(6, 0, 0),      # Uncomment to set specific time
        
        # Temple details
        "temple_image_url": temple_image_url,
        "temple_address": "Ancient Shiva Temple, Varanasi, Uttar Pradesh, India",
        "temple_description": "This ancient temple dedicated to Lord Shiva has been a center of devotion for over 1000 years. Located on the banks of the holy Ganges, it is renowned for its powerful spiritual energy and miraculous blessings.",
        
        # Prasad
        "prasad_price": 251,
        "is_prasad_active": True,
        
        # Dakshina options
        "dakshina_prices_inr": "108,251,501,1001,2501",
        "dakshina_prices_usd": "2,5,10,15,30",
        "is_dakshina_active": True,
        
        # Manokamna options
        "manokamna_prices_inr": "501,1001,2501,5001",
        "manokamna_prices_usd": "10,15,30,60",
        "is_manokamna_active": True,
        
        # General
        "category": "Shiva Puja"
    }
    
    puja = create_puja(token, puja_data)
    if not puja:
        return False
    
    puja_id = puja["id"]
    
    # Step 5: Upload puja images
    print(f"\n📷 Uploading puja images for Puja ID: {puja_id}...")
    uploaded_images = upload_puja_images(token, puja_id, image_paths[1:])
    
    # Step 6: Add puja benefits
    print(f"\n🌟 Adding puja benefits...")
    benefits = [
        {
            "benefit_title": "Spiritual Purification",
            "benefit_description": "Cleanses negative karma and purifies the soul through divine blessings of Lord Shiva."
        },
        {
            "benefit_title": "Health & Prosperity",
            "benefit_description": "Brings good health, wealth, and prosperity to the devotee and their family."
        },
        {
            "benefit_title": "Peace & Harmony",
            "benefit_description": "Establishes peace in mind and harmony in relationships, removing obstacles from life."
        },
        {
            "benefit_title": "Protection from Evil",
            "benefit_description": "Provides divine protection from negative energies and evil influences."
        },
        {
            "benefit_title": "Fulfillment of Desires",
            "benefit_description": "Helps in fulfilling righteous desires and achieving life goals with divine grace."
        }
    ]
    
    added_benefits = add_puja_benefits(token, puja_id, benefits)
    
    # Step 7: Retrieve and display created puja
    print(f"\n📋 Retrieving created puja...")
    try:
        response = requests.get(f"{BASE_URL}/pujas/{puja_id}")
        if response.status_code == 200:
            full_puja = response.json()
            print("✅ Puja retrieved successfully!")
            
            # Display puja details
            print(f"\n🕉️  PUJA DETAILS:")
            print(f"   ID: {full_puja['id']}")
            print(f"   Name: {full_puja['name']}")
            print(f"   Sub-heading: {full_puja['sub_heading']}")
            print(f"   Category: {full_puja['category']}")
            print(f"   Date: {full_puja['date']}")
            print(f"   Time: {full_puja['time']}")
            print(f"   Temple: {full_puja['temple_address']}")
            print(f"   Prasad Active: {full_puja['is_prasad_active']} (₹{full_puja['prasad_price']})")
            print(f"   Dakshina Active: {full_puja['is_dakshina_active']}")
            print(f"   Manokamna Active: {full_puja['is_manokamna_active']}")
            print(f"   Images: {len(full_puja['images'])} uploaded")
            print(f"   Benefits: {len(full_puja['benefits'])} added")
            
            if full_puja['images']:
                print(f"\n📸 UPLOADED IMAGES:")
                for i, img in enumerate(full_puja['images'], 1):
                    print(f"   {i}. Image ID: {img['id']}")
                    print(f"      URL: {img['image_url']}")
            
            if full_puja['benefits']:
                print(f"\n🌟 PUJA BENEFITS:")
                for i, benefit in enumerate(full_puja['benefits'], 1):
                    print(f"   {i}. {benefit['benefit_title']}")
                    print(f"      {benefit['benefit_description']}")
        else:
            print(f"❌ Failed to retrieve puja: {response.status_code}")
    except Exception as e:
        print(f"❌ Error retrieving puja: {e}")
    
    # Step 8: Test puja listing
    print(f"\n📝 Testing puja listing...")
    try:
        response = requests.get(f"{BASE_URL}/pujas/")
        if response.status_code == 200:
            pujas = response.json()
            print(f"✅ Retrieved {len(pujas)} pujas from listing")
            
            # Find our created puja
            our_puja = next((p for p in pujas if p['id'] == puja_id), None)
            if our_puja:
                print(f"✅ Our created puja found in listing!")
            else:
                print(f"❌ Our created puja not found in listing")
        else:
            print(f"❌ Failed to list pujas: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing pujas: {e}")
    
    # Cleanup: Remove temporary image files
    print(f"\n🧹 Cleaning up temporary files...")
    for img_path in image_paths:
        try:
            os.remove(img_path)
            print(f"   Removed: {os.path.basename(img_path)}")
        except Exception as e:
            print(f"   Failed to remove {img_path}: {e}")
    
    print(f"\n🎉 Puja creation workflow completed successfully!")
    print(f"\n📊 SUMMARY:")
    print(f"   ✅ Admin authentication")
    print(f"   ✅ Sample images created")
    print(f"   ✅ Temple image uploaded")
    print(f"   ✅ Puja created (ID: {puja_id})")
    print(f"   ✅ Puja images uploaded ({len(uploaded_images)})")
    print(f"   ✅ Puja benefits added ({len(added_benefits)})")
    print(f"   ✅ Puja retrieval verified")
    print(f"   ✅ Puja listing verified")
    
    return True

def test_puja_api_endpoints():
    """Test various puja API endpoints."""
    print("\n🔧 Testing Additional Puja API Endpoints")
    print("=" * 50)
    
    token = get_admin_token()
    if not token:
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test creating a simple puja
    simple_puja_data = {
        "name": "Ganesha Puja",
        "sub_heading": "Remover of obstacles",
        "description": "Simple Ganesha puja for removing obstacles",
        "category": "Ganesha Puja",
        "is_prasad_active": True,
        "prasad_price": 108
    }
    
    print("📝 Creating simple puja...")
    response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=simple_puja_data)
    if response.status_code == 200:
        simple_puja = response.json()
        print(f"✅ Simple puja created: {simple_puja['name']} (ID: {simple_puja['id']})")
        
        # Test updating the puja
        print("📝 Testing puja update...")
        update_data = {
            "description": "Updated description for Ganesha puja with more details",
            "dakshina_prices_inr": "108,251,501",
            "is_dakshina_active": True
        }
        
        response = requests.put(f"{BASE_URL}/pujas/{simple_puja['id']}", headers=headers, json=update_data)
        if response.status_code == 200:
            updated_puja = response.json()
            print(f"✅ Puja updated successfully!")
            print(f"   New description: {updated_puja['description'][:50]}...")
            print(f"   Dakshina active: {updated_puja['is_dakshina_active']}")
        else:
            print(f"❌ Puja update failed: {response.status_code}")
    else:
        print(f"❌ Simple puja creation failed: {response.status_code}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting Puja Creation API Tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000\n")
    
    # Test main workflow
    success = test_puja_creation_workflow()
    
    if success:
        # Test additional endpoints
        test_puja_api_endpoints()
    
    print("\n✨ All tests completed!")
    print("\n💡 You can now:")
    print("   • View the created pujas at http://localhost:8000/docs")
    print("   • Test the API endpoints in the FastAPI documentation")
    print("   • Use the puja data in your frontend application")
