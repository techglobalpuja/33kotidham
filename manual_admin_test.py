#!/usr/bin/env python3
"""
Manual admin test - run this to debug the authentication issue step by step.
"""

import requests
import json

def test_step_by_step():
    """Test admin authentication step by step."""
    print("🔍 Manual Admin Authentication Test")
    print("=" * 40)
    
    BASE_URL = "http://localhost:8000/api/v1"
    
    # Step 1: Test server
    print("\n1️⃣ Testing server connection...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Server is running")
        else:
            print("   ❌ Server issue")
            return
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    # Step 2: Create super admin
    print("\n2️⃣ Creating super admin...")
    admin_data = {
        "name": "Test Super Admin",
        "email": "test@33kotidham.com",
        "mobile": "8888888888",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/setup-super-admin", json=admin_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            print("   ✅ Super admin created successfully")
        elif "already exists" in str(response.json()):
            print("   ℹ️  Super admin already exists, continuing...")
        else:
            print("   ❌ Failed to create super admin")
            return
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # Step 3: Test admin login
    print("\n3️⃣ Testing admin login...")
    login_data = {
        "username": "8888888888",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("   ✅ Admin login successful!")
            print(f"   Token: {token[:50]}...")
            
            # Step 4: Test token usage
            print("\n4️⃣ Testing token usage...")
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"   ✅ Token works! User: {user_info['name']} ({user_info['role']})")
                else:
                    print(f"   ❌ Token validation failed: {response.json()}")
            except Exception as e:
                print(f"   ❌ Token test error: {e}")
                
        else:
            print("   ❌ Admin login failed")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
    
    # Step 5: Alternative login attempts
    print("\n5️⃣ Trying alternative login methods...")
    
    # Try with email
    login_email = {
        "username": "test@33kotidham.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_email)
        print(f"   Email login status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Email login works!")
        else:
            print(f"   ❌ Email login failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Email login error: {e}")
    
    # Try regular login endpoint
    regular_login = {
        "mobile": "8888888888",
        "password": "test123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=regular_login)
        print(f"   Regular login status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Regular login works!")
        else:
            print(f"   ❌ Regular login failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Regular login error: {e}")
    
    print("\n📋 Test completed!")
    print("\nNext steps:")
    print("1. If super admin creation worked but login failed:")
    print("   - Check password hashing in the database")
    print("   - Verify bcrypt is working correctly")
    print("2. If both failed:")
    print("   - Check server logs for detailed errors")
    print("   - Verify database connectivity")
    print("3. Try accessing http://localhost:8000/docs manually")

if __name__ == "__main__":
    test_step_by_step()
