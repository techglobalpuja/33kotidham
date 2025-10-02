#!/usr/bin/env python3
"""
Test MSG91 setup and configuration
"""

import requests
from app.config import settings

def test_msg91_credentials():
    """Test MSG91 API credentials."""
    
    print("🔍 Testing MSG91 Configuration...")
    
    # Check if credentials are set
    if not settings.MSG91_API_KEY:
        print("❌ MSG91_API_KEY not found in environment")
        print("📝 Add to your .env file:")
        print("MSG91_API_KEY=your_api_key_here")
        return False
    
    print(f"✓ MSG91_API_KEY found: {settings.MSG91_API_KEY[:10]}...")
    
    # Test API connection
    try:
        url = "https://control.msg91.com/api/v5/otp/verify"
        headers = {
            "Content-Type": "application/json",
            "authkey": settings.MSG91_API_KEY
        }
        
        # Test with dummy data to check API key validity
        payload = {
            "mobile": "919999999999",
            "otp": "123456"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("✅ MSG91 API Key is valid!")
            return True
        elif response.status_code == 401:
            print("❌ MSG91 API Key is invalid")
            return False
        else:
            print(f"⚠️ MSG91 API response: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MSG91: {e}")
        return False

def check_account_balance():
    """Check MSG91 account balance."""
    try:
        url = f"https://control.msg91.com/api/balance.php?authkey={settings.MSG91_API_KEY}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            balance = response.text.strip()
            print(f"💰 MSG91 Account Balance: ₹{balance}")
            
            if float(balance) < 10:
                print("⚠️ Low balance! Add money to your MSG91 account")
            else:
                print("✅ Sufficient balance for SMS")
        else:
            print(f"❌ Could not fetch balance: {response.text}")
            
    except Exception as e:
        print(f"❌ Error checking balance: {e}")

if __name__ == "__main__":
    print("🇮🇳 MSG91 Setup Test\n")
    
    # Test credentials
    if test_msg91_credentials():
        check_account_balance()
    
    print("\n📋 Next Steps:")
    print("1. Create OTP template in MSG91 dashboard")
    print("2. Wait for template approval (1-2 hours)")
    print("3. Add MSG91_TEMPLATE_ID to .env file")
    print("4. Restart server to use MSG91")
