# WhatsApp Production Setup Guide

## Current Status
- ✅ WhatsApp Sandbox: Working (requires "join ancient-science")
- ⏳ WhatsApp Production: Pending setup

## Why Production is Needed
- **Sandbox**: Users must manually join by sending "join ancient-science"
- **Production**: Send to ANY number without opt-in required
- **Professional**: Uses your own WhatsApp Business number

---

## Step 1: Apply for WhatsApp Business API

### 1.1 Start Application in Twilio Console
1. Login to Twilio: https://console.twilio.com/
2. Go to **Messaging** → **Senders** → **WhatsApp Senders**
3. Click **"Get started with WhatsApp"** or **"Request Access"**

### 1.2 Required Information
- **Business Name**: 33 Koti Dham
- **Business Website**: https://33kotidham.in
- **Business Description**: Digital platform for Hindu religious puja bookings and temple services
- **Use Case**: Transactional notifications for booking confirmations, updates, and reminders
- **Expected Volume**: 1000-5000 messages/month
- **Business Address**: Your registered business address
- **Business Registration**: Company registration documents

---

## Step 2: Facebook Business Manager Setup

### 2.1 Create Facebook Business Manager Account
1. Go to: https://business.facebook.com/
2. Create account with business email
3. Add **Business Name**: 33 Koti Dham
4. Add **Business Details**: Website, address, etc.

### 2.2 Link to Twilio
- Twilio will provide a link to connect your Facebook Business Manager
- Authorize Twilio to manage your WhatsApp Business Account

### 2.3 Business Verification (Required)
Facebook will verify your business using:
- Business registration documents
- Business phone number
- Business email domain
- Website verification

**⏱️ Verification Time**: 1-5 business days

---

## Step 3: Get Your WhatsApp Business Number

### Option A: Use Your Existing Number
- Port your existing WhatsApp number to WhatsApp Business API
- ⚠️ **Cannot use the same number on WhatsApp app anymore**
- Recommended: Get a NEW number

### Option B: Get New WhatsApp Business Number
1. Purchase a new phone number in Twilio
2. Request WhatsApp enablement for that number
3. Go through verification process

**Recommended**: Get a number starting with +91 (Indian number)

```bash
# In Twilio Console:
# Phone Numbers → Buy a Number → India (+91) → Buy
# Then request WhatsApp enablement for that number
```

---

## Step 4: Create Message Templates

WhatsApp requires **pre-approved templates** for outbound messages.

### 4.1 Template Categories
- **TRANSACTIONAL**: Order confirmations, booking updates (HIGH PRIORITY)
- **MARKETING**: Promotional messages (requires opt-in)
- **UTILITY**: Account updates, appointment reminders

### 4.2 Create Booking Confirmation Template

**Template Name**: `booking_pending_notification`  
**Category**: TRANSACTIONAL  
**Language**: English, Hindi (create both)  

**Body (English)**:
```
Your booking #{{1}} for {{2}} has been received and is pending confirmation.

📋 Booking Details:
Plan: {{3}}
Date: {{4}}
Amount: ₹{{5}}

Thank you for choosing 33 Koti Dham! 🙏
```

**Body (Hindi)**:
```
आपकी बुकिंग #{{1}} {{2}} के लिए प्राप्त हो गई है और पुष्टि लंबित है।

📋 बुकिंग विवरण:
योजना: {{3}}
तिथि: {{4}}
राशि: ₹{{5}}

33 कोटि धाम चुनने के लिए धन्यवाद! 🙏
```

### 4.3 Create Booking Confirmed Template

**Template Name**: `booking_confirmed_notification`  
**Category**: TRANSACTIONAL  

**Body**:
```
✅ Booking Confirmed! #{{1}}

Your puja booking for {{2}} has been confirmed.

Puja Date: {{3}}
Puja Time: {{4}}
Location: {{5}}

Further details will be shared soon. 🙏
```

### 4.4 Template Approval
- Submit templates in Twilio Console
- Facebook reviews within 24-48 hours
- Once approved, you can use them in production

---

## Step 5: Update Code for Production

### 5.1 Environment Variables

Add to `.env`:
```bash
# WhatsApp Production Settings
WHATSAPP_ENVIRONMENT=production  # or 'sandbox'
TWILIO_WHATSAPP_PRODUCTION_NUMBER=+919XXXXXXXXX  # Your approved number

# Template IDs (after approval)
WHATSAPP_TEMPLATE_BOOKING_PENDING=booking_pending_notification
WHATSAPP_TEMPLATE_BOOKING_CONFIRMED=booking_confirmed_notification
```

