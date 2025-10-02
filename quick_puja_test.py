#!/usr/bin/env python3
"""
Quick test to verify puja creation works with correct admin credentials.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def quick_test():
    """Quick test of puja creation."""
    print("🚀 Quick Puja Creation Test")
    print("=" * 30)
    
    # Step 1: Login with correct credentials
    print("🔐 Logging in as admin...")
    login_data = {
        "username": "admin@33kotidham.com",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Admin login successful!")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Step 2: Create a simple test puja
    print("\n🕉️  Creating test puja...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    puja_data = {
        "name": "Quick Test Puja",
        "sub_heading": "Testing puja creation API",
        "description": "This is a quick test to verify the puja creation API is working correctly with the admin authentication.",
        "category": "Test",
        "is_prasad_active": True,
        "prasad_price": 108
    }
    
    try:
        response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=puja_data)
        if response.status_code == 200:
            puja = response.json()
            print("✅ Puja created successfully!")
            print(f"   ID: {puja['id']}")
            print(f"   Name: {puja['name']}")
            print(f"   Category: {puja['category']}")
            print(f"   Prasad: ₹{puja['prasad_price']}")
            
            # Step 3: Verify puja can be retrieved
            print("\n📋 Verifying puja retrieval...")
            try:
                response = requests.get(f"{BASE_URL}/pujas/{puja['id']}")
                if response.status_code == 200:
                    retrieved_puja = response.json()
                    print("✅ Puja retrieved successfully!")
                    print(f"   Retrieved name: {retrieved_puja['name']}")
                else:
                    print(f"❌ Puja retrieval failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Retrieval error: {e}")
            
            # Step 4: List all pujas
            print("\n📝 Listing all pujas...")
            try:
                response = requests.get(f"{BASE_URL}/pujas/")
                if response.status_code == 200:
                    pujas = response.json()
                    print(f"✅ Found {len(pujas)} pujas in database")
                    for p in pujas[-3:]:  # Show last 3 pujas
                        print(f"   - {p['name']} (ID: {p['id']})")
                else:
                    print(f"❌ Puja listing failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Listing error: {e}")
                
        else:
            print(f"❌ Puja creation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            
    except Exception as e:
        print(f"❌ Puja creation error: {e}")
    
    print(f"\n🎉 Quick test completed!")
    print(f"\n💡 If this worked, you can now run:")
    print(f"   python test_puja_creation.py")

if __name__ == "__main__":
    quick_test()
