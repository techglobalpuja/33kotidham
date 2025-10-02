#!/usr/bin/env python3
"""
Debug script to diagnose authentication issues.
This will help identify what's wrong with the admin login.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_server_connection():
    """Test if server is responding."""
    print("🌐 Testing server connection...")
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✅ Server is running and responding")
            result = response.json()
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Version: {result.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ Server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False

def test_auth_endpoints():
    """Test if auth endpoints are accessible."""
    print("\n🔗 Testing auth endpoints...")
    
    endpoints = [
        "/auth/setup-super-admin",
        "/auth/admin-login", 
        "/auth/login",
        "/auth/request-otp"
    ]
    
    for endpoint in endpoints:
        try:
            # Test with empty POST to see if endpoint exists
            response = requests.post(f"{BASE_URL}{endpoint}", json={})
            print(f"   {endpoint}: Status {response.status_code}")
            if response.status_code == 422:  # Validation error means endpoint exists
                print(f"      ✅ Endpoint exists (validation error expected)")
            elif response.status_code == 404:
                print(f"      ❌ Endpoint not found")
            else:
                print(f"      ℹ️  Response: {response.json()}")
        except Exception as e:
            print(f"   {endpoint}: ❌ Error - {e}")

def test_super_admin_creation():
    """Test super admin creation with detailed logging."""
    print("\n👑 Testing super admin creation...")
    
    admin_data = {
        "name": "Super Admin",
        "email": "admin@33kotidham.com",
        "mobile": "9999999999",
        "password": "admin123"
    }
    
    print(f"📝 Sending data: {json.dumps(admin_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/setup-super-admin", json=admin_data)
        print(f"📤 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📄 Response body: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📄 Response body (raw): {response.text}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Super admin creation failed: {e}")
        return False

def test_admin_login_detailed():
    """Test admin login with detailed logging."""
    print("\n🔐 Testing admin login...")
    
    login_data = {
        "username": "9999999999",
        "password": "admin123"
    }
    
    print(f"📝 Sending login data: {json.dumps(login_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/admin-login", json=login_data)
        print(f"📤 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📄 Response body: {json.dumps(response_data, indent=2)}")
            
            if response.status_code == 200:
                token = response_data.get("access_token")
                if token:
                    print(f"🎟️  Token received: {token[:50]}...")
                    return token
            
        except:
            print(f"📄 Response body (raw): {response.text}")
            
    except Exception as e:
        print(f"❌ Admin login failed: {e}")
    
    return None

def test_regular_user_endpoints():
    """Test regular user endpoints for comparison."""
    print("\n👤 Testing regular user endpoints...")
    
    # Test OTP request
    otp_data = {"mobile": "9999999999"}
    try:
        response = requests.post(f"{BASE_URL}/auth/request-otp", json=otp_data)
        print(f"📱 OTP request: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Response: {result}")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"📱 OTP request failed: {e}")

def test_database_connection():
    """Test if we can infer database issues."""
    print("\n🗄️  Testing database connectivity...")
    
    # Try to access public endpoints that might reveal DB issues
    try:
        response = requests.get(f"{BASE_URL}/pujas/")
        print(f"📚 Public pujas endpoint: {response.status_code}")
        if response.status_code == 200:
            pujas = response.json()
            print(f"   Found {len(pujas)} pujas in database")
        else:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"📚 Pujas endpoint failed: {e}")

def main():
    """Run all diagnostic tests."""
    print("🔍 Authentication Debug Tool")
    print("=" * 50)
    
    # Test 1: Server connection
    if not test_server_connection():
        print("\n❌ Server is not responding. Please start the FastAPI server first.")
        return
    
    # Test 2: Auth endpoints
    test_auth_endpoints()
    
    # Test 3: Database connection
    test_database_connection()
    
    # Test 4: Super admin creation
    admin_created = test_super_admin_creation()
    
    # Test 5: Admin login
    token = test_admin_login_detailed()
    
    # Test 6: Regular user endpoints
    test_regular_user_endpoints()
    
    # Summary
    print("\n📊 DIAGNOSTIC SUMMARY:")
    print("=" * 30)
    
    if token:
        print("✅ Admin authentication is working!")
        print("   You can proceed with puja creation tests.")
    elif admin_created:
        print("⚠️  Super admin was created but login failed")
        print("   This suggests a password hashing or verification issue.")
    else:
        print("❌ Authentication system has issues")
        print("   Check server logs and database connectivity.")
    
    print("\n💡 Recommendations:")
    if not token:
        print("   1. Check server console for error messages")
        print("   2. Verify database is properly initialized")
        print("   3. Try accessing http://localhost:8000/docs manually")
        print("   4. Check if bcrypt is properly installed")
        print("   5. Consider restarting the server")

if __name__ == "__main__":
    main()
