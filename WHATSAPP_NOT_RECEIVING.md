# ✅ WhatsApp Setup - Why You're Not Receiving Messages

## Current Status
Your WhatsApp notification system is **✅ FULLY CONFIGURED** and working:
- ✅ Twilio Account Active (Trial)
- ✅ SEND_WHATSAPP_ON_BOOKING = true
- ✅ SEND_BOOKING_NOTIFICATIONS = true
- ✅ Twilio WhatsApp Sandbox: **+14155238886**

## ⚠️ The Issue: Twilio Sandbox Opt-In Requirement

**Twilio uses a Sandbox for WhatsApp during trial accounts.** This sandbox requires phone numbers to explicitly opt-in before they can receive messages.

### How to Fix It (3 Simple Steps)

#### Step 1: Open WhatsApp on Your Phone
- Use the phone number where you want to receive messages
- This should be the number you added to your booking

#### Step 2: Send the Join Message
Send a message to the **Twilio Sandbox Number**: `+14155238886`

**Message to send:**
```
join ancient-science
```

**Exactly as shown above** - this is the sandbox join code.

#### Step 3: Wait for Confirmation
You should receive a confirmation message:
```
You successfully joined the Twilio Sandbox for WhatsApp
```

Once confirmed, you will start receiving all notifications!

---

## 🧪 Testing After Opt-In

After you've sent the "join" message and received confirmation:

### Create a test booking to verify:
1. Go to your booking API
2. Create a booking with:
   - Your mobile number (10 digits or with +91)
   - Your WhatsApp number (same as above)
   - Select a puja and plan

You should receive:
- 📧 Email notification with booking details
- 💬 WhatsApp message with puja details and image

### Or run this test script:

Create a file called `test_booking_notification.py`:

```python
import os
from dotenv import load_dotenv
load_dotenv()

from app.services import NotificationService
from app import models
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Your test phone number (must have opted-in to sandbox)
TEST_PHONE = os.getenv("TEST_PHONE_NUMBER", "+919XXXXXXXXX")  # Replace with your number

print(f"📱 Sending test WhatsApp notification to: {TEST_PHONE}")

# Send direct WhatsApp test
result = NotificationService.send_whatsapp_notification(
    phone_number=TEST_PHONE,
    message="""🙏 *Test WhatsApp Notification* 🙏

📋 *Booking Reference:* #12345
✅ *Status:* PENDING
📅 *Booking Created:* 02-11-2025 10:30

🙏 *Puja Details:*
   *Name:* Durga Puja
   *Plan:* Premium
   💰 *Price:* ₹5000
   📍 *Location:* 33 Koti Dham Temple
   📅 *Puja Date:* 10-11-2025
   ⏰ *Puja Time:* 06:00 PM IST

Thank you for your trust in 33 Koti Dham! 🙏
"""
)

if result:
    print("✅ Message sent successfully to Twilio!")
    print("   Message status: queued (normal for sandbox)")
    print("   Check your WhatsApp on the registered phone number")
else:
    print("❌ Failed to send message")
```

---

## 📋 Complete WhatsApp Setup Checklist

- [x] ✅ Twilio Account created and active
- [x] ✅ TWILIO_ACCOUNT_SID configured
- [x] ✅ TWILIO_AUTH_TOKEN configured
- [x] ✅ TWILIO_WHATSAPP_NUMBER set to +14155238886
- [x] ✅ SEND_WHATSAPP_ON_BOOKING = true
- [ ] ⏳ **Phone number opted-in to sandbox** (YOU ARE HERE - DO THIS STEP)
- [ ] Test WhatsApp notification received
- [ ] Test booking created and notification sent

---

## 🔍 How to Verify Opt-In Status

### Check if you've opted in:
1. Send "join ancient-science" to +14155238886
2. If you receive a confirmation message, you're opted-in ✅
3. If not, Twilio will send instructions

### After Opt-In:
- You'll receive test messages from this system
- All booking notifications will be delivered
- Test messages and production messages work the same way

---

## 💡 Important Notes

### Sandbox vs Production
- **You're currently on Twilio Sandbox** (trial account)
- Sandbox requires opt-in but is free for testing
- Production would use a business WhatsApp number (requires approval from Meta/Facebook)

### Message Timing
- Messages sent immediately (status: "queued")
- Delivery happens within seconds after opt-in
- If not opted-in, messages remain queued indefinitely

### Multiple Phone Numbers
- Each phone number must separately opt-in to the sandbox
- Send "join ancient-science" from each number that should receive messages

---

## ❓ Troubleshooting

### Still not receiving after opt-in?

1. **Verify opt-in status:**
   - Send "join ancient-science" again
   - You should get "Already joined" or a confirmation

2. **Check phone number format:**
   - Use +91 format for Indian numbers: +919876543210
   - Don't use spaces or dashes

3. **Check settings:**
   - Verify SEND_WHATSAPP_ON_BOOKING=true in .env
   - Verify SEND_BOOKING_NOTIFICATIONS=true in .env
   - Restart the application after changing .env

4. **Check booking data:**
   - Booking must have a valid mobile_number
   - mobile_number should match the opted-in phone

5. **Check logs:**
   - When creating a booking, check application logs
   - Look for "WhatsApp notification" logs
   - Should show "✅ SENT" if successful

---

## 📞 Twilio Sandbox Number Reference

**Sandbox WhatsApp Number:** `+14155238886`

**Join Code:** `ancient-science`

**Full Command to Send:** `join ancient-science`

---

## 🚀 Next Steps

1. **RIGHT NOW:** Send "join ancient-science" to +14155238886 from your phone
2. **Wait for confirmation message** (usually instant)
3. **Create a test booking** or run the test script above
4. **Verify you receive the WhatsApp notification** with booking details and image

Once you receive the first test message, all future booking notifications will work automatically! 🎉

---

**Questions?** Check the logs in your application when sending a booking - they show exactly what's happening with notifications.
