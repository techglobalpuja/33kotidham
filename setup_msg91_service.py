#!/usr/bin/env python3
"""
MSG91 SMS Service Setup - No Trial Restrictions
"""

import requests
from app.config import settings

class MSG91Service:
    """MSG91 SMS service - works with any Indian number."""
    
    def __init__(self):
        self.api_key = settings.MSG91_API_KEY
        self.template_id = settings.MSG91_TEMPLATE_ID
        self.sender_id = settings.MSG91_SENDER_ID
        
    def send_otp(self, mobile: str, otp: str) -> bool:
        """Send OTP via MSG91 - works with any number."""
        try:
            # Clean mobile number
            if mobile.startswith('+91'):
                mobile = mobile[3:]
            elif mobile.startswith('91'):
                mobile = mobile[2:]
            
            # MSG91 OTP API
            url = "https://control.msg91.com/api/v5/otp"
            
            payload = {
                "template_id": self.template_id,
                "mobile": f"91{mobile}",
                "authkey": self.api_key,
                "otp": otp,
                "otp_expiry": 10  # 10 minutes
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ MSG91 OTP sent to {mobile}")
                return True
            else:
                print(f"❌ MSG91 failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ MSG91 error: {e}")
            return False

# MSG91 Setup Instructions
print("""
🇮🇳 MSG91 Setup (No Trial Restrictions):

1. Go to https://msg91.com/
2. Sign up (₹100 minimum recharge)
3. Create OTP template:
   - Template: "Your 33 Koti Dham OTP is ##OTP##. Valid for 10 minutes."
   - Get Template ID
4. Get API Key from dashboard
5. Add to .env:
   MSG91_API_KEY=your_api_key
   MSG91_TEMPLATE_ID=your_template_id
   MSG91_SENDER_ID=33KOTI

Benefits:
✅ Send to ANY Indian number (no verification needed)
✅ Cheaper rates (₹0.15 per SMS)
✅ Better delivery in India
✅ No trial restrictions
✅ Instant activation
""")

# Cost Comparison:
print("""
💰 Cost Comparison:
Twilio: $0.0075 per SMS (₹0.62)
MSG91: ₹0.15 per SMS (4x cheaper!)
""")

if __name__ == "__main__":
    print("MSG91 setup instructions shown above")
