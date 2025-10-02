#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint."""
    response = requests.get("http://localhost:8000/health")
    print(f"Health check: {response.status_code} - {response.json()}")

def test_register():
    """Test user registration."""
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "mobile": "+919876543210",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register: {response.status_code}")
    if response.status_code == 200:
        print(f"User created: {response.json()}")
    else:
        print(f"Error: {response.text}")

def test_login():
    """Test user login."""
    login_data = {
        "mobile": "+919876543210",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Token: {token_data['access_token'][:50]}...")
        return token_data['access_token']
    else:
        print(f"Error: {response.text}")
        return None

def test_get_pujas():
    """Test getting pujas."""
    response = requests.get(f"{BASE_URL}/pujas/")
    print(f"Get pujas: {response.status_code}")
    if response.status_code == 200:
        pujas = response.json()
        print(f"Found {len(pujas)} pujas")
    else:
        print(f"Error: {response.text}")

def main():
    """Run API tests."""
    print("Testing 33 Koti Dham API...")
    print("=" * 40)
    
    test_health()
    print()
    
    test_register()
    print()
    
    token = test_login()
    print()
    
    test_get_pujas()
    print()
    
    print("API tests completed!")

if __name__ == "__main__":
    main()
