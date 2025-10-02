#!/usr/bin/env python3
"""
Test script to check SMS configuration and send test OTP
"""

from app.config import settings
from app.services import notification_service
import os

def test_sms_config():
    """Test SMS configuration and send test OTP."""
    
    print("🔍 Checking SMS Configuration...")
    print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID[:10] if settings.TWILIO_ACCOUNT_SID else 'NOT SET'}...")
    print(f"TWILIO_AUTH_TOKEN: {'SET' if settings.TWILIO_AUTH_TOKEN else 'NOT SET'}")
    print(f"TWILIO_PHONE_NUMBER: {settings.TWILIO_PHONE_NUMBER}")
    
    print("\n📱 Testing SMS Service...")
    
    # Test sending OTP
    test_mobile = "8962507486"
    test_otp = "123456"
    
    print(f"Sending test OTP {test_otp} to {test_mobile}...")
    
    success = notification_service.send_otp(test_mobile, test_otp)
    
    if success:
        print("✅ SMS sent successfully!")
    else:
        print("❌ SMS sending failed!")
    
    return success

if __name__ == "__main__":
    test_sms_config()
