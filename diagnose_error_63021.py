#!/usr/bin/env python3
"""Diagnose WhatsApp delivery issue - Error 63021."""

import requests
from app.config import settings

print(f"\n{'='*70}")
print(f"🔍 DIAGNOSING ERROR 63021 - CHANNEL INVALID CONTENT ERROR")
print(f"{'='*70}\n")

# Test 1: Can we reach the media URL?
print(f"✅ TEST 1: Media URL Reachability")
media_url = "https://api.33kotidham.in/uploads/pujas/72/ac4b522a-0ab6-4311-910b-5e3e041d87ed.webp"
print(f"   URL: {media_url}")
try:
    response = requests.head(media_url, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'Not specified')}")
    print(f"   Content-Length: {response.headers.get('Content-Length', 'Unknown')} bytes")
    
    if response.status_code != 200:
        print(f"   ❌ PROBLEM: URL returned {response.status_code}, not 200!")
    else:
        print(f"   ✅ URL is reachable")
        
        # Check content type
        content_type = response.headers.get('Content-Type', '').lower()
        if 'image' not in content_type:
            print(f"   ❌ PROBLEM: Not an image! Content-Type is: {content_type}")
        
        # Check file extension
        if '.webp' in media_url:
            print(f"   ⚠️  WARNING: .webp format - WhatsApp may not support it!")
            print(f"      WhatsApp supports: jpeg, jpg, png, gif, bmp")
            print(f"      Consider converting to .jpg or .png")
        
except Exception as e:
    print(f"   ❌ PROBLEM: Cannot reach URL")
    print(f"      Error: {e}")

# Test 2: Check if Sandbox token might have expired
print(f"\n✅ TEST 2: Twilio Sandbox Configuration")
print(f"   SEND_WHATSAPP_ON_BOOKING: {settings.SEND_WHATSAPP_ON_BOOKING}")
print(f"   TWILIO_ACCOUNT_SID: {'SET' if settings.TWILIO_ACCOUNT_SID else 'NOT SET'}")
print(f"   TWILIO_AUTH_TOKEN: {'SET' if settings.TWILIO_AUTH_TOKEN else 'NOT SET'}")
print(f"   TWILIO_WHATSAPP_NUMBER: {settings.TWILIO_WHATSAPP_NUMBER}")

# Test 3: Message format check
print(f"\n✅ TEST 3: WhatsApp Message Format")
test_message = """🙏 *Booking Received* 🙏

Test message with:
- Bullet points
- *Bold text*
- _Italic text_

Should this work?"""
print(f"   Message preview:")
for line in test_message.split('\n'):
    print(f"   {line}")
    
# Count characters
if len(test_message) > 4096:
    print(f"   ❌ PROBLEM: Message too long! ({len(test_message)} chars)")
else:
    print(f"   ✅ Message length OK ({len(test_message)} chars)")

# Test 4: Check sandbox opt-in status
print(f"\n✅ TEST 4: Sandbox Opt-in Status")
print(f"   ⏱️  Last opt-in: You sent 'join joy-studied' on a previous date")
print(f"   ⚠️  Twilio Sandbox sessions expire after inactivity!")
print(f"   📌 SOLUTION: Try opting in again with 'join joy-studied'")

# Test 5: Recommendations
print(f"\n{'='*70}")
print(f"📋 RECOMMENDATIONS TO FIX ERROR 63021:")
print(f"{'='*70}\n")

print(f"1. 🖼️  IMAGE FORMAT")
print(f"   Your URL uses .webp - WhatsApp may not support it")
print(f"   Action: Convert images to .jpg or .png format")
print(f"\n2. 🔄 SANDBOX RE-OPT-IN")
print(f"   Sandbox sessions expire periodically")
print(f"   Action: Send 'join joy-studied' to +14155238886 on WhatsApp")
print(f"   Wait for: '✓ You were successfully joined to the WhatsApp Sandbox'")
print(f"\n3. 🧪 TEST TEXT-ONLY MESSAGE FIRST")
print(f"   Try sending without media attachment to isolate the issue")
print(f"   If text works → problem is with media URL")
print(f"   If text fails → problem is with account/settings")
print(f"\n4. 📱 VERIFY PHONE NUMBER")
print(f"   Your test number: +918962507486")
print(f"   Make sure this number opted into sandbox AFTER image URL changes")
print(f"\n5. 🔗 TEST MEDIA URL DIRECTLY")
print(f"   Action: Try downloading from: {media_url}")
print(f"   If it downloads correctly → URL is good")
print(f"   If it fails → media server issue")
print(f"\n{'='*70}\n")
