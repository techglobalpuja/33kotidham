#!/usr/bin/env python
"""
Check specific failed WhatsApp message details
"""
from twilio.rest import Client
from decouple import config

TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")

# The failed message SID from your server
MESSAGE_SID = "MM40d37d7e30aa53a4aebb000ddfc91255"

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 CHECKING FAILED MESSAGE DETAILS")
    print("="*80)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages(MESSAGE_SID).fetch()
        
        print(f"\n📨 Message SID: {message.sid}")
        print(f"📱 From: {message.from_}")
        print(f"📱 To: {message.to}")
        print(f"📊 Status: {message.status.upper()}")
        print(f"📅 Date Sent: {message.date_sent}")
        print(f"📅 Date Updated: {message.date_updated}")
        print(f"💰 Price: {message.price} {message.price_unit}")
        print(f"🔢 Error Code: {message.error_code or 'None'}")
        print(f"❌ Error Message: {message.error_message or 'None'}")
        print(f"🔄 Number of Media: {message.num_media}")
        print(f"🔄 Number of Segments: {message.num_segments}")
        
        if message.body:
            print(f"\n📝 Message Body (first 200 chars):")
            print(f"{message.body[:200]}...")
        
        print("\n" + "="*80)
        print("🔍 ERROR ANALYSIS")
        print("="*80)
        
        if message.error_code:
            error_explanations = {
                "63007": "Recipient not in WhatsApp Sandbox - Send 'join ancient-science' to +14155238886",
                "63016": "Maximum message size exceeded",
                "21211": "Invalid 'To' phone number",
                "21408": "Permission to send WhatsApp messages has not been enabled",
                "21606": "Phone number is not a valid WhatsApp number",
                "30007": "Message filtered (spam)",
                "30008": "Unknown error",
                "63003": "Sending window has expired (only 24h to reply)",
            }
            
            explanation = error_explanations.get(str(message.error_code), "Unknown error code")
            print(f"\n❌ Error Code {message.error_code}: {explanation}")
            
            if message.error_code == 63007:
                print("\n🔧 SOLUTION:")
                print("   The recipient needs to join your WhatsApp Sandbox:")
                print(f"   1. Open WhatsApp on phone: {message.to.replace('whatsapp:+91', '')}")
                print(f"   2. Send to: +14155238886")
                print(f"   3. Message: join ancient-science")
                print(f"   4. Wait for confirmation")
            elif message.error_code == 21408:
                print("\n🔧 SOLUTION:")
                print("   Your Twilio account needs WhatsApp enabled:")
                print("   1. Go to: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn")
                print("   2. Enable WhatsApp Sandbox")
                print("   3. Get your join code")
        
        print("\n" + "="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error fetching message: {str(e)}\n")
        import traceback
        print(traceback.format_exc())