### 5.2 Code Changes

Update `app/services.py` to use templates:

```python
@staticmethod
def send_whatsapp_production(phone: str, template_name: str, params: list, media_url: Optional[str] = None):
    """Send WhatsApp using approved template (Production)."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    # For production, use ContentSid (template)
    message = client.messages.create(
        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_PRODUCTION_NUMBER}",
        to=f"whatsapp:{phone}",
        content_sid=template_name,  # Template ID from Twilio
        content_variables=json.dumps({"1": params[0], "2": params[1], ...})
    )
    
    return message.sid
```

---

## Step 6: Testing Production

### 6.1 Test Template
```python
# test_whatsapp_production.py
from twilio.rest import Client
import os

client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))

message = client.messages.create(
    from_='whatsapp:+919XXXXXXXXX',  # Your production number
    to='whatsapp:+918962507486',
    content_sid='HXXXXXXXXXXXXXXXXXXXXXXXXXX',  # Template SID
    content_variables='{"1":"12345","2":"Ganesh Puja","3":"Premium","4":"2024-12-15","5":"5000"}'
)

print(f"Message sent! SID: {message.sid}")
```

---

## Cost Comparison

### Sandbox (Current)
- ✅ **FREE**
- ❌ Requires user opt-in
- ❌ Sandbox message prefix

### Production
- ✅ Send to any number
- ✅ Professional
- 💰 **Cost**: ~₹0.40-0.60 per message (India)
- 💰 **Conversation-based pricing**:
  - Business-initiated: ₹0.40/conversation (24 hours)
  - User-initiated: FREE (after user replies)

**Monthly Cost Estimate**:
- 1000 bookings/month = ₹400-600/month
- Very affordable for transactional messages

---

## Timeline

| Step | Time Required | Status |
|------|---------------|--------|
| Apply for WhatsApp API | 1 day | ⏳ Not started |
| Business Verification | 1-5 days | ⏳ Pending |
| Create Templates | 1 day | ⏳ Not started |
| Template Approval | 1-2 days | ⏳ Pending |
| Get Phone Number | 1 day | ⏳ Not started |
| Code Integration | 1 day | ⏳ Not started |
| Testing | 1 day | ⏳ Not started |
| **Total** | **7-14 days** | |

---

## Quick Start Checklist

- [ ] Apply for WhatsApp Business API in Twilio Console
- [ ] Create Facebook Business Manager account
- [ ] Submit business verification documents
- [ ] Get/buy WhatsApp Business number
- [ ] Create message templates (booking_pending, booking_confirmed)
- [ ] Wait for template approval
- [ ] Update .env with production settings
- [ ] Update services.py to use templates
- [ ] Test with production number
- [ ] Deploy to production

---

## Important Notes

1. **24-Hour Window**: After user replies, you have 24 hours for free-form messages
2. **Templates Required**: First message MUST use approved template
3. **No Sandbox Prefix**: Production messages are clean (no "sandbox" prefix)
4. **Conversation Pricing**: Charged per 24-hour conversation, not per message
5. **Number Verification**: Must verify your business and phone number
6. **Message Quality**: High-quality, transactional messages only

---

## Alternative: Faster Options

If Twilio approval takes too long, consider:

### Option 1: Gupshup
- Faster approval (2-3 days)
- Popular in India
- Similar pricing

### Option 2: WATI (WhatsApp Team Inbox)
- Quick setup (1-2 days)
- Good for small businesses
- Slightly higher cost

### Option 3: MSG91 WhatsApp
- Already have MSG91 for SMS
- Can add WhatsApp
- 3-5 days approval

---

## Need Help?

1. **Twilio Support**: support@twilio.com
2. **Documentation**: https://www.twilio.com/docs/whatsapp
3. **Business Verification**: https://business.facebook.com/business/help

---

## Next Steps

1. **Start the application process in Twilio Console TODAY**
2. **Prepare business documents** (registration, website, etc.)
3. **Continue using sandbox** while production is being set up
4. **Create templates** in Twilio Console
5. **Test production** once approved

**Estimated Time to Go Live**: 7-14 days

Good luck! 🙏
