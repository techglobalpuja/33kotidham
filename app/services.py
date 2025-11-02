from typing import Optional
from twilio.rest import Client
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import razorpay
from app.config import settings
from decimal import Decimal
from typing import List
from pydantic import BaseModel
from razorpay.errors import SignatureVerificationError
from app import models

class SMSService:
    """SMS service supporting both Twilio and MSG91."""
    
    def __init__(self):
        self.sms_provider = None
        self.client = None
        
        # Determine SMS provider based on configuration
        provider_choice = settings.SMS_PROVIDER.lower()
        
        print(f"🔧 SMS Provider Setting: {provider_choice}")
        
        if provider_choice == "msg91":
            self._init_msg91_only()
        elif provider_choice == "twilio":
            self._init_twilio_only()
        elif provider_choice == "auto":
            self._init_auto_selection()
        else:
            print(f"❌ Invalid SMS_PROVIDER: {provider_choice}. Use 'auto', 'twilio', or 'msg91'")
            self.sms_provider = None
    
    def _init_msg91_only(self):
        """Initialize MSG91 only."""
        if settings.MSG91_API_KEY:
            self.sms_provider = "msg91"
            print("✅ MSG91 SMS service initialized (forced)")
        else:
            print("❌ MSG91 credentials not found")
            self.sms_provider = None
    
    def _init_twilio_only(self):
        """Initialize Twilio only."""
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            self.sms_provider = "twilio"
            try:
                print(f"Initializing Twilio with Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...")
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                print("✅ Twilio client initialized (forced)")
            except Exception as e:
                print(f"❌ Failed to initialize Twilio: {e}")
                self.sms_provider = None
        else:
            print("❌ Twilio credentials not found")
            self.sms_provider = None
    
    def _init_auto_selection(self):
        """Auto-select best available SMS provider."""
        # Priority: MSG91 > Twilio (MSG91 is better for Indian numbers)
        if settings.MSG91_API_KEY:
            self.sms_provider = "msg91"
            print("✅ MSG91 SMS service initialized (auto-selected)")
        elif settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER:
            self.sms_provider = "twilio"
            try:
                print(f"Initializing Twilio with Account SID: {settings.TWILIO_ACCOUNT_SID[:10]}...")
                self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                print("✅ Twilio client initialized (auto-selected)")
            except Exception as e:
                print(f"❌ Failed to initialize Twilio: {e}")
                self.sms_provider = None
        else:
            print("❌ No SMS service configured (MSG91 or Twilio)")
            self.sms_provider = None
    
    def send_otp(self, mobile: str, otp: str) -> bool:
        """Send OTP via SMS using MSG91 or Twilio."""
        if not self.sms_provider:
            print(f"❌ SMS Service not configured. OTP for {mobile}: {otp}")
            return False
        
        if self.sms_provider == "msg91":
            return self._send_msg91_otp(mobile, otp)
        elif self.sms_provider == "twilio":
            return self._send_twilio_otp(mobile, otp)
        else:
            return False
    
    def _send_msg91_otp(self, mobile: str, otp: str) -> bool:
        """Send OTP via MSG91."""
        try:
            # Clean mobile number for MSG91
            original_mobile = mobile
            if mobile.startswith('+91'):
                mobile = mobile[3:]
            elif mobile.startswith('91'):
                mobile = mobile[2:]
            
            print(f"📱 Sending MSG91 SMS to {mobile} (original: {original_mobile})")
            print(f"🔐 OTP: {otp}")
            
            url = "https://control.msg91.com/api/v5/otp"
            
            payload = {
                "template_id": settings.MSG91_TEMPLATE_ID,
                "mobile": f"91{mobile}",
                "authkey": settings.MSG91_API_KEY,
                "otp": otp,
                "otp_expiry": 10
            }
            
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ MSG91 SMS sent successfully to {mobile}")
                print(f"📧 Request ID: {result.get('request_id', 'N/A')}")
                return True
            else:
                print(f"❌ MSG91 SMS failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ MSG91 SMS error for {mobile}: {e}")
            return False
    
    def _send_twilio_otp(self, mobile: str, otp: str) -> bool:
        """Send OTP via Twilio."""
        try:
            # Format mobile number for international format
            original_mobile = mobile
            if not mobile.startswith('+'):
                mobile = f"+91{mobile}"
            
            print(f"📱 Sending Twilio SMS to {mobile} (original: {original_mobile})")
            print(f"📞 From: {settings.TWILIO_PHONE_NUMBER}")
            print(f"🔐 OTP: {otp}")
            
            message = self.client.messages.create(
                body=f"Your 33 Koti Dham OTP is: {otp}. Valid for 10 minutes. Do not share this OTP.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=mobile
            )
            print(f"✅ Twilio SMS sent successfully to {mobile}")
            print(f"📧 Message SID: {message.sid}")
            return True
        except Exception as e:
            print(f"❌ Twilio SMS failed for {mobile}: {e}")
            return False
    
    def send_booking_confirmation(self, mobile: str, booking_id: int) -> bool:
        """Send booking confirmation SMS."""
        if not self.client:
            print(f"Booking confirmation SMS for {mobile}: Booking #{booking_id} confirmed")
            return True
        
        try:
            message = self.client.messages.create(
                body=f"Your puja booking #{booking_id} has been confirmed.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=mobile
            )
            return True
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False

