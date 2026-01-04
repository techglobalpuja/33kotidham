"""
Check Twilio WhatsApp message delivery status
"""
from twilio.rest import Client
from app.config import settings
from datetime import datetime, timedelta

def check_recent_messages(hours=1):
    """Check all WhatsApp messages sent in the last N hours"""
    print("\n" + "="*70)
    print("📱 TWILIO WHATSAPP MESSAGE STATUS CHECK")
    print("="*70)
    
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("\n❌ Twilio credentials not configured")
        return
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Get messages from last N hours WITHOUT filtering by from number
        # (Some messages might not show up with from filter)
        date_sent_after = datetime.now() - timedelta(hours=hours)
        
        print(f"\n🔍 Fetching ALL messages sent after: {date_sent_after.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📞 Expected from: {settings.TWILIO_WHATSAPP_NUMBER}\n")
        
        # Try without from filter first
        messages = client.messages.list(
            date_sent_after=date_sent_after,
            limit=100
        )
        
        # Filter for WhatsApp messages only
        whatsapp_messages = [m for m in messages if 'whatsapp:' in str(m.from_) or 'whatsapp:' in str(m.to)]
        
        if not whatsapp_messages:
            print("❌ No WhatsApp messages found in the last hour")
            print("\nTrying to fetch recent messages by SID...")
            
            # Try to fetch a few recent messages directly
            all_recent = client.messages.list(limit=20)
            print(f"\n📋 Last 20 messages (any type):")
            for msg in all_recent[:5]:
                print(f"   {msg.sid}: {msg.from_} → {msg.to} ({msg.status})")
            
            print("\nPossible reasons:")
            print("   1. Messages were rejected immediately by Twilio")
            print("   2. Using wrong Twilio project/credentials")
            print("   3. Messages sent from different account")
            return
        
        messages = whatsapp_messages
        print(f"✅ Found {len(messages)} WhatsApp message(s):\n")
        
        for msg in messages:
            status_icon = {
                'queued': '⏳',
                'sending': '📤',
                'sent': '✅',
                'delivered': '✅✅',
                'undelivered': '❌',
                'failed': '🔴',
                'read': '✅✅✅'
            }.get(msg.status, '❓')
            
            print(f"{status_icon} Message SID: {msg.sid}")
            print(f"   To: {msg.to}")
            print(f"   Status: {msg.status.upper()}")
            print(f"   Sent: {msg.date_sent}")
            
            if msg.error_code:
                print(f"   ❌ Error Code: {msg.error_code}")
                print(f"   ❌ Error Message: {msg.error_message}")
            
            # Fetch detailed status
            try:
                msg_detail = client.messages(msg.sid).fetch()
                print(f"   Price: {msg_detail.price} {msg_detail.price_unit}")
                if msg_detail.num_media != '0':
                    print(f"   Media: {msg_detail.num_media} attachment(s)")
            except:
                pass
            
            print()
        
        # Check for common issues
        print("\n" + "="*70)
        print("📋 DIAGNOSTICS")
        print("="*70)
        
        failed_msgs = [m for m in messages if m.status in ['failed', 'undelivered']]
        if failed_msgs:
            print(f"\n❌ {len(failed_msgs)} message(s) failed:")
            for msg in failed_msgs:
                print(f"   • {msg.to}: Error {msg.error_code} - {msg.error_message}")
        
        queued_msgs = [m for m in messages if m.status in ['queued', 'sending']]
        if queued_msgs:
            print(f"\n⏳ {len(queued_msgs)} message(s) still queued/sending")
        
        sent_msgs = [m for m in messages if m.status in ['sent', 'delivered', 'read']]
        if sent_msgs:
            print(f"\n✅ {len(sent_msgs)} message(s) sent/delivered")
        
        # Check for sandbox join requirement
        undelivered = [m for m in messages if m.status == 'failed' and m.error_code == 63016]
        if undelivered:
            print("\n⚠️  SANDBOX JOIN REQUIRED!")
            print("="*70)
            print("\nRecipients must join the Twilio Sandbox first:")
            print(f"\n1. Send this message to WhatsApp number: {settings.TWILIO_WHATSAPP_NUMBER}")
            print(f"   Message: 'join <your-sandbox-keyword>'")
            print("\n2. Get your sandbox keyword from Twilio Console:")
            print("   https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
            print("\n3. Each recipient must join before receiving messages")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        print(traceback.format_exc())


def check_sandbox_status():
    """Check Twilio Sandbox configuration"""
    print("\n" + "="*70)
    print("🔧 TWILIO SANDBOX CONFIGURATION")
    print("="*70)
    
    print(f"\n📞 Twilio WhatsApp Number: {settings.TWILIO_WHATSAPP_NUMBER}")
    print(f"🔑 Account SID: {settings.TWILIO_ACCOUNT_SID[:20]}...")
    print(f"✅ Send WhatsApp: {settings.SEND_WHATSAPP_ON_BOOKING}")
    
    print("\n⚠️  IMPORTANT: Twilio Sandbox Requirements")
    print("="*70)
    print("\nFor testing with Twilio Sandbox:")
    print("1. Each recipient must join your sandbox first")
    print("2. Send 'join <sandbox-code>' to your Twilio WhatsApp number")
    print("3. You'll receive a confirmation message")
    print("4. Only then can you receive template messages")
    
    print("\n📝 To find your sandbox join code:")
    print("   https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")


def check_specific_message(message_sid: str):
    """Check a specific message by SID"""
    print("\n" + "="*70)
    print(f"🔍 CHECKING MESSAGE: {message_sid}")
    print("="*70)
    
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("\n❌ Twilio credentials not configured")
        return
    
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        message = client.messages(message_sid).fetch()
        
        status_icon = {
            'queued': '⏳',
            'sending': '📤',
            'sent': '✅',
            'delivered': '✅✅',
            'undelivered': '❌',
            'failed': '🔴',
            'read': '✅✅✅'
        }.get(message.status, '❓')
        
        print(f"\n{status_icon} Message Details:")
        print(f"   SID: {message.sid}")
        print(f"   From: {message.from_}")
        print(f"   To: {message.to}")
        print(f"   Status: {message.status.upper()}")
        print(f"   Date Created: {message.date_created}")
        print(f"   Date Sent: {message.date_sent}")
        print(f"   Date Updated: {message.date_updated}")
        print(f"   Direction: {message.direction}")
        print(f"   Price: {message.price} {message.price_unit}")
        
        if message.error_code:
            print(f"\n❌ ERROR DETAILS:")
            print(f"   Error Code: {message.error_code}")
            print(f"   Error Message: {message.error_message}")
            
            # Common Twilio WhatsApp error codes
            if message.error_code == 63016:
                print(f"\n⚠️  Error 63016: User has not joined sandbox")
                print(f"   Recipient must send 'join <code>' to {settings.TWILIO_WHATSAPP_NUMBER}")
            elif message.error_code == 21408:
                print(f"\n⚠️  Error 21408: Permission to send denied")
                print(f"   May need to verify WhatsApp Business account")
            elif message.error_code == 63007:
                print(f"\n⚠️  Error 63007: Template not approved or invalid")
            elif message.error_code == 63024:
                print(f"\n⚠️  Error 63024: Template content mismatch or syntax error")
                print(f"\n   COMMON CAUSES:")
                print(f"   1. Template variables don't match approved template")
                print(f"   2. Using Content Template API incorrectly")
                print(f"   3. Template SID is for wrong template type")
                print(f"   4. Missing required template parameters")
                print(f"\n   SOLUTION:")
                print(f"   • Check template in Twilio Console:")
                print(f"     https://console.twilio.com/us1/develop/sms/content-editor")
                print(f"   • Verify template variables match exactly")
                print(f"   • For sandbox: Use Message Template API instead of Content Template API")
            elif message.error_code == 63025:
                print(f"\n⚠️  Error 63025: Template rejected by WhatsApp")
                print(f"   Template may not be approved for production use")
        
        print()
        
    except Exception as e:
        print(f"\n❌ Error fetching message: {str(e)}")


if __name__ == "__main__":
    import sys
    
    print("\n🔵 Twilio WhatsApp Delivery Checker")
    
    # Check specific message SID if provided
    if len(sys.argv) > 1:
        message_sid = sys.argv[1]
        check_specific_message(message_sid)
    else:
        # Check recent message delivery status
        check_recent_messages(hours=2)
    
    # Show sandbox configuration
    check_sandbox_status()
    
    print("\n" + "="*70)
    print("\n💡 TIP: To check a specific message:")
    print("   python check_twilio_delivery.py <MESSAGE_SID>")
    print("\n   Example:")
    print("   python check_twilio_delivery.py MM9265eb1d56f31d4badf6d009ba48011a")
    print("\n" + "="*70 + "\n")
