#!/usr/bin/env python3
"""
Try to login with potentially existing admin credentials.
This tests various common admin credential combinations.
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"

def try_admin_login():
    """Try various admin credential combinations."""
    print("🔐 Trying Existing Admin Credentials")
    print("=" * 40)
    
    # Common admin credential combinations
    credential_combinations = [
        # Original test credentials
        {"username": "9999999999", "password": "admin123"},
        {"username": "admin@33kotidham.com", "password": "admin123"},
        
        # Variations with different cases
        {"username": "9999999999", "password": "Admin123"},
        {"username": "admin@33kotidham.com", "password": "Admin123"},
        
        # Common default passwords
        {"username": "9999999999", "password": "password"},
        {"username": "admin@33kotidham.com", "password": "password"},
        {"username": "9999999999", "password": "123456"},
        {"username": "admin@33kotidham.com", "password": "123456"},
        
        # Empty password (in case it was created without password)
        {"username": "9999999999", "password": ""},
        {"username": "admin@33kotidham.com", "password": ""},
        
        # Different mobile numbers that might have been used
        {"username": "1234567890", "password": "admin123"},
        {"username": "0000000000", "password": "admin123"},
    ]
    
    for i, creds in enumerate(credential_combinations, 1):
        print(f"\n🔑 Attempt {i}: {creds['username']} / {'*' * len(creds['password']) if creds['password'] else '(empty)'}")
        
        try:
            response = requests.post(f"{BASE_URL}/auth/admin-login", json=creds)
            
            if response.status_code == 200:
                token = response.json().get("access_token")
                print(f"   ✅ SUCCESS! Login worked!")
                print(f"   Token: {token[:50]}...")
                
                # Test the token
                headers = {"Authorization": f"Bearer {token}"}
                try:
                    user_response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
                    if user_response.status_code == 200:
                        user_info = user_response.json()
                        print(f"   👤 User: {user_info['name']}")
                        print(f"   📧 Email: {user_info.get('email', 'N/A')}")
                        print(f"   📱 Mobile: {user_info['mobile']}")
                        print(f"   👑 Role: {user_info['role']}")
                        
                        print(f"\n🎉 WORKING CREDENTIALS FOUND!")
                        print(f"   Username: {creds['username']}")
                        print(f"   Password: {creds['password']}")
                        return creds, token
                except Exception as e:
                    print(f"   ⚠️  Token validation failed: {e}")
                    
            elif response.status_code == 401:
                print(f"   ❌ Invalid credentials")
            elif response.status_code == 403:
                print(f"   ❌ Access denied (user exists but not admin)")
            else:
                print(f"   ❌ Error {response.status_code}: {response.json()}")
                
        except Exception as e:
            print(f"   ❌ Request failed: {e}")
    
    print(f"\n❌ No working credentials found")
    
    # Try to create a fresh admin
    print(f"\n🆕 Trying to create a fresh admin...")
    fresh_admin = {
        "name": "Fresh Admin",
        "email": "fresh@33kotidham.com",
        "mobile": "7777777777",
        "password": "fresh123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/setup-super-admin", json=fresh_admin)
        print(f"   Setup status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Fresh admin created!")
            
            # Try to login with fresh credentials
            fresh_login = {
                "username": "7777777777",
                "password": "fresh123"
            }
            
            response = requests.post(f"{BASE_URL}/auth/admin-login", json=fresh_login)
            if response.status_code == 200:
                token = response.json().get("access_token")
                print(f"   ✅ Fresh admin login successful!")
                print(f"   Token: {token[:50]}...")
                return fresh_login, token
            else:
                print(f"   ❌ Fresh admin login failed: {response.json()}")
        else:
            print(f"   ❌ Fresh admin creation failed: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Fresh admin error: {e}")
    
    return None, None

def main():
    """Main function."""
    creds, token = try_admin_login()
    
    if creds and token:
        print(f"\n🎯 SUCCESS! Use these credentials:")
        print(f"   Username: {creds['username']}")
        print(f"   Password: {creds['password']}")
        print(f"\n💡 Update your test scripts with these credentials")
        
        # Test creating a puja with working credentials
        print(f"\n🕉️  Testing puja creation with working credentials...")
        headers = {"Authorization": f"Bearer {token}"}
        
        test_puja = {
            "name": "Test Puja",
            "sub_heading": "Testing puja creation",
            "description": "This is a test puja to verify the API works",
            "category": "Test"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/pujas/", headers=headers, json=test_puja)
            if response.status_code == 200:
                puja = response.json()
                print(f"   ✅ Test puja created successfully! ID: {puja['id']}")
            else:
                print(f"   ❌ Puja creation failed: {response.status_code}")
                print(f"   Error: {response.json()}")
        except Exception as e:
            print(f"   ❌ Puja creation error: {e}")
    else:
        print(f"\n❌ No working admin credentials found")
        print(f"\n💡 Troubleshooting steps:")
        print(f"   1. Check if the server is running correctly")
        print(f"   2. Check server logs for authentication errors")
        print(f"   3. Verify database is properly initialized")
        print(f"   4. Try accessing http://localhost:8000/docs manually")
        print(f"   5. Consider resetting the database")

if __name__ == "__main__":
    main()
