#!/usr/bin/env python
"""
Sample WhatsApp Test - Quick test on server
Usage: python sample_message_wt.py <phone_number>
Example: python sample_message_wt.py 8962507486
"""
import sys
from twilio.rest import Client
from decouple import config

# Twilio credentials
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_WHATSAPP_NUMBER = config("TWILIO_WHATSAPP_NUMBER", default="+14155238886")

# The verified image URL
IMAGE_URL = "https://api.33kotidham.in/uploads/images/b4bd9c33-d6e3-4069-b436-ef8e4c5cfaa0.png"

def send_test_message(phone_number, with_image=True):
    """Send a test WhatsApp message."""
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("❌ Error: Twilio credentials not configured in .env file")
        return False
    
    # Normalize phone number
    phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
    if not phone.startswith("91") and len(phone) == 10:
        phone = "91" + phone
    if not phone.startswith("+"):
        phone = "+" + phone
    
    print("\n" + "="*70)
    print("📱 WHATSAPP TEST MESSAGE")
    print("="*70)
    print(f"To: {phone}")
    print(f"With Image: {with_image}")
    print(f"Image URL: {IMAGE_URL if with_image else 'None'}")
    print("-"*70)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_body = """🙏 *Test Message from 33 Koti Dham* 🙏

This is a sample test message to verify WhatsApp delivery.

✅ If you receive this, WhatsApp is working!

📋 Test Details:
   • Service: WhatsApp via Twilio
   • Image: Attached (PNG format)
   • Status: Testing

Thank you! 🙏"""
        
        print("\n📤 Sending message...")
        
        if with_image:
            msg = client.messages.create(
                body=message_body,
                from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{phone}",
                media_url=[IMAGE_URL]
            )
            print("📸 Message sent WITH image")
        else:
            msg = client.messages.create(
                body=message_body,
                from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
                to=f"whatsapp:{phone}"
            )
            print("📝 Message sent WITHOUT image (text only)")
        
        print("\n✅ SUCCESS!")
        print(f"   Message SID: {msg.sid}")
        print(f"   Status: {msg.status}")
        print(f"   To: {msg.to}")
        print(f"   From: {msg.from_}")
        
        if msg.status == "queued":
            print("\n⚠️  WARNING: Message is QUEUED")
            print("   This means the recipient needs to join WhatsApp Sandbox!")
            print("\n   📱 Recipient must:")
            print(f"      1. Open WhatsApp")
            print(f"      2. Send to: {TWILIO_WHATSAPP_NUMBER}")
            print(f"      3. Message: join ancient-science")
            print(f"      4. Wait for confirmation")
        elif msg.status in ["sent", "delivered"]:
            print("\n✅ Message delivered successfully!")
            print("   Check WhatsApp on your phone")
        
        print("="*70 + "\n")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED!")
        print(f"   Error: {str(e)}")
        print(f"   Type: {type(e).__name__}")
        print("="*70 + "\n")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("📱 SAMPLE WHATSAPP TEST")
        print("="*70)
        print("\nUsage:")
        print("  python sample_message_wt.py <phone_number> [no-image]")
        print("\nExamples:")
        print("  python sample_message_wt.py 8962507486")
        print("  python sample_message_wt.py 8962507486 no-image")
        print("  python sample_message_wt.py +918962507486")
        print("\nOptions:")
        print("  no-image  - Send message without image attachment")
        print("="*70 + "\n")
        sys.exit(1)
    
    phone = sys.argv[1]
    with_image = "no-image" not in sys.argv
    
    success = send_test_message(phone, with_image=with_image)
    
    if success:
        print("✅ Test completed successfully!")
        print("\nNext steps:")
        print("1. Check WhatsApp on phone:", phone)
        print("2. If not received, check if user joined sandbox")
        print("3. Run: python check_whatsapp_status.py")
    else:
        print("❌ Test failed!")
        print("\nTroubleshooting:")
        print("1. Check .env file has TWILIO credentials")
        print("2. Verify SEND_WHATSAPP_ON_BOOKING=true")
        print("3. Check phone number format")
        print("4. Run: python monitor_notifications.py config")
    
    sys.exit(0 if success else 1)
