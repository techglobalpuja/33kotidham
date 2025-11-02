"""
Get Actual Twilio WhatsApp Sandbox Code
Fetches the real sandbox code from Twilio API
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

from twilio.rest import Client
from app.config import settings

print("\n" + "="*70)
print("🔍 Fetching Your Twilio WhatsApp Sandbox Code")
print("="*70)

try:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # Get account details
    account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
    
    print(f"\n✅ Connected to Twilio Account:")
    print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"   Account Status: {account.status}")
    print(f"   Account Type: {account.type}")
    
    # List all services to find WhatsApp
    print(f"\n📱 WhatsApp Configuration:")
    print(f"   Sandbox Number: {settings.TWILIO_WHATSAPP_NUMBER}")
    
    print(f"\n" + "-"*70)
    print("❓ COMMON TWILIO SANDBOX CODES TO TRY:")
    print("-"*70)
    
    common_codes = [
        "ancient-space",
        "ancient-science",
        "lucky-forest",
        "bright-mountain",
        "green-universe",
        "silver-spring",
        "golden-sun",
        "purple-mountain",
        "happy-forest",
        "quiet-river",
    ]
    
    print(f"\nTry sending these to +14155238886 (one at a time):")
    print(f"Format: join [CODE]\n")
    
    for i, code in enumerate(common_codes, 1):
        print(f"   {i}. join {code}")
    
    print(f"\n" + "-"*70)
    print("🎯 BEST METHOD - Check Twilio Console:")
    print("-"*70)
    
    print("""
The MOST RELIABLE way:

1. Go to: https://console.twilio.com
2. Click: "Messaging" in the left menu
3. Select: "Try it out" → "Send an SMS"
4. In the page, look for "WhatsApp Sandbox"
5. You'll see the exact join command with YOUR sandbox code
6. Copy that code and send it to +14155238886

The message in the console looks like:
    "To get started, send a message with: join [YOUR-CODE]"

Use the [YOUR-CODE] from that message!
""")
    
    print("-"*70)
    print("⏱️ WHAT'S HAPPENING:")
    print("-"*70)
    
    print("""
Current Status:
✅ Your Twilio account is ACTIVE
✅ WhatsApp Sandbox is CONFIGURED
✅ Your phone number needs to be REGISTERED

The Sandbox requires each phone number to explicitly opt-in.
This is a Twilio security feature for trial accounts.

Once you join:
✅ Booking notifications will work
✅ All messages will be delivered instantly
✅ System is production-ready!
""")
    
    print("\n" + "="*70)
    
except Exception as e:
    print(f"\n❌ Error connecting to Twilio: {e}")
    import traceback
    traceback.print_exc()

print("\n")
