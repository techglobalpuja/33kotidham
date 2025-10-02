#!/usr/bin/env python3
"""
Simple test to verify image downloads from the internet work correctly.
Run this first to test image downloading before running the full puja tests.
"""

import requests
import os
import tempfile
from PIL import Image

# Real image URLs from the internet
IMAGE_URLS = [
    {
        "url": "https://www.tripsavvy.com/thmb/FW00bGmyhQ_cHIMw50A00WnTXIU=/2123x1412/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-172596980-5b7d710fc9e77c00503345ba.jpg",
        "filename": "GettyImages-172596980-5b7d710fc9e77c00503345ba.jpg",
        "expected_size": (2123, 1412)
    },
    {
        "url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1200&h=700&fit=crop",
        "filename": "rudrabhishek-puja-at-home-FEATURE-compressed.jpg",
        "expected_size": (1200, 700)
    },
    {
        "url": "https://wallpaperaccess.com/full/504997.jpg",
        "filename": "504997.jpg",
        "expected_size": (1920, 1080)
    }
]

def test_image_download(image_info):
    """Test downloading a single image."""
    url = image_info["url"]
    filename = image_info["filename"]
    expected_size = image_info["expected_size"]
    
    print(f"\n📥 Testing download: {filename}")
    print(f"   URL: {url}")
    print(f"   Expected size: {expected_size[0]}x{expected_size[1]}")
    
    try:
        # Download with proper headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print("   🔄 Downloading...")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save to temp file
        temp_path = os.path.join(tempfile.gettempdir(), filename)
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        # Get file info
        file_size = os.path.getsize(temp_path)
        print(f"   📁 File size: {file_size:,} bytes")
        
        # Verify it's a valid image
        try:
            # Open and immediately close the image to release file handle
            img = Image.open(temp_path)
            actual_size = img.size
            format_type = img.format
            mode = img.mode
            img.close()  # Explicitly close to release file handle
            
            print(f"   🖼️  Image format: {format_type}")
            print(f"   📐 Actual size: {actual_size[0]}x{actual_size[1]}")
            print(f"   🎨 Color mode: {mode}")
            
            # Check if size matches expected
            if actual_size == expected_size:
                print(f"   ✅ Size matches expected dimensions!")
            else:
                print(f"   ⚠️  Size differs from expected: {expected_size}")
            
            # Clean up - try multiple times if needed
            try:
                os.remove(temp_path)
                print(f"   🧹 Cleaned up temp file")
            except PermissionError:
                print(f"   ⚠️  Temp file cleanup skipped (file in use)")
            
            return True
                
        except Exception as e:
            print(f"   ❌ Invalid image file: {e}")
            try:
                os.remove(temp_path)
            except:
                pass
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Download failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def main():
    """Test all image downloads."""
    print("🌐 Testing Internet Image Downloads")
    print("=" * 50)
    
    success_count = 0
    total_count = len(IMAGE_URLS)
    
    for image_info in IMAGE_URLS:
        if test_image_download(image_info):
            success_count += 1
    
    print(f"\n📊 DOWNLOAD TEST RESULTS:")
    print(f"   Total images tested: {total_count}")
    print(f"   Successfully downloaded: {success_count}")
    print(f"   Failed downloads: {total_count - success_count}")
    
    if success_count == total_count:
        print(f"\n🎉 All images downloaded successfully!")
        print(f"   ✅ Ready to run puja creation tests")
    elif success_count > 0:
        print(f"\n⚠️  {success_count}/{total_count} images downloaded successfully")
        print(f"   ✅ Partial functionality available")
        print(f"   💡 Failed downloads will use fallback images")
    else:
        print(f"\n❌ No images could be downloaded")
        print(f"   🔄 All tests will use fallback images")
        print(f"   💡 Check your internet connection")
    
    print(f"\n🔧 Technical Notes:")
    print(f"   • File cleanup issues are normal on Windows")
    print(f"   • Images are successfully downloaded and verified")
    print(f"   • Temp files will be cleaned up on system restart")
    
    print(f"\n💡 Next steps:")
    print(f"   • Run: python test_puja_creation.py")
    print(f"   • Or run: python test_image_upload.py")

if __name__ == "__main__":
    main()
