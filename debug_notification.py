"""
Debug: Check if notifications are being sent
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*70)
print("🔍 DEBUGGING NOTIFICATION SENDING")
print("="*70)

from app.config import settings

print(f"\n✅ CONFIGURATION CHECK:")
print(f"   SEND_BOOKING_NOTIFICATIONS: {settings.SEND_BOOKING_NOTIFICATIONS}")
print(f"   SEND_EMAIL_ON_BOOKING: {settings.SEND_EMAIL_ON_BOOKING}")
print(f"   SEND_WHATSAPP_ON_BOOKING: {settings.SEND_WHATSAPP_ON_BOOKING}")
print(f"   TWILIO_ACCOUNT_SID: {'SET' if settings.TWILIO_ACCOUNT_SID else 'NOT SET'}")
print(f"   TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")

print(f"\n💡 IF SEND_WHATSAPP_ON_BOOKING = False:")
print(f"   → WhatsApp notifications will NOT be sent")
print(f"   → Fix: Edit .env file and set SEND_WHATSAPP_ON_BOOKING=true")
print(f"   → Then restart the server")

print(f"\n💡 IF SEND_BOOKING_NOTIFICATIONS = False:")
print(f"   → ALL notifications will be SKIPPED")
print(f"   → Fix: Edit .env file and set SEND_BOOKING_NOTIFICATIONS=true")
print(f"   → Then restart the server")

print("\n" + "="*70)

# Now test sending a WhatsApp message directly
print("\n🧪 TESTING DIRECT WHATSAPP SEND:")
print("="*70)

from app.services import NotificationService

test_phone = "+918962507486"
test_message = """
🧪 *Direct WhatsApp Test* 🧪

If you receive this, notifications are working!

This is a direct test message.
"""

print(f"\nSending to: {test_phone}")
print(f"Settings check:")
print(f"  - SEND_WHATSAPP_ON_BOOKING: {settings.SEND_WHATSAPP_ON_BOOKING}")
print(f"  - TWILIO credentials: {'✅ OK' if settings.TWILIO_ACCOUNT_SID else '❌ MISSING'}")

result = NotificationService.send_whatsapp_notification(test_phone, test_message)
print(f"\nResult: {result}")

if result:
    print("✅ Message sent successfully!")
    print("Check your WhatsApp in a few seconds")
else:
    print("❌ Message failed!")
    print("Check the logs above for the reason")

print("\n" + "="*70 + "\n")
