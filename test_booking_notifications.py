#!/usr/bin/env python
"""Test script to create a booking and verify WhatsApp + Email notifications."""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Step 1: Request OTP
print("=" * 60)
print("STEP 1: Requesting OTP for mobile number")
print("=" * 60)

mobile = "8962507486"
otp_response = requests.post(
    f"{BASE_URL}/auth/request-otp",
    json={"mobile": mobile}
)
print(f"✓ OTP Request Status: {otp_response.status_code}")
print(f"Response: {json.dumps(otp_response.json(), indent=2)}")

# For testing, we need to get the OTP from the database or logs
# Usually in development, check the server logs or database for the OTP code
print("\n⚠️  Please check server logs or database for the generated OTP code")
print("Query: SELECT * FROM otps WHERE user_id = (SELECT id FROM users WHERE mobile = '8962507486') ORDER BY created_at DESC LIMIT 1;")

# Step 2: Verify OTP (manual input needed)
print("\n" + "=" * 60)
print("STEP 2: Verify OTP")
print("=" * 60)

otp_code = input("Enter the OTP code you found: ").strip()

verify_response = requests.post(
    f"{BASE_URL}/auth/verify-otp",
    json={
        "mobile": mobile,
        "otp_code": otp_code
    }
)
print(f"✓ OTP Verification Status: {verify_response.status_code}")
print(f"Response: {json.dumps(verify_response.json(), indent=2)}")

if verify_response.status_code != 200:
    print("❌ OTP verification failed. Cannot proceed.")
    exit(1)

# Extract access token
token = verify_response.json().get("access_token")
if not token:
    print("❌ No access token received")
    exit(1)

print(f"✓ Access Token: {token[:50]}...")

# Step 3: Create a booking with notifications
print("\n" + "=" * 60)
print("STEP 3: Creating a booking (will trigger notifications)")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

booking_data = {
    "puja_id": 1,  # Adjust based on your pujas
    "whatsapp_number": "+918962507486",  # Your WhatsApp number
    "mobile_number": "8962507486",
    "gotra": "Test Gotra",
    "booking_date": (datetime.now() + timedelta(days=7)).isoformat()
}

print(f"\nBooking Data:")
print(json.dumps(booking_data, indent=2))

booking_response = requests.post(
    f"{BASE_URL}/bookings",
    json=booking_data,
    headers=headers
)

print(f"\n✓ Booking Creation Status: {booking_response.status_code}")
print(f"Response: {json.dumps(booking_response.json(), indent=2)}")

if booking_response.status_code in [200, 201]:
    booking_id = booking_response.json().get("id")
    print(f"\n✅ Booking created successfully! ID: {booking_id}")
    print("\n" + "=" * 60)
    print("📧 EMAIL & 💬 WHATSAPP NOTIFICATIONS SHOULD BE SENT!")
    print("=" * 60)
    print("\nCheck the following:")
    print("1. ✉️  Email: Check your email inbox/spam folder")
    print(f"2. 💬 WhatsApp: Check message from +{'+19804808487'} on {mobile}")
    print("3. 📋 Server logs: Should show notification sent messages")
else:
    print(f"\n❌ Booking creation failed!")
    print(f"Error: {booking_response.text}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
