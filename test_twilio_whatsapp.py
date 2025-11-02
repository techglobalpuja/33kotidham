#!/usr/bin/env python
"""Test Twilio WhatsApp configuration and send a test message."""

from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')

print("=" * 70)
print("📱 TESTING TWILIO WHATSAPP CONFIGURATION")
print("=" * 70)

print(f"\n📋 Current Configuration:")
print(f"   Account SID: {TWILIO_ACCOUNT_SID[:20]}...")
print(f"   Auth Token: {TWILIO_AUTH_TOKEN[:20]}...")
print(f"   Phone Number: {TWILIO_PHONE_NUMBER}")

print(f"\n⚠️  IMPORTANT:")
print(f"   The WhatsApp sandbox requires a specific 'From' number.")
print(f"   You need to use the Twilio SANDBOX WhatsApp number format:")
print(f"   From: whatsapp:+14155238886 (Twilio Sandbox)")
print(f"   This is a TEST number provided by Twilio")

print(f"\n📝 To enable WhatsApp messaging:")
print(f"   1. Go to Twilio Console > Messaging > Send a WhatsApp message")
print(f"   2. Click 'Opt In' and follow the instructions")
print(f"   3. Send test message from your Twilio sandbox number")
print(f"   4. Once opt-in is complete, bookings will send WhatsApp messages")

print(f"\n🔗 Twilio WhatsApp Sandbox Setup:")
print(f"   https://www.twilio.com/console/sms/whatsapp/sandbox")

try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    
    # Try to get account info
    account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
    print(f"\n✅ Twilio Account Connected:")
    print(f"   Status: {account.status}")
    
    # Try to send a test WhatsApp message
    print(f"\n📤 Attempting to send test WhatsApp message...")
    print(f"   From: whatsapp:+14155238886")
    print(f"   To: whatsapp:+918962507486")
    
    msg = client.messages.create(
        body='Test message from 33 Koti Dham booking system',
        from_='whatsapp:+14155238886',
        to='whatsapp:+918962507486'
    )
    
    print(f"\n✅ WhatsApp message sent!")
    print(f"   Message SID: {msg.sid}")
    print(f"   Status: {msg.status}")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print(f"\n💡 Solution:")
    print(f"   1. If you see 'Channel with specified From address' error:")
    print(f"      - Update TWILIO_PHONE_NUMBER in .env to: +14155238886")
    print(f"      - This is the Twilio WhatsApp Sandbox number")
    print(f"   2. Make sure your personal number is opt-ed in:")
    print(f"      - Go to: https://www.twilio.com/console/sms/whatsapp/sandbox")
    print(f"      - Send the JOIN code to activate your number")

print(f"\n" + "=" * 70)
