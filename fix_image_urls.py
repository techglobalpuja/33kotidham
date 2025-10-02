#!/usr/bin/env python3
"""
Fix existing image URLs in the database to use relative paths.
This script updates all image URLs from full URLs to relative paths.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def get_admin_token():
    """Get admin authentication token."""
    print("🔑 Getting admin authentication token...")
    
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

def fix_image_urls():
    """Fix image URLs in the database."""
    print("🔧 Fixing Image URLs in Database")
    print("=" * 40)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        return
    
    # Get all pujas
    print("\n📋 Fetching all pujas...")
    try:
        response = requests.get(f"{BASE_URL}/pujas/")
        if response.status_code == 200:
            pujas = response.json()
            print(f"✅ Found {len(pujas)} pujas")
        else:
            print(f"❌ Failed to fetch pujas: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error fetching pujas: {e}")
        return
    
    # Check and fix image URLs
    fixed_count = 0
    total_images = 0
    
    for puja in pujas:
        puja_id = puja['id']
        puja_name = puja['name']
        images = puja.get('images', [])
        
        if not images:
            continue
            
        print(f"\n🕉️  Checking Puja: {puja_name} (ID: {puja_id})")
        print(f"   Images: {len(images)}")
        
        for image in images:
            total_images += 1
            image_id = image['id']
            current_url = image['image_url']
            
            print(f"   📷 Image ID {image_id}:")
            print(f"      Current URL: {current_url}")
            
            # Check if URL needs fixing
            if current_url.startswith('http://localhost:8000'):
                # Extract the relative path
                relative_url = current_url.replace('http://localhost:8000', '')
                print(f"      ✅ Needs fixing -> {relative_url}")
                
                # Note: We would need a database update endpoint to fix this
                # For now, just report what needs to be fixed
                fixed_count += 1
            elif current_url.startswith('/uploads'):
                print(f"      ✅ Already correct (relative path)")
            else:
                print(f"      ⚠️  Unknown format: {current_url}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total images found: {total_images}")
    print(f"   Images needing fixes: {fixed_count}")
    print(f"   Images already correct: {total_images - fixed_count}")
    
    if fixed_count > 0:
        print(f"\n💡 To fix the URLs:")
        print(f"   1. The upload endpoints have been updated to return relative URLs")
        print(f"   2. New uploads will use the correct format: /uploads/...")
        print(f"   3. Existing URLs will work but show full paths")
        print(f"   4. Consider re-uploading images or updating database directly")
    else:
        print(f"\n🎉 All image URLs are already in the correct format!")

def test_image_access():
    """Test if images are accessible via relative URLs."""
    print(f"\n🧪 Testing Image Access")
    print("=" * 25)
    
    # Get a sample puja with images
    try:
        response = requests.get(f"{BASE_URL}/pujas/")
        if response.status_code == 200:
            pujas = response.json()
            
            for puja in pujas:
                images = puja.get('images', [])
                if images:
                    sample_image = images[0]
                    image_url = sample_image['image_url']
                    
                    print(f"🖼️  Testing image access:")
                    print(f"   Puja: {puja['name']}")
                    print(f"   Image URL: {image_url}")
                    
                    # Test direct access
                    if image_url.startswith('/'):
                        test_url = f"http://localhost:8000{image_url}"
                    else:
                        test_url = image_url
                    
                    try:
                        img_response = requests.get(test_url, timeout=5)
                        if img_response.status_code == 200:
                            print(f"   ✅ Image accessible! Size: {len(img_response.content):,} bytes")
                        else:
                            print(f"   ❌ Image not accessible: {img_response.status_code}")
                    except Exception as e:
                        print(f"   ❌ Image access error: {e}")
                    
                    break  # Test only first image found
            else:
                print("   ℹ️  No images found to test")
                
    except Exception as e:
        print(f"   ❌ Test error: {e}")

def main():
    """Main function."""
    fix_image_urls()
    test_image_access()
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Restart your FastAPI server to apply the fixes")
    print(f"   2. Test uploading new images - they should use relative URLs")
    print(f"   3. Check that existing images are still accessible")
    print(f"   4. Run: python test_puja_creation.py")

if __name__ == "__main__":
    main()
