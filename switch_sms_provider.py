#!/usr/bin/env python3
"""
SMS Provider Switching Tool for 33 Koti Dham
Easily switch between Twilio and MSG91
"""

import os
from app.config import settings
from app.services import notification_service

def show_current_provider():
    """Show currently active SMS provider."""
    print("📱 Current SMS Configuration:")
    print(f"SMS_PROVIDER setting: {settings.SMS_PROVIDER}")
    print(f"Active provider: {notification_service.sms_provider or 'None'}")
    
    if notification_service.sms_provider == "msg91":
        print("✅ MSG91 is active")
        print(f"   API Key: {settings.MSG91_API_KEY[:10] if settings.MSG91_API_KEY else 'Not set'}...")
        print(f"   Template ID: {settings.MSG91_TEMPLATE_ID or 'Not set'}")
    elif notification_service.sms_provider == "twilio":
        print("✅ Twilio is active")
        print(f"   Account SID: {settings.TWILIO_ACCOUNT_SID[:10] if settings.TWILIO_ACCOUNT_SID else 'Not set'}...")
        print(f"   Phone Number: {settings.TWILIO_PHONE_NUMBER or 'Not set'}")
    else:
        print("❌ No SMS provider active")

def test_current_provider():
    """Test current SMS provider."""
    print("\n🧪 Testing Current SMS Provider...")
    
    test_mobile = "8962507486"  # Your verified number
    test_otp = "123456"
    
    print(f"Sending test OTP {test_otp} to {test_mobile}...")
    
    success = notification_service.send_otp(test_mobile, test_otp)
    
    if success:
        print("✅ SMS test successful!")
    else:
        print("❌ SMS test failed!")
    
    return success

def switch_provider_guide():
    """Show guide for switching providers."""
    print("\n🔄 How to Switch SMS Providers:")
    print("\n1. Edit your .env file")
    print("2. Change SMS_PROVIDER value:")
    print("   - SMS_PROVIDER=auto     (smart selection)")
    print("   - SMS_PROVIDER=msg91    (force MSG91)")
    print("   - SMS_PROVIDER=twilio   (force Twilio)")
    print("3. Restart server: python run.py")
    
    print("\n💡 Provider Comparison:")
    print("┌─────────────┬─────────────┬─────────────────┬─────────────────┐")
    print("│ Provider    │ Cost/SMS    │ Best For        │ Restrictions    │")
    print("├─────────────┼─────────────┼─────────────────┼─────────────────┤")
    print("│ MSG91       │ ₹0.15       │ Indian numbers  │ None            │")
    print("│ Twilio      │ ₹0.62       │ Global numbers  │ Trial limits    │")
    print("└─────────────┴─────────────┴─────────────────┴─────────────────┘")

def check_provider_credentials():
    """Check which providers have valid credentials."""
    print("\n🔍 Checking Provider Credentials:")
    
    # Check MSG91
    if settings.MSG91_API_KEY:
        print("✅ MSG91 credentials found")
        if settings.MSG91_TEMPLATE_ID:
            print("   ✅ Template ID configured")
        else:
            print("   ⚠️ Template ID missing")
    else:
        print("❌ MSG91 credentials missing")
    
    # Check Twilio
    if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
        print("✅ Twilio credentials found")
    else:
        print("❌ Twilio credentials missing")

def main():
    """Main function."""
    print("🇮🇳 33 Koti Dham SMS Provider Manager\n")
    
    show_current_provider()
    check_provider_credentials()
    
    print("\n" + "="*50)
    
    while True:
        print("\nChoose an option:")
        print("1. Test current provider")
        print("2. Show switching guide")
        print("3. Show current status")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            test_current_provider()
        elif choice == "2":
            switch_provider_guide()
        elif choice == "3":
            show_current_provider()
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()
