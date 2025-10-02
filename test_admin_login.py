#!/usr/bin/env python3
"""
Simple test script to verify admin login functionality.
Run this after starting the FastAPI server.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_admin_setup_and_login():
    """Test admin setup and login functionality."""
    
    print("🧪 Testing Admin Login Functionality")
    print("=" * 50)
    
    # Test data
    admin_data = {
        "name": "Super Admin",
        "email": "admin@33kotidham.com",
        "mobile": "9999999999",
        "password": "admin123",
        "role": "super_admin"
    }
    
    # Step 1: Setup Super Admin
    print("1️⃣ Setting up Super Admin...")
    try:
        response = requests.post(f"{BASE_URL}/setup-super-admin", json=admin_data)
        if response.status_code == 200:
            print("✅ Super Admin created successfully!")
            admin_user = response.json()
            print(f"   ID: {admin_user['id']}")
            print(f"   Name: {admin_user['name']}")
            print(f"   Role: {admin_user['role']}")
            print(f"   Mobile: {admin_user['mobile']}")
        elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
            print("ℹ️  Super Admin already exists, skipping creation...")
        else:
            print(f"❌ Failed to create Super Admin: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the FastAPI server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 2: Test Admin Login with Mobile
    print("\n2️⃣ Testing Admin Login with Mobile...")
    login_data = {
        "username": admin_data["mobile"],
        "password": admin_data["password"]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin-login", json=login_data)
        if response.status_code == 200:
            print("✅ Admin login with mobile successful!")
            token_data = response.json()
            print(f"   Token Type: {token_data['token_type']}")
            print(f"   Access Token: {token_data['access_token'][:50]}...")
            mobile_token = token_data['access_token']
        else:
            print(f"❌ Admin login with mobile failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 3: Test Admin Login with Email (if email provided)
    if admin_data["email"]:
        print("\n3️⃣ Testing Admin Login with Email...")
        login_data = {
            "username": admin_data["email"],
            "password": admin_data["password"]
        }
        
        try:
            response = requests.post(f"{BASE_URL}/admin-login", json=login_data)
            if response.status_code == 200:
                print("✅ Admin login with email successful!")
                token_data = response.json()
                print(f"   Token Type: {token_data['token_type']}")
                print(f"   Access Token: {token_data['access_token'][:50]}...")
            else:
                print(f"❌ Admin login with email failed: {response.status_code}")
                print(f"   Error: {response.json()}")
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
    
    # Step 4: Test Invalid Login
    print("\n4️⃣ Testing Invalid Admin Login...")
    invalid_login_data = {
        "username": admin_data["mobile"],
        "password": "wrongpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin-login", json=invalid_login_data)
        if response.status_code == 401:
            print("✅ Invalid login correctly rejected!")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"❌ Invalid login should have been rejected: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Step 5: Test Token Validation
    print("\n5️⃣ Testing Token Validation...")
    headers = {"Authorization": f"Bearer {mobile_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers)
        if response.status_code == 200:
            print("✅ Token validation successful!")
            user_info = response.json()
            print(f"   Logged in as: {user_info['name']} ({user_info['role']})")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            print(f"   Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n🎉 All admin login tests passed successfully!")
    print("\n📋 Summary:")
    print("   ✅ Super Admin setup")
    print("   ✅ Admin login with mobile")
    if admin_data["email"]:
        print("   ✅ Admin login with email")
    print("   ✅ Invalid login rejection")
    print("   ✅ Token validation")
    
    return True

def test_regular_user_admin_access():
    """Test that regular users cannot access admin endpoints."""
    print("\n🔒 Testing Regular User Admin Access Restriction")
    print("=" * 50)
    
    # Try to login as regular user to admin endpoint
    regular_user_data = {
        "username": "1234567890",  # Some regular user mobile
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/admin-login", json=regular_user_data)
        if response.status_code in [401, 403]:
            print("✅ Regular user correctly denied admin access!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.json()['detail']}")
        else:
            print(f"❌ Regular user should not have admin access: {response.status_code}")
    except Exception as e:
        print(f"ℹ️  Expected error (user doesn't exist): {e}")

if __name__ == "__main__":
    print("🚀 Starting Admin Login Tests...")
    print("Make sure the FastAPI server is running on http://localhost:8000\n")
    
    success = test_admin_setup_and_login()
    if success:
        test_regular_user_admin_access()
    
    print("\n✨ Test completed!")
