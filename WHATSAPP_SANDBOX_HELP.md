#!/usr/bin/env python
"""
Twilio WhatsApp Sandbox Opt-in Helper

To receive messages from Twilio's WhatsApp Sandbox, you need to:
1. Send "join [CODE]" to the sandbox number
2. The code is usually provided in your Twilio console

For the sandbox number +14155238886, you typically send:
"join {CODE}" to get added to the allowlist

This script helps you understand what needs to happen.
"""

print("\n" + "="*70)
print("📱 TWILIO WHATSAPP SANDBOX OPT-IN INSTRUCTIONS")
print("="*70)

print("""
🔧 To receive WhatsApp messages from Twilio's Sandbox:

1. Open WhatsApp on your phone
2. Send a message to +14155238886 (the Twilio Sandbox number)
3. In the message, type: join {CODE}
   (Replace {CODE} with your actual sandbox code from Twilio Console)

4. You should receive a confirmation message

5. After that, you'll be able to receive all sandbox messages

📊 Common Sandbox Codes:
   - Check your Twilio Console > Messaging > WhatsApp Sandbox
   - The format is usually "join <adjective><animal>"
   - Example: "join orange-kitten"

⚠️  Without opting in to the sandbox:
   - Messages are "queued" but never delivered
   - Status shows "queued" in logs
   - No error is returned by Twilio

✅ After opting in:
   - Messages will be delivered immediately
   - Status changes to "accepted" then "received"
   - You'll see them on your WhatsApp

For more info: https://www.twilio.com/docs/whatsapp/sandbox
""")

print("="*70)
print("Need help? Check Twilio Console > Messaging > WhatsApp Sandbox")
print("="*70 + "\n")
