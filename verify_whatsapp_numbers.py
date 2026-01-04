"""
Verify WhatsApp Numbers Before Sending
=======================================
This helps filter out invalid numbers to avoid 63049 errors.
"""

from app.config import settings
from twilio.rest import Client

def verify_whatsapp_numbers(phone_numbers: list) -> dict:
    """
    Check which numbers can receive WhatsApp messages.
    
    Note: Twilio doesn't have a direct "check if on WhatsApp" API,
    but we can check recent delivery patterns.
    """
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    results = {
        "valid": [],
        "invalid": [],
        "unknown": []
    }
    
    print("🔍 Checking WhatsApp Number Validity\n")
    print("=" * 70)
    
    for phone in phone_numbers:
        # Normalize phone
        normalized = phone.replace("+", "").replace("-", "").replace(" ", "")
        if not normalized.startswith("91") and len(normalized) == 10:
            normalized = "91" + normalized
        if not normalized.startswith("+"):
            normalized = "+" + normalized
        
        print(f"\n📱 Checking: {phone} → {normalized}")
        
        # Check recent message history to this number
        try:
            recent_messages = client.messages.list(
                to=f"whatsapp:{normalized}",
                limit=5
            )
            
            if recent_messages:
                # Check latest message status
                latest = recent_messages[0]
                print(f"   Latest message: {latest.sid}")
                print(f"   Status: {latest.status}")
                print(f"   Error: {latest.error_code or 'None'}")
                
                if latest.status in ["delivered", "sent", "read"]:
                    print(f"   ✅ VALID - Previously delivered successfully")
                    results["valid"].append(phone)
                elif latest.error_code == 63049:
                    print(f"   ❌ INVALID - Error 63049 (not on WhatsApp or blocked)")
                    results["invalid"].append(phone)
                elif latest.error_code:
                    print(f"   ⚠️  ERROR - Code {latest.error_code}")
                    results["invalid"].append(phone)
                else:
                    print(f"   ⏳ UNKNOWN - Check status later")
                    results["unknown"].append(phone)
            else:
                print(f"   🆕 NEW - Never messaged before")
                results["unknown"].append(phone)
                
        except Exception as e:
            print(f"   ❌ Error checking: {str(e)}")
            results["unknown"].append(phone)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Summary:")
    print(f"   ✅ Valid (will deliver): {len(results['valid'])}")
    print(f"   ❌ Invalid (will fail): {len(results['invalid'])}")
    print(f"   ⏳ Unknown (need to test): {len(results['unknown'])}")
    
    if results["valid"]:
        print(f"\n✅ Send to these numbers:")
        for phone in results["valid"]:
            print(f"   • {phone}")
    
    if results["invalid"]:
        print(f"\n❌ Skip these numbers (will get 63049):")
        for phone in results["invalid"]:
            print(f"   • {phone}")
    
    if results["unknown"]:
        print(f"\n⏳ Test with these numbers:")
        for phone in results["unknown"]:
            print(f"   • {phone}")
    
    return results


# Test with your numbers
if __name__ == "__main__":
    test_numbers = [
        "+91 9099045749",  # This one worked
        "+91 9407350770",  # Failed with 63049
        "+91 8962507486",  # Failed with 63049
        "+91 7225859454",  # Failed with 63049
    ]
    
    results = verify_whatsapp_numbers(test_numbers)
    
    print("\n\n💡 Recommendation:")
    print("Only send bulk messages to 'valid' numbers to avoid 63049 errors.")
    print("For 'unknown' numbers, send a test message first.")
