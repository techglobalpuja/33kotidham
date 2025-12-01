#!/usr/bin/env python
"""
WhatsApp Message Status Checker
Check Twilio WhatsApp message delivery status for debugging
"""
from twilio.rest import Client
from decouple import config
from datetime import datetime, timedelta

# Load Twilio credentials
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_WHATSAPP_NUMBER = config("TWILIO_WHATSAPP_NUMBER", default="+14155238886")

def check_whatsapp_messages(hours_back=24, limit=20):
    """Check recent WhatsApp message status."""
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("❌ Twilio credentials not configured in .env file")
        return
    
    print("\n" + "="*80)
    print("📱 TWILIO WHATSAPP MESSAGE STATUS CHECKER")
    print("="*80)
    print(f"🔍 Checking messages from last {hours_back} hours...")
    print(f"📊 Showing up to {limit} most recent messages\n")
    
    try:
        # Initialize Twilio client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Calculate date filter
        date_after = datetime.utcnow() - timedelta(hours=hours_back)
        
        # Fetch messages sent from WhatsApp number
        messages = client.messages.list(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            date_sent_after=date_after,
            limit=limit
        )
        
        if not messages:
            print("📭 No WhatsApp messages found in the last {} hours".format(hours_back))
            print("\n💡 This could mean:")
            print("   1. No bookings were created recently")
            print("   2. SEND_WHATSAPP_ON_BOOKING is set to False")
            print("   3. Messages are being sent from a different number")
            return
        
        print(f"✅ Found {len(messages)} message(s)\n")
        print("-"*80)
        
        for idx, msg in enumerate(messages, 1):
            print(f"\n📨 Message #{idx}")
            print(f"   Message SID: {msg.sid}")
            print(f"   To: {msg.to}")
            print(f"   Status: {msg.status.upper()}")
            print(f"   Date Sent: {msg.date_sent}")
            print(f"   Error Code: {msg.error_code or 'None'}")
            print(f"   Error Message: {msg.error_message or 'None'}")
            
            # Explain status
            status_explanations = {
                "queued": "⏳ Message is waiting to be sent (RECIPIENT NOT OPTED IN TO SANDBOX)",
                "sending": "📤 Message is being sent",
                "sent": "✅ Message was sent successfully",
                "delivered": "✅ Message was delivered to recipient",
                "undelivered": "❌ Message failed to deliver",
                "failed": "❌ Message failed to send",
                "received": "✅ Message was received by recipient"
            }
            
            explanation = status_explanations.get(msg.status.lower(), "Unknown status")
            print(f"   Meaning: {explanation}")
            
            # Show message preview (first 100 chars)
            if msg.body:
                preview = msg.body[:100] + "..." if len(msg.body) > 100 else msg.body
                print(f"   Preview: {preview}")
            
            # Show media if present
            if msg.num_media and int(msg.num_media) > 0:
                print(f"   Media: {msg.num_media} attachment(s)")
            
            print("-"*80)
        
        # Summary
        print("\n📊 STATUS SUMMARY:")
        status_counts = {}
        for msg in messages:
            status_counts[msg.status] = status_counts.get(msg.status, 0) + 1
        
        for status, count in status_counts.items():
            print(f"   {status.upper()}: {count}")
        
        # Check for queued messages (sandbox issue)
        queued_count = status_counts.get('queued', 0)
        if queued_count > 0:
            print(f"\n⚠️  WARNING: {queued_count} message(s) are QUEUED")
            print("   This usually means the recipient hasn't joined the WhatsApp Sandbox!")
            print("\n🔧 TO FIX:")
            print(f"   1. Open WhatsApp on recipient's phone")
            print(f"   2. Send to: {TWILIO_WHATSAPP_NUMBER}")
            print(f"   3. Message: join ancient-science")
            print(f"   4. Wait for confirmation")
            print("\n   Get your exact code: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
        
    except Exception as e:
        print(f"❌ Error checking messages: {str(e)}")
        import traceback
        print(traceback.format_exc())
    
    print("\n" + "="*80 + "\n")


def check_specific_message(message_sid):
    """Check status of a specific message by SID."""
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("❌ Twilio credentials not configured")
        return
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages(message_sid).fetch()
        
        print("\n" + "="*80)
        print("📨 MESSAGE DETAILS")
        print("="*80)
        print(f"Message SID: {message.sid}")
        print(f"From: {message.from_}")
        print(f"To: {message.to}")
        print(f"Status: {message.status.upper()}")
        print(f"Date Created: {message.date_created}")
        print(f"Date Sent: {message.date_sent}")
        print(f"Date Updated: {message.date_updated}")
        print(f"Direction: {message.direction}")
        print(f"Price: {message.price} {message.price_unit}")
        print(f"Error Code: {message.error_code or 'None'}")
        print(f"Error Message: {message.error_message or 'None'}")
        print(f"\nBody:\n{message.body}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Error fetching message: {str(e)}")


def get_account_info():
    """Get Twilio account information."""
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("❌ Twilio credentials not configured")
        return
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        account = client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        
        print("\n" + "="*80)
        print("📊 TWILIO ACCOUNT INFO")
        print("="*80)
        print(f"Account SID: {account.sid}")
        print(f"Friendly Name: {account.friendly_name}")
        print(f"Status: {account.status.upper()}")
        print(f"Type: {account.type}")
        print(f"WhatsApp Number: {TWILIO_WHATSAPP_NUMBER}")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"❌ Error fetching account info: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("\n🔍 WhatsApp Message Status Checker")
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "account":
            get_account_info()
        elif sys.argv[1].startswith("SM"):
            # Message SID provided
            check_specific_message(sys.argv[1])
        else:
            print("Usage:")
            print("  python check_whatsapp_status.py              # Check recent messages")
            print("  python check_whatsapp_status.py account      # Show account info")
            print("  python check_whatsapp_status.py SM...        # Check specific message")
    else:
        # Default: Check recent messages
        check_whatsapp_messages(hours_back=72, limit=50)
        get_account_info()
