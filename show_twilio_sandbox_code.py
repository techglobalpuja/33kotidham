"""
Check Twilio Sandbox Code and Status
This script helps you find the correct sandbox code for joining
"""

import os
from dotenv import load_dotenv

load_dotenv()

from twilio.rest import Client
from app.config import settings

print("\n" + "="*70)
print("🔍 Twilio Sandbox Information Checker")
print("="*70)

try:
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    print(f"\n📱 Twilio Account: {settings.TWILIO_ACCOUNT_SID}")
    print(f"📱 WhatsApp Sandbox Number: {settings.TWILIO_WHATSAPP_NUMBER}")
    
    print("\n" + "-"*70)
    print("ℹ️  WHAT TO DO NOW:")
    print("-"*70)
    
    print("""
1. Open WhatsApp on your phone

2. Send a message to: +14155238886

3. The EXACT message format:
   
   join [SANDBOX-CODE]
   
   Where [SANDBOX-CODE] is one of these (or check your Twilio console):
   
   - ancient-space
   - ancient-science  
   - lucky-forest
   - bright-mountain
   - green-universe
   - silver-spring
   - golden-sun
   - purple-mountain
   
   Twilio will tell you which one is correct!

4. Send the message and wait for confirmation

5. Once confirmed, run: python send_whatsapp_test.py
""")
    
    print("-"*70)
    print("📋 ALTERNATIVE METHOD (More Reliable):")
    print("-"*70)
    
    print("""
If the join codes above don't work:

1. Go to: https://console.twilio.com
2. Click: Messaging menu
3. Select: Try it out
4. Look for: WhatsApp Sandbox section
5. Copy the exact sandbox code shown there
6. Send: join [COPIED-CODE] to +14155238886
""")
    
    print("-"*70)
    print("✅ WHAT HAPPENS AFTER JOINING:")
    print("-"*70)
    
    print("""
Once you successfully join:
- You'll get a confirmation message from +14155238886
- Your phone number will be registered in the sandbox
- All booking notifications will work
- Test messages will be delivered instantly
""")
    
    print("\n" + "="*70)
    print("🚀 Ready to proceed!")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"Error Type: {type(e).__name__}")
