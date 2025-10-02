from typing import Optional
from twilio.rest import Client
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
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
                body=f"Your puja booking #{booking_id} has been confirmed. Thank you for choosing 33 Koti Dham!",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=mobile
            )
            return True
        except Exception as e:
            print(f"SMS sending failed: {e}")
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
    """Combined notification service."""
    
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


# Global instances
notification_service = NotificationService()
