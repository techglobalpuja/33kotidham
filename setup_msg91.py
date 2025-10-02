#!/usr/bin/env python3
"""
Setup script for MSG91 SMS service (Indian SMS provider)
"""

import requests
from app.config import settings

class MSG91Service:
    """MSG91 SMS service for Indian numbers."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.msg91.com/api/v5"
    
    def send_otp(self, mobile: str, otp: str) -> bool:
        """Send OTP via MSG91."""
        try:
            # Remove +91 prefix if present
            if mobile.startswith('+91'):
                mobile = mobile[3:]
            elif mobile.startswith('91'):
                mobile = mobile[2:]
            
            url = f"{self.base_url}/otp"
            
            payload = {
                "template_id": "YOUR_TEMPLATE_ID",  # Get from MSG91 dashboard
                "mobile": f"91{mobile}",
                "authkey": self.api_key,
                "otp": otp
            }
            
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                print(f"✅ MSG91 SMS sent successfully to {mobile}")
                return True
            else:
                print(f"❌ MSG91 SMS failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ MSG91 error: {e}")
            return False

# Instructions for MSG91 setup
print("""
🇮🇳 MSG91 Setup Instructions:

1. Go to https://msg91.com/
2. Sign up for free account
3. Get API Key from dashboard
4. Create OTP template
5. Add to .env file:
   MSG91_API_KEY=your_api_key_here
   MSG91_TEMPLATE_ID=your_template_id_here

MSG91 Benefits:
✅ No trial restrictions
✅ Good delivery rates in India
✅ Cheaper than Twilio for Indian numbers
✅ No number verification required
""")

if __name__ == "__main__":
    print("MSG91 setup guide displayed above")
