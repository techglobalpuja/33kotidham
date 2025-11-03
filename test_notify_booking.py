#!/usr/bin/env python
"""Test booking creation with WhatsApp and Email notifications."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Your authorization token
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3MDAwMTE4NjUxIiwicm9sZSI6InN1cGVyX2FkbWluIiwiZXhwIjoxNzYyMjIwMDU5fQ.WingG8r6NbJgHeh1mZ662NQ5YaZH82u2BEq1hQz9n9Q"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
    "accept": "application/json"
}

# Your booking details
booking_data = {
    "puja_id": 72,
    "temple_id": 0,
    "plan_id": 7,
    "booking_date": "2025-11-02T06:31:51.169Z",
    "mobile_number": "8962507486",
    "whatsapp_number": "+918962507486",
    "gotra": "Test Gotra",
    "chadawas": [],
    "chadawa_ids": [9]
}

print("=" * 70)
print("📦 CREATING BOOKING WITH NOTIFICATIONS TEST")
print("=" * 70)

print("\n📋 Booking Details:")
print(json.dumps(booking_data, indent=2))

print("\n" + "=" * 70)
print("🚀 Sending booking request...")
print("=" * 70)

try:
    response = requests.post(
        f"{BASE_URL}/bookings/razorpay-booking",
        json=booking_data,
        headers=headers
    )
    
    print(f"\n✓ Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code in [200, 201]:
        booking_id = response.json().get("id")
        print(f"\n✅ SUCCESS! Booking created with ID: {booking_id}")
        print("\n" + "=" * 70)
        print("📨 NOTIFICATIONS SHOULD BE SENT!")
        print("=" * 70)
        print("\n✉️  EMAIL NOTIFICATION:")
        print("   - Recipient: Your email address")
        print("   - Subject: 'Booking Confirmed - Ref: {booking_id}'")
        print("   - Check: Inbox & Spam folder")
        
        print("\n💬 WHATSAPP NOTIFICATION:")
        print("   - From: +19804808487 (Twilio WhatsApp)")
        print("   - To: +918962507486")
        print("   - Message: 'Booking Received' with booking details")
        
        print("\n📋 SERVER LOGS:")
        print("   - Look for messages like:")
        print("     'Email sent successfully to...'")
        print("     'WhatsApp message sent successfully to...'")
        print("     'Booking notification sent'")
    else:
        print(f"\n❌ Request failed with status {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("\n" + "=" * 70)
print("TEST COMPLETE - Check email and WhatsApp for notifications")
print("=" * 70)
