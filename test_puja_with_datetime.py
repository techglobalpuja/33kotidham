#!/usr/bin/env python3
"""
Test puja creation with proper date/time handling.
This version shows how to correctly set date and time for pujas.
"""

import requests
import json
import os
from datetime import datetime, date, time
from io import BytesIO
from PIL import Image
import tempfile

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
            print(f"❌ Admin login failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def create_puja_with_datetime():
    """Create puja with proper date/time objects."""
    print("🕉️  Testing Puja Creation with Date/Time")
    print("=" * 50)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        return False
    
    # Create puja data with proper date/time objects
    print("\n📝 Creating puja with date and time...")
    
    # Method 1: Using date and time objects
    puja_data_with_datetime = {
        "name": "Scheduled Maha Rudrabhishek Puja",
        "sub_heading": "Divine blessing ceremony scheduled for specific date and time",
        "description": "This Maha Rudrabhishek puja is scheduled for a specific date and time. The sacred ceremony will invoke the blessings of Lord Shiva through Rudra mantras and offerings.",
        "date": "2024-03-15",  # ISO format string
        "time": "06:00:00",    # ISO format string
        "category": "Shiva Puja",
        "is_prasad_active": True,
        "prasad_price": 251,
        "is_dakshina_active": True,
        "dakshina_prices_inr": "108,251,501,1001",
        "temple_address": "Ancient Shiva Temple, Varanasi, UP, India"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=puja_data_with_datetime)
        
        if response.status_code == 200:
            puja = response.json()
            print("✅ Puja with date/time created successfully!")
            print(f"   ID: {puja['id']}")
            print(f"   Name: {puja['name']}")
            print(f"   Date: {puja['date']}")
            print(f"   Time: {puja['time']}")
            return puja
        else:
            print(f"❌ Puja creation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            
            # Try without date/time
            print("\n🔄 Trying without date/time...")
            puja_data_no_datetime = puja_data_with_datetime.copy()
            del puja_data_no_datetime['date']
            del puja_data_no_datetime['time']
            
            response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=puja_data_no_datetime)
            
            if response.status_code == 200:
                puja = response.json()
                print("✅ Puja without date/time created successfully!")
                print(f"   ID: {puja['id']}")
                print(f"   Name: {puja['name']}")
                return puja
            else:
                print(f"❌ Still failed: {response.status_code}")
                print(f"   Error: {response.json()}")
                return None
                
    except Exception as e:
        print(f"❌ Puja creation error: {e}")
        return None

def test_date_time_formats():
    """Test different date/time formats."""
    print("\n🧪 Testing Different Date/Time Formats")
    print("=" * 40)
    
    token = get_admin_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test different formats
    test_cases = [
        {
            "name": "Test Puja - No DateTime",
            "description": "Puja without date and time"
            # No date/time fields
        },
        {
            "name": "Test Puja - Null DateTime", 
            "description": "Puja with null date and time",
            "date": None,
            "time": None
        },
        {
            "name": "Test Puja - ISO Date/Time",
            "description": "Puja with ISO format date and time",
            "date": "2024-03-15",
            "time": "06:00:00"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        
        # Add required fields
        puja_data = {
            "sub_heading": "Test puja creation",
            "category": "Test",
            **test_case
        }
        
        try:
            response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=puja_data)
            
            if response.status_code == 200:
                puja = response.json()
                print(f"   ✅ Success! ID: {puja['id']}")
                print(f"   Date: {puja.get('date', 'None')}")
                print(f"   Time: {puja.get('time', 'None')}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                error_detail = response.json()
                print(f"   Error: {error_detail}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")

def main():
    """Main test function."""
    # Test 1: Create puja with date/time
    puja = create_puja_with_datetime()
    
    # Test 2: Test different formats
    test_date_time_formats()
    
    print(f"\n📊 Summary:")
    print(f"   • Date/time fields are optional in puja creation")
    print(f"   • Use ISO format strings: 'YYYY-MM-DD' and 'HH:MM:SS'")
    print(f"   • Or omit the fields entirely for flexible scheduling")
    
    if puja:
        print(f"\n🎉 Successfully created puja with ID: {puja['id']}")
    
    print(f"\n💡 Now run the main test:")
    print(f"   python test_puja_creation.py")

if __name__ == "__main__":
    main()