def create_razorpay_order(amount, receipt_id):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    order = client.order.create({
        "amount": int(amount * 100),  # Amount in paise
        "currency": "INR",
        "receipt": str(receipt_id),
        "payment_capture": 1
    })
    return order


def calculate_booking_amount(db, booking) -> Decimal:
    """Calculate total amount for a Booking (persisted or incoming) using authoritative DB prices.

    Only includes:
    - plan.actual_price (if plan_id provided)
    - sum of selected chadawa prices (from booking_chadawas, chadawa_ids, or chadawas)

    Returns Decimal total amount (INR)
    """
    total = Decimal('0')

    # Plan price: prefer discounted_price when present, otherwise actual_price
    plan_id = getattr(booking, 'plan_id', None)
    if plan_id:
        plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
        if plan:
            price = None
            if getattr(plan, 'discounted_price', None) is not None and str(getattr(plan, 'discounted_price')).strip() != "":
                price = getattr(plan, 'discounted_price')
            elif getattr(plan, 'actual_price', None) is not None:
                price = getattr(plan, 'actual_price')

            if price is not None:
                try:
                    total += Decimal(str(price))
                except Exception:
                    pass

    # Collect chadawa ids from multiple possible shapes (persisted booking or request shapes)
    chadawa_ids = []
    if hasattr(booking, 'booking_chadawas') and booking.booking_chadawas is not None:
        for bc in booking.booking_chadawas:
            cid = getattr(bc, 'chadawa_id', None) or (bc.get('chadawa_id') if isinstance(bc, dict) else None)
            if cid:
                chadawa_ids.append(cid)

    if not chadawa_ids and getattr(booking, 'chadawa_ids', None):
        chadawa_ids = list(getattr(booking, 'chadawa_ids') or [])

    if not chadawa_ids and getattr(booking, 'chadawas', None):
        for c in getattr(booking, 'chadawas') or []:
            cid = getattr(c, 'chadawa_id', None) or (c.get('chadawa_id') if isinstance(c, dict) else None)
            if cid:
                chadawa_ids.append(cid)

    for cid in chadawa_ids:
        try:
            ch_obj = db.query(models.Chadawa).filter(models.Chadawa.id == cid).first()
        except Exception:
            ch_obj = None
        if ch_obj and getattr(ch_obj, 'price', None) is not None:
            try:
                total += Decimal(str(ch_obj.price))
            except Exception:
                pass

    return total


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify a Razorpay payment signature using the Razorpay SDK. Returns True if valid."""
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })
        return True
    except SignatureVerificationError:
        return False
    except Exception:
        # Any unexpected exception should be treated as verification failure at this layer
        return False

class EmailService:
    """Email service for sending notifications."""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email."""
        if not all([self.smtp_host, self.username, self.password]):
            print(f"Email service not configured. Email to {to_email}: {subject}")
            return True  # Return True for development
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
            
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            text = msg.as_string()
            server.sendmail(self.username, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False
    
    def send_booking_confirmation_email(self, to_email: str, user_name: str, booking_id: int) -> bool:
        """Send booking confirmation email."""
        subject = "Booking Confirmation - 33 Koti Dham"
        body = f"""
        <html>
        <body>
            <h2>Booking Confirmation</h2>
            <p>Dear {user_name},</p>
            <p>Your puja booking has been confirmed!</p>
            <p><strong>Booking ID:</strong> #{booking_id}</p>
            <p>We will notify you once your puja is scheduled.</p>
            <p>Thank you for choosing 33 Koti Dham!</p>
            <br>
            <p>Best regards,<br>33 Koti Dham Team</p>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body, is_html=True)
    
    def send_puja_completion_email(self, to_email: str, user_name: str, booking_id: int, puja_link: str) -> bool:
        """Send puja completion email with link."""
        subject = "Your Puja is Complete - 33 Koti Dham"
        body = f"""
        <html>
        <body>
            <h2>Puja Completed</h2>
            <p>Dear {user_name},</p>
            <p>Your puja (Booking ID: #{booking_id}) has been completed successfully!</p>
            {f'<p><strong>Puja Link:</strong> <a href="{puja_link}">View Puja</a></p>' if puja_link else ''}
            <p>Thank you for your devotion and for choosing 33 Koti Dham!</p>
            <br>
            <p>Best regards,<br>33 Koti Dham Team</p>
        </body>
        </html>
        """
        return self.send_email(to_email, subject, body, is_html=True)


class NotificationService:
    """Combined notification service for SMS, Email, and WhatsApp."""
    
    def __init__(self):
        self.sms_service = SMSService()
        self.email_service = EmailService()
    
    def send_otp(self, mobile: str, otp: str) -> bool:
        """Send OTP notification."""
        return self.sms_service.send_otp(mobile, otp)
    
    def send_booking_confirmation(self, user, booking_id: int) -> bool:
        """Send booking confirmation via SMS and email."""
        sms_sent = self.sms_service.send_booking_confirmation(user.mobile, booking_id)
        
        email_sent = True
        if user.email:
            email_sent = self.email_service.send_booking_confirmation_email(
                user.email, user.name, booking_id
            )
        
        return sms_sent and email_sent
    
    def send_puja_completion(self, user, booking_id: int, puja_link: Optional[str] = None) -> bool:
        """Send puja completion notification."""
        email_sent = True
        if user.email:
            email_sent = self.email_service.send_puja_completion_email(
                user.email, user.name, booking_id, puja_link or ""
            )
        
        return email_sent

    @staticmethod
    def format_booking_details(booking) -> str:
        """Format booking details for notification message."""
        details = f"""
Booking ID: {booking.id}
Status: {booking.status.upper()}
Booking Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M:%S') if booking.booking_date else 'N/A'}

Puja Details:
- Puja ID: {booking.puja_id if booking.puja_id else 'N/A'}
- Temple ID: {booking.temple_id if booking.temple_id else 'N/A'}
- Plan ID: {booking.plan_id if booking.plan_id else 'N/A'}

User Details:
- Mobile: {booking.mobile_number or 'N/A'}
- WhatsApp: {booking.whatsapp_number or 'N/A'}
- Gotra: {booking.gotra or 'N/A'}

Thank you for booking with us!
"""
        return details.strip()

    @staticmethod
    def send_email_notification(
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """Send email notification."""
        if not settings.SEND_EMAIL_ON_BOOKING or not settings.SMTP_USERNAME:
            import logging
            logging.warning(f"Email notifications disabled or not configured. Skipping email to {to_email}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email

            # Add plain text part
            msg.attach(MIMEText(body, "plain"))

            # Add HTML part if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Connect and send
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(msg)

            import logging
            logging.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            import logging
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    def send_whatsapp_notification(
        phone_number: str,
        message: str,
        media_url: Optional[str] = None
    ) -> bool:
        """Send WhatsApp message notification using Twilio WhatsApp API."""
        if not settings.SEND_WHATSAPP_ON_BOOKING:
            import logging
            logging.warning(f"WhatsApp notifications disabled. Skipping message to {phone_number}")
            return False

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            import logging
            logging.warning("Twilio credentials not configured. Skipping WhatsApp message.")
            return False

        try:
            # Initialize Twilio client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Normalize phone number
            phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
            if not phone.startswith("91") and len(phone) == 10:  # Indian number without country code
                phone = "91" + phone
            
            # Ensure it starts with +
            if not phone.startswith("+"):
                phone = "+" + phone

            # Send via Twilio WhatsApp
            msg = client.messages.create(
                body=message,
                from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
                to=f"whatsapp:{phone}"
            )

            import logging
            logging.info(f"WhatsApp message sent successfully to {phone} via Twilio (SID: {msg.sid})")
            return True
        except Exception as e:
            import logging
            logging.error(f"Failed to send WhatsApp message to {phone_number} via Twilio: {str(e)}")
            return False

    @staticmethod
    def send_booking_pending_notification(booking, user_email: str, user_phone: str) -> dict:
        """Send notification when booking is created (PENDING status)."""
        if not settings.SEND_BOOKING_NOTIFICATIONS:
            import logging
            logging.info(f"Booking notifications disabled. Skipping notifications for booking {booking.id}")
            return {"email_sent": False, "whatsapp_sent": False}

        booking_details = NotificationService.format_booking_details(booking)

        # Email notification
        email_subject = f"Booking Confirmed - Ref: {booking.id}"
        email_body = f"""Dear Customer,

Thank you for your booking with 33 Koti Dham!

Your booking has been created and is pending confirmation.

{booking_details}

We will confirm your booking shortly and send you further details.

Best regards,
33 Koti Dham Team
"""
        email_sent = NotificationService.send_email_notification(user_email, email_subject, email_body)

        # WhatsApp notification
        whatsapp_body = f"""🙏 *Booking Received* 🙏

Dear Customer,

Your booking has been received!

{booking_details}

We will confirm your booking shortly.

Thank you for choosing 33 Koti Dham!
"""
        whatsapp_sent = NotificationService.send_whatsapp_notification(user_phone, whatsapp_body)

        return {
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent,
            "booking_id": booking.id
        }

    @staticmethod
    def send_booking_confirmed_notification(booking, user_email: str, user_phone: str) -> dict:
        """Send notification when booking is confirmed by admin."""
        if not settings.SEND_BOOKING_NOTIFICATIONS:
            import logging
            logging.info(f"Booking notifications disabled. Skipping notifications for booking {booking.id}")
            return {"email_sent": False, "whatsapp_sent": False}

        booking_details = NotificationService.format_booking_details(booking)

        # Email notification
        email_subject = f"Booking Confirmed! - Ref: {booking.id}"
        email_body = f"""Dear Customer,

Great news! Your booking has been confirmed.

{booking_details}

Please keep this reference number safe for future correspondence.

If you have any questions, please don't hesitate to contact us.

Best regards,
33 Koti Dham Team
"""
        email_sent = NotificationService.send_email_notification(user_email, email_subject, email_body)

        # WhatsApp notification
        whatsapp_body = f"""✅ *Booking Confirmed* ✅

Dear Customer,

Your booking has been confirmed!

{booking_details}

Thank you for choosing 33 Koti Dham!

For support: Contact our team
"""
        whatsapp_sent = NotificationService.send_whatsapp_notification(user_phone, whatsapp_body)

        return {
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent,
            "booking_id": booking.id
        }


# Global instances
notification_service = NotificationService()
