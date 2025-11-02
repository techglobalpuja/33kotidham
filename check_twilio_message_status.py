#!/usr/bin/env python3
"""Check the actual status of a Twilio WhatsApp message."""

from app.config import settings
from twilio.rest import Client
import sys

def check_message_status(message_sid):
    """Check the status of a Twilio message."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("❌ Twilio credentials not configured")
        return
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages(message_sid).fetch()
        
        print(f"\n{'='*70}")
        print(f"📬 TWILIO MESSAGE STATUS CHECK")
        print(f"{'='*70}")
        print(f"📧 Message SID: {message.sid}")
        print(f"📱 From: {message.from_}")
        print(f"📱 To: {message.to}")
        print(f"📨 Body: {message.body[:100]}..." if len(message.body) > 100 else f"📨 Body: {message.body}")
        print(f"⏰ Date Sent: {message.date_sent}")
        print(f"🚀 Status: {message.status}")
        print(f"📍 Error Code: {message.error_code if message.error_code else 'None'}")
        print(f"📍 Error Message: {message.error_message if message.error_message else 'None'}")
        print(f"💰 Price: {message.price if message.price else 'N/A'}")
        print(f"📊 Price Unit: {message.price_unit if message.price_unit else 'N/A'}")
        print(f"🎯 Num Media: {message.num_media}")
        print(f"{'='*70}\n")
        
        # Interpret status
        if message.status == "delivered":
            print("✅ Message DELIVERED to recipient!")
        elif message.status == "sent":
            print("⏳ Message SENT but delivery status unknown")
        elif message.status == "queued":
            print("⏳ Message QUEUED - still pending send")
        elif message.status == "failed":
            print(f"❌ Message FAILED - Error: {message.error_message}")
        elif message.status == "undelivered":
            print(f"❌ Message UNDELIVERED - Error: {message.error_message}")
        
        return message
        
    except Exception as e:
        print(f"❌ Error checking message status: {e}")
        import traceback
        print(traceback.format_exc())
        return None

if __name__ == "__main__":
    # Use the message SID from your output
    message_sid = "MM5f0dee43cbb6a190ab409cb2d4e42629"
    
    if len(sys.argv) > 1:
        message_sid = sys.argv[1]
    
    print(f"\n🔍 Checking message status for: {message_sid}")
    check_message_status(message_sid)
