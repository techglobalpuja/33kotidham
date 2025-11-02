# Booking Notification System Documentation

## Overview
The system automatically sends **WhatsApp** and **Email** notifications to users when their bookings are created and confirmed.

## Features Implemented

### 1. **Notification Service** (`app/services/notifications.py`)
- `send_email()` - Send email notifications via SMTP
- `send_whatsapp()` - Send WhatsApp messages via WhatsApp Business API
- `send_booking_pending_notification()` - Triggered when booking is created (PENDING status)
- `send_booking_confirmed_notification()` - Triggered when admin confirms booking

### 2. **Integration Points**

#### When Booking is Created
- **Endpoint**: `POST /api/v1/bookings/`
- **Trigger**: After booking is saved in database
- **Messages Sent**:
  - Email with booking details
  - WhatsApp message with booking details
- **Contact Info Used**: `booking.whatsapp_number`, `booking.mobile_number`, `current_user.email`, `current_user.mobile`

#### When Booking is Confirmed by Admin
- **Endpoint**: `PUT /api/v1/bookings/{booking_id}/confirm`
- **Trigger**: After admin confirms pending booking
- **Messages Sent**:
  - Email confirmation with booking details
  - WhatsApp confirmation with booking details
- **Contact Info Used**: User's email and phone from booking record

### 3. **Configuration** (`app/config.py`)

Add these environment variables to your `.env` file:

```env
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@33kotidham.com

# WhatsApp Configuration (using WhatsApp Business API)
WHATSAPP_ENABLED=true
WHATSAPP_API_URL=https://graph.instagram.com/v18.0
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
WHATSAPP_API_TOKEN=your-whatsapp-api-token

# Notification Toggles
SEND_BOOKING_NOTIFICATIONS=true
SEND_EMAIL_ON_BOOKING=true
SEND_WHATSAPP_ON_BOOKING=true
```

### 4. **Notification Format**

**Email Subject**: `Booking Received - Ref: {booking_id}` (for pending) or `Booking Confirmed! - Ref: {booking_id}` (for confirmed)

**Email Body** includes:
- Booking ID
- Status
- Booking date/time
- Puja/Temple/Plan IDs
- User details (mobile, WhatsApp, gotra)

**WhatsApp Message** includes:
- Status emoji (🙏 for pending, ✅ for confirmed)
- All booking details in formatted text
- Thank you message

### 5. **Error Handling**
- Notification errors do NOT prevent booking creation or confirmation
- Errors are logged but caught gracefully
- System continues operation even if email/WhatsApp fails

## Setup Instructions

### 1. Install Required Packages
```powershell
pip install requests
```

### 2. Configure Email (Gmail Example)
1. Enable 2-Factor Authentication on Gmail
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Add to `.env`:
   ```env
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-generated-app-password
   SMTP_FROM_EMAIL=your-email@gmail.com
   ```

### 3. Configure WhatsApp Business API
1. Get a WhatsApp Business Account
2. Request API access from Meta/Facebook
3. Generate access token
4. Add to `.env`:
   ```env
   WHATSAPP_ENABLED=true
   WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
   WHATSAPP_API_TOKEN=your-api-token
   ```

Alternatively, if using Twilio for WhatsApp, update the notification service to use Twilio's WhatsApp API.

### 4. Test Locally
Create a test script (`test_notifications.py`):
```python
from app.services.notifications import NotificationService
from app.database import SessionLocal
from app import models

db = SessionLocal()
booking = db.query(models.Booking).first()

# Test email
NotificationService.send_email(
    to_email="your-email@example.com",
    subject="Test Email",
    body="This is a test"
)

# Test WhatsApp (requires credentials configured)
NotificationService.send_whatsapp(
    phone_number="919876543210",
    message="Test WhatsApp message"
)
```

Run: `python test_notifications.py`

## Message Examples

### PENDING Status (Booking Created)
```
🙏 Booking Received 🙏

Dear Customer,

Your booking has been received!

Booking ID: 42
Status: PENDING
Booking Date: 2025-11-02 10:30:45

Puja Details:
- Puja ID: 5
- Temple ID: 2
- Plan ID: 1

User Details:
- Mobile: 8962507486
- WhatsApp: 8962507486
- Gotra: Sharma

We will confirm your booking shortly.

Thank you for choosing 33 Koti Dham!
```

### CONFIRMED Status (Booking Confirmed)
```
✅ Booking Confirmed ✅

Dear Customer,

Your booking has been confirmed!

Booking ID: 42
Status: CONFIRMED
Booking Date: 2025-11-02 10:30:45

[Same booking details...]

Thank you for choosing 33 Koti Dham!

For support: Contact our team
```

## Future Enhancements

1. **SMS Fallback**: Use MSG91 SMS if WhatsApp fails
2. **Scheduled Notifications**: Send reminders before puja date
3. **Payment Notifications**: Notify on payment success
4. **HTML Email Templates**: Use Jinja2 for rich HTML emails
5. **Message Templates**: Store templates in DB for easy editing
6. **Notification Logs**: Track all sent notifications in DB

## Troubleshooting

### Emails not sending
- Check SMTP credentials in `.env`
- Verify Gmail app password (not regular password)
- Check SMTP host/port settings
- Look for logs in terminal for detailed errors

### WhatsApp messages not sending
- Verify `WHATSAPP_ENABLED=true`
- Check API token validity
- Ensure phone number is in international format (91XXXXXXXXXX for India)
- Check WhatsApp Business API quota

### Notifications disabled
- Check `SEND_BOOKING_NOTIFICATIONS=true` in config
- Check individual toggles: `SEND_EMAIL_ON_BOOKING` and `SEND_WHATSAPP_ON_BOOKING`
