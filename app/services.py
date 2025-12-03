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
from datetime import datetime

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

    For PUJA bookings:
    - plan.actual_price (if plan_id provided)
    - sum of selected chadawa prices

    For TEMPLE bookings:
    - ONLY sum of selected chadawa prices (NO plan price)

    Returns Decimal total amount (INR)
    """
    total = Decimal('0')

    # Check if this is a temple booking (temple_id set, puja_id not set)
    temple_id = getattr(booking, 'temple_id', None)
    puja_id = getattr(booking, 'puja_id', None)
    is_temple_booking = temple_id and not puja_id

    # Plan price: only include for PUJA bookings, NOT for temple bookings
    if not is_temple_booking:
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
        puja_name = booking.puja.name if booking.puja else "N/A"
        plan_name = booking.plan.name if booking.plan else "N/A"
        
        details = f"""
Booking ID: {booking.id}
Status: {booking.status.upper()}
Booking Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M:%S') if booking.booking_date else 'N/A'}

Puja Details:
- Puja: {puja_name}
- Plan: {plan_name}

User Details:
- Mobile: {booking.mobile_number or 'N/A'}
- WhatsApp: {booking.whatsapp_number or 'N/A'}
- Gotra: {booking.gotra or 'N/A'}

Thank you for booking with us!
"""
        return details.strip()
    
    @staticmethod
    def format_booking_details_whatsapp(booking) -> str:
        """Format booking details for WhatsApp message with emojis, pricing and images."""
        from datetime import datetime
        
        try:
            puja_name = booking.puja.name if booking.puja else "N/A"
        except:
            puja_name = "N/A"
            
        try:
            plan_name = booking.plan.name if booking.plan else "N/A"
        except:
            plan_name = "N/A"
        
        # Extract temple name (for temple bookings)
        try:
            temple_name = booking.temple.name if booking.temple else "N/A"
        except:
            temple_name = "N/A"
            
        try:
            temple_address = booking.puja.temple_address if booking.puja else "N/A"
        except:
            temple_address = "N/A"
            
        try:
            puja_date = booking.puja.date if booking.puja else "N/A"
        except:
            puja_date = "N/A"
            
        try:
            puja_time = booking.puja.time if booking.puja else "N/A"
        except:
            puja_time = "N/A"
        
        # Format time to 12-hour IST format
        if puja_time and puja_time != "N/A":
            try:
                if isinstance(puja_time, str):
                    time_obj = datetime.strptime(puja_time, "%H:%M:%S").time()
                else:
                    time_obj = puja_time
                puja_time = datetime.combine(datetime.today(), time_obj).strftime("%I:%M %p") + " IST"
            except:
                puja_time = f"{puja_time} IST"
        else:
            puja_time = "N/A"
        
        # Get plan pricing
        plan_price = "0"
        try:
            if booking.plan:
                plan_price = booking.plan.discounted_price if booking.plan.discounted_price else booking.plan.actual_price
        except:
            plan_price = "0"
        
        # Calculate chadawa prices and details
        chadawa_details = ""
        chadawa_total = 0
        try:
            if booking.booking_chadawas and len(booking.booking_chadawas) > 0:
                chadawa_details = "\n🎁 *Selected Offerings(chadawas):*\n"
                for bc in booking.booking_chadawas:
                    try:
                        chadawa = bc.chadawa if hasattr(bc, 'chadawa') else bc.get('chadawa') if isinstance(bc, dict) else None
                        if chadawa:
                            chadawa_name = chadawa.name if hasattr(chadawa, 'name') else chadawa.get('name')
                            chadawa_price = float(chadawa.price if hasattr(chadawa, 'price') else chadawa.get('price', 0))
                            chadawa_details += f"   • {chadawa_name}: ₹{chadawa_price}\n"
                            chadawa_total += chadawa_price
                    except Exception as e:
                        print(f"⚠️ Error parsing chadawa: {e}")
                        continue
        except Exception as e:
            print(f"⚠️ Error processing chadawas: {e}")
        # Calculate total price
        try:
            plan_price_float = float(plan_price)
        except:
            plan_price_float = 0
        
        # For temple bookings: only chadawa total (no plan)
        # For puja bookings: plan + chadawas
        is_temple_booking = booking.temple and not booking.puja
        if is_temple_booking:
            total_price = chadawa_total
        else:
            total_price = plan_price_float + chadawa_total
        
        # Get first puja image URL
        puja_image = ""
        try:
            if booking.puja and booking.puja.images:
                img_url = booking.puja.images[0].image_url if booking.puja.images else ""
                if img_url:
                    puja_image = NotificationService._normalize_image_url(img_url)
        except:
            pass
        
        # Build puja/temple section and pricing section
        puja_details_section = ""
        pricing_section = ""
        
        # For temple bookings (has temple but no puja)
        if booking.temple and not booking.puja:
            puja_details_section = f"""
🛕 *Temple Details:*
   *Temple:* {temple_name}
   📍 *Location:* {booking.temple.location if booking.temple and booking.temple.location else 'N/A'}
"""
            # Temple booking: show chadawas with total on new line
            pricing_section = f"""{chadawa_details}   *Total:* ₹{total_price}"""
        # For puja bookings (has puja)
        elif booking.puja:
            # Check if puja details are all N/A
            if not (puja_name == "N/A" and temple_address == "N/A" and puja_date == "N/A" and puja_time == "N/A"):
                puja_details_section = f"""
🙏 *Puja Details:*
   *Name:* {puja_name}
   *Plan:* {plan_name}
   📍 *Location:* {temple_address}
   📅 *Puja Date:* {puja_date}
   ⏰ *Puja Time:* {puja_time}
"""
            # Puja booking: show plan + chadawas pricing
            pricing_section = f"""💰 *Pricing:*
   *Plan Price:* ₹{plan_price}{chadawa_details}   *Total:* ₹{total_price}"""
        
        details = f"""🙏 Booking Received 🙏

📋 *Booking Reference:* #{booking.id}
✅ *Status:* {booking.status.upper()}
📅 *Booking Created:* {booking.booking_date.strftime('%d-%m-%Y %H:%M') if booking.booking_date else 'N/A'}{puja_details_section}
{pricing_section}

👤 *Your Details:*
   *Gotra:* {booking.gotra or 'N/A'}
   *Mobile:* {booking.mobile_number or 'N/A'}

🙏 Thank you for choosing 33 Koti Dham! 🙏
"""
        
        return details.strip()
    
    @staticmethod
    def _normalize_image_url(url: str) -> str:
        """Normalize image URL by adding base URL if needed."""
        if not url:
            return ""
        if url.startswith("/uploda") or url.startswith("/uploads"):
            return f"https://api.33kotidham.in{url}"
        if url.startswith("http"):
            return url
        return f"https://api.33kotidham.in/{url}"
    
    @staticmethod
    def _calculate_booking_total(booking) -> float:
        """Calculate total booking amount including plan and all chadawas."""
        try:
            plan_price = float(booking.plan.discounted_price if booking.plan and booking.plan.discounted_price else booking.plan.actual_price if booking.plan else 0)
        except:
            plan_price = 0
        
        chadawa_total = 0
        try:
            if booking.booking_chadawas and len(booking.booking_chadawas) > 0:
                for bc in booking.booking_chadawas:
                    try:
                        chadawa = bc.chadawa if hasattr(bc, 'chadawa') else bc.get('chadawa') if isinstance(bc, dict) else None
                        if chadawa:
                            price = float(chadawa.price if hasattr(chadawa, 'price') else chadawa.get('price', 0))
                            chadawa_total += price
                    except Exception as e:
                        print(f"⚠️ Error parsing chadawa price: {e}")
                        continue
        except Exception as e:
            print(f"⚠️ Error calculating chadawa total: {e}")
        
        return plan_price + chadawa_total
    
    @staticmethod
    def _format_chadawa_html_for_email(booking) -> str:
        """Format chadawas as HTML rows for email."""
        if not booking.booking_chadawas or len(booking.booking_chadawas) == 0:
            return ""
        
        html = '<div style="margin: 10px 0;"><strong>   🎁 Selected Offerings:</strong><br>'
        try:
            for bc in booking.booking_chadawas:
                try:
                    chadawa = bc.chadawa if hasattr(bc, 'chadawa') else bc.get('chadawa') if isinstance(bc, dict) else None
                    if chadawa:
                        chadawa_name = chadawa.name if hasattr(chadawa, 'name') else chadawa.get('name')
                        chadawa_price = float(chadawa.price if hasattr(chadawa, 'price') else chadawa.get('price', 0))
                        html += f"<div style='display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #e8e8e8; font-size: 14px;'>"
                        html += f"<span style='padding-left: 15px;'>• {chadawa_name}</span>"
                        html += f"<span>₹{chadawa_price}</span>"
                        html += f"</div>"
                except Exception as e:
                    print(f"⚠️ Error formatting chadawa row: {e}")
                    continue
        except Exception as e:
            print(f"⚠️ Error processing chadawas for HTML: {e}")
        
        html += "</div>"
        return html
    
    @staticmethod
    def format_booking_details_email(booking) -> str:
        """Format booking details for email with HTML styling, pricing and images."""
        puja_name = booking.puja.name if booking.puja else "N/A"
        plan_name = booking.plan.name if booking.plan else "N/A"
        temple_address = booking.puja.temple_address if booking.puja else "N/A"
        puja_date = booking.puja.date if booking.puja else "N/A"
        puja_time = booking.puja.time if booking.puja else "N/A"
        
        # Get pricing
        plan_actual = booking.plan.actual_price if booking.plan else "0"
        plan_discount = booking.plan.discounted_price if booking.plan and booking.plan.discounted_price else plan_actual
        
        # Get puja image
        puja_image = ""
        if booking.puja and booking.puja.temple_image_url:
            puja_image = NotificationService._normalize_image_url(booking.puja.temple_image_url)
        
        # Build image HTML
        image_html = ""
        if puja_image:
            image_html = f"""
            <div style="margin: 20px 0; text-align: center;">
                <img src="{puja_image}" alt="{puja_name}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            </div>
            """
        
        # Get all puja images if available
        puja_images_html = ""
        if booking.puja and booking.puja.images and len(booking.puja.images) > 0:
            puja_images_html = "<div style='margin: 15px 0;'><h4 style='color: #8B4513; margin-bottom: 10px;'>📸 Puja Gallery:</h4>"
            puja_images_html += "<div style='display: flex; gap: 10px; flex-wrap: wrap;'>"
            for img in booking.puja.images[:4]:  # Show first 4 images
                if img.image_url:
                    normalized_url = NotificationService._normalize_image_url(img.image_url)
                    puja_images_html += f"<img src='{normalized_url}' alt='Puja' style='max-width: 150px; height: 120px; object-fit: cover; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);'>"
            puja_images_html += "</div></div>"
        
        html = f"""
<div style="font-family: Arial, sans-serif; color: #333; background-color: #fafafa; padding: 20px;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        
        <div style="background: linear-gradient(135deg, #8B4513 0%, #D2691E 100%); padding: 20px; text-align: center; color: white;">
            <h2 style="margin: 0; font-size: 24px;">� Booking Received</h2>
            <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.9;">Reference: #{booking.id}</p>
        </div>
        
        <div style="padding: 25px;">
            <p style="font-size: 16px; margin: 0 0 20px 0;">Dear Valued Customer,</p>
            
            <p>Thank you for your booking with <strong>33 Koti Dham</strong>! Your puja booking has been received and is pending confirmation.</p>
            
            {image_html}
            
            <div style="background-color: #fff8f0; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #8B4513;">
                <h4 style="color: #8B4513; margin-top: 0;">🙏 Puja Details</h4>
                <p style="margin: 8px 0;"><strong>Puja Name:</strong> {puja_name}</p>
                <p style="margin: 8px 0;"><strong>Plan:</strong> {plan_name}</p>
                <p style="margin: 8px 0;"><strong>Location:</strong> {temple_address}</p>
                <p style="margin: 8px 0;"><strong>Puja Date:</strong> {puja_date}</p>
                <p style="margin: 8px 0;"><strong>Puja Time:</strong> {puja_time}</p>
            </div>
            
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #4169E1;">
                <h4 style="color: #4169E1; margin-top: 0;">💰 Pricing Details</h4>
                <div style="display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e0e0e0;">
                    <span><strong>Plan:</strong></span>
                    <span>₹{plan_discount}</span>
                </div>
                {NotificationService._format_chadawa_html_for_email(booking)}
                <div style="display: flex; justify-content: space-between; padding: 8px 0; color: #4CAF50; font-size: 18px; font-weight: bold;">
                    <span><strong>Total Amount:</strong></span>
                    <span>₹{NotificationService._calculate_booking_total(booking)}</span>
                </div>
            </div>
            
            <div style="background-color: #fffacd; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #FFD700;">
                <h4 style="color: #8B4513; margin-top: 0;">👤 Your Details</h4>
                <p style="margin: 8px 0;"><strong>Gotra:</strong> {booking.gotra or 'N/A'}</p>
                <p style="margin: 8px 0;"><strong>Mobile:</strong> {booking.mobile_number or 'N/A'}</p>
                <p style="margin: 8px 0;"><strong>WhatsApp:</strong> {booking.whatsapp_number or 'N/A'}</p>
                <p style="margin: 8px 0;"><strong>Booking Status:</strong> <span style="color: #FF6347; font-weight: bold;">PENDING</span></p>
            </div>
            
            {puja_images_html}
            
            <div style="background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #2196F3;">
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>Further puja details will be shared with you</li>
                </ul>
            </div>
            
            <p style="color: #666; font-size: 14px; margin-top: 25px; text-align: center;">
                <strong>33 Koti Dham Team</strong><br>
                Bringing Divine Blessings to Your Home 🙏
            </p>
        </div>
    </div>
</div>
"""
        return html

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
        print(f"\n🔵 SEND_WHATSAPP_NOTIFICATION CALLED")
        print(f"   Phone: {phone_number}")
        print(f"   Message length: {len(message)}")
        print(f"   Media URL: {media_url}")
        
        if not settings.SEND_WHATSAPP_ON_BOOKING:
            print(f"🔴 SEND_WHATSAPP_ON_BOOKING = False, returning False")
            return False

        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            print(f"🔴 Twilio credentials not configured")
            return False

        try:
            print(f"🟢 Initializing Twilio client...")
            # Initialize Twilio client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            # Normalize phone number
            phone = phone_number.replace("+", "").replace("-", "").replace(" ", "")
            if not phone.startswith("91") and len(phone) == 10:  # Indian number without country code
                phone = "91" + phone
            
            # Ensure it starts with +
            if not phone.startswith("+"):
                phone = "+" + phone

            print(f"📤 Twilio WhatsApp Send Details:")
            print(f"   From: whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}")
            print(f"   To: whatsapp:{phone}")
            print(f"   Has Media: {bool(media_url)}")
            print(f"   Message Length: {len(message)}")

            # Send via Twilio WhatsApp using sandbox number
            try:
                if media_url:
                    print(f"📸 Sending WhatsApp WITH media attachment...")
                    # Send message with media attachment
                    msg = client.messages.create(
                        body=message,
                        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                        to=f"whatsapp:{phone}",
                        media_url=[media_url]
                    )
                else:
                    print(f"📝 Sending WhatsApp TEXT ONLY (no media)...")
                    # Send text-only message
                    msg = client.messages.create(
                        body=message,
                        from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
                        to=f"whatsapp:{phone}"
                    )
                
                print(f"✅ Twilio API Response:")
                print(f"   Message SID: {msg.sid}")
                print(f"   Status: {msg.status}")
                print(f"🟢 RETURNING TRUE\n")
                return True
                
            except Exception as twilio_err:
                print(f"🔴 Twilio API Error: {str(twilio_err)}")
                print(f"   Error Type: {type(twilio_err).__name__}")
                raise  # Re-raise to outer exception handler
                
        except Exception as e:
            print(f"🔴 FAILED to send WhatsApp message")
            print(f"   Phone: {phone_number}")
            print(f"   Exception: {str(e)}")
            print(f"   Exception Type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            print(f"🔴 RETURNING FALSE\n")
            return False

    @staticmethod
    def send_booking_pending_notification(booking, user_email: str, user_phone: str) -> dict:
        """Send notification when booking is created (PENDING status)."""
        print(f"\n{'='*70}")
        print(f"🔔 NOTIFICATION SERVICE - PENDING NOTIFICATION")
        print(f"{'='*70}")
        print(f"📋 Booking ID: {booking.id}")
        print(f"👤 Email: {user_email}")
        print(f"📱 Phone (Raw): '{user_phone}'")
        print(f"📱 Phone (Type): {type(user_phone)}")
        print(f"📱 Phone (Bool): {bool(user_phone)}")
        print(f"📱 Phone (Len): {len(str(user_phone)) if user_phone else 0}")
        
        if not settings.SEND_BOOKING_NOTIFICATIONS:
            print(f"⚠️ Booking notifications DISABLED in settings")
            return {"email_sent": False, "whatsapp_sent": False}

        print(f"✅ Booking notifications ENABLED")
        print(f"✅ SEND_WHATSAPP_ON_BOOKING: {settings.SEND_WHATSAPP_ON_BOOKING}")
        print(f"✅ TWILIO_ACCOUNT_SID: {'SET' if settings.TWILIO_ACCOUNT_SID else 'NOT SET'}")
        print(f"🛕 Temple: {booking.temple if hasattr(booking, 'temple') else None}")
        print(f"🛕 Puja: {booking.puja}")
        print(f"📋 Plan: {booking.plan}")

        # Email notification with enhanced details
        email_subject = f"🙏 Booking Received - Ref: {booking.id} | 33 Koti Dham"
        puja_name = booking.puja.name if booking.puja else "Puja"
        
        email_body = f"""Dear Customer,

Thank you for your booking with 33 Koti Dham!

Your booking for {puja_name} has been received and is pending confirmation.

Booking Reference: #{booking.id}
Status: PENDING

We will confirm your booking shortly and send you further details.

Best regards,
33 Koti Dham Team
"""
        
        email_html = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: #8B4513; text-align: center;">🙏 Booking Received</h2>
        
        <p>Dear Customer,</p>
        
        <p>Thank you for your booking with <strong>33 Koti Dham</strong>!</p>
        
        <p>Your booking for <strong>{puja_name}</strong> has been received and is pending confirmation.</p>
        
        {NotificationService.format_booking_details_email(booking)}
        
        <div style="background-color: #e8f4f8; padding: 15px; border-left: 4px solid #2196F3; margin: 20px 0;">
            <p style="margin: 0;"><strong>Next Steps:</strong></p>
            <p style="margin: 10px 0 0 0;">We will confirm your booking shortly and send you further details via email and WhatsApp.</p>
        </div>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px;">
            Best regards,<br>
            <strong>33 Koti Dham Team</strong><br>
            Bringing Divine Blessings to Your Home
        </p>
    </div>
</body>
</html>"""
        
        # Email notifications are temporarily disabled per request - only WhatsApp will be sent
        email_sent = False
        print(f"✉️ Email sending skipped for booking {booking.id} (WhatsApp-only mode)")
        email_sent = False

        # WhatsApp notification with enhanced details
        whatsapp_sent = False
        try:
            print(f"💬 Building WhatsApp message...")
            print(f"💬 User phone for WhatsApp: '{user_phone}'")
            
            if not user_phone or user_phone.strip() == "":
                print(f"⚠️ SKIPPING WHATSAPP: No valid phone number provided")
                print(f"   user_phone value: '{user_phone}'")
                whatsapp_sent = False
            else:
                print(f"✅ Phone number valid, proceeding with WhatsApp")
                
                # Check if this is a temple booking (temple_id set, puja_id not set)
                is_temple_booking = hasattr(booking, 'temple') and booking.temple and not booking.puja
                
                # Try using WhatsApp templates first (production)
                template_sent = False
                try:
                    from whatsapp_template_sender import WhatsAppTemplateSender
                    sender = WhatsAppTemplateSender()
                    
                    if is_temple_booking:
                        # Use temple booking template
                        print(f"📋 Using TEMPLE booking template")
                        template_sent = sender.send_temple_booking(
                            phone=user_phone,
                            booking_id=booking.id,
                            status="PENDING",
                            booking_date=booking.booking_date.strftime('%d-%m-%Y %H:%M') if booking.booking_date else "N/A",
                            temple_name=booking.temple.name if booking.temple else "N/A",
                            location=booking.temple.location if booking.temple and booking.temple.location else "N/A",
                            total_amount=str(NotificationService._calculate_booking_total(booking)),
                            gotra=booking.gotra or "N/A",
                            mobile=booking.mobile_number or user_phone
                        )
                    else:
                        # Use puja booking template
                        print(f"📋 Using PUJA booking template")
                        puja_date = booking.puja.date if booking.puja and booking.puja.date else "N/A"
                        puja_time_obj = booking.puja.time if booking.puja and booking.puja.time else None
                        
                        # Format time to 12-hour IST format
                        if puja_time_obj and puja_time_obj != "N/A":
                            try:
                                if isinstance(puja_time_obj, str):
                                    time_obj = datetime.strptime(puja_time_obj, "%H:%M:%S").time()
                                else:
                                    time_obj = puja_time_obj
                                puja_time = datetime.combine(datetime.today(), time_obj).strftime("%I:%M %p") + " IST"
                            except:
                                puja_time = f"{puja_time_obj} IST"
                        else:
                            puja_time = "N/A"
                        
                        plan_price = "0"
                        try:
                            if booking.plan:
                                plan_price = str(booking.plan.discounted_price if booking.plan.discounted_price else booking.plan.actual_price)
                        except:
                            plan_price = "0"
                        
                        template_sent = sender.send_booking_pending(
                            phone=user_phone,
                            booking_id=booking.id,
                            booking_date=booking.booking_date.strftime('%d-%m-%Y %H:%M') if booking.booking_date else "N/A",
                            puja_name=booking.puja.name if booking.puja else "N/A",
                            plan_name=booking.plan.name if booking.plan else "N/A",
                            location=booking.puja.temple_address if booking.puja else "N/A",
                            puja_date=str(puja_date),
                            puja_time=puja_time,
                            plan_price=plan_price,
                            total_amount=str(NotificationService._calculate_booking_total(booking)),
                            gotra=booking.gotra or "N/A",
                            mobile=booking.mobile_number or user_phone
                        )
                    
                    if template_sent:
                        print(f"✅ WhatsApp TEMPLATE sent successfully")
                        whatsapp_sent = True
                    else:
                        print(f"⚠️ Template not configured or failed, falling back to free-form message")
                        
                except Exception as template_err:
                    print(f"⚠️ Template sending failed: {template_err}")
                    print(f"   Falling back to free-form WhatsApp message")
                
                # Fallback to free-form message if template failed or not configured
                if not template_sent:
                    print(f"📝 Using free-form WhatsApp message (sandbox/fallback)")
                    whatsapp_body = NotificationService.format_booking_details_whatsapp(booking)
                    
                    # ALWAYS use this specific PNG image for WhatsApp
                    media_url = "https://api.33kotidham.in/uploads/images/b4bd9c33-d6e3-4069-b436-ef8e4c5cfaa0.png"
                    print(f"📸 Using verified WhatsApp-compatible image: {media_url}")
                    
                    print(f"📤 Calling send_whatsapp_notification...")
                    print(f"   Phone: {user_phone}")
                    print(f"   Media URL: {media_url}")
                    print(f"   Message length: {len(whatsapp_body)}")
                    
                    # Try sending with media first
                    whatsapp_sent = NotificationService.send_whatsapp_notification(user_phone, whatsapp_body, media_url=media_url)
                    
                    # If failed and media was included, retry without media
                    if not whatsapp_sent and media_url:
                        print(f"⚠️ WhatsApp with media failed, retrying WITHOUT media...")
                        whatsapp_sent = NotificationService.send_whatsapp_notification(user_phone, whatsapp_body, media_url=None)
                        if whatsapp_sent:
                            print(f"✅ WhatsApp sent successfully WITHOUT media")
                
                print(f"💬 WhatsApp final result: {'✅ SENT' if whatsapp_sent else '❌ FAILED'}")
                
        except Exception as e:
            print(f"❌ WhatsApp notification error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            whatsapp_sent = False

        print(f"{'='*70}\n")
        
        return {
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent,
            "booking_id": booking.id
        }

    @staticmethod
    def send_booking_confirmed_notification(booking, user_email: str, user_phone: str) -> dict:
        """Send notification when booking is confirmed by admin."""
        import logging
        logger = logging.getLogger(__name__)
        
        if not settings.SEND_BOOKING_NOTIFICATIONS:
            logger.info(f"Booking notifications disabled. Skipping notifications for booking {booking.id}")
            return {"email_sent": False, "whatsapp_sent": False}

        logger.info(f"🔔 Starting confirmation notification for booking #{booking.id}")

        # Email notification with enhanced details
        email_subject = f"✅ Booking Confirmed! - Ref: {booking.id} | 33 Koti Dham"
        puja_name = booking.puja.name if booking.puja else "Puja"
        
        email_body = f"""Dear Customer,

Great news! Your booking has been confirmed!

Booking Reference: #{booking.id}
Puja: {puja_name}
Status: CONFIRMED

Thank you for your trust in 33 Koti Dham!

Best regards,
33 Koti Dham Team
"""
        
        email_html = f"""<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4CAF50; text-align: center;">✅ Booking Confirmed!</h2>
        
        <p>Dear Customer,</p>
        
        <p style="color: #4CAF50; font-size: 18px;"><strong>Great news! Your booking has been confirmed.</strong></p>
        
        {NotificationService.format_booking_details_email(booking)}
        
        <div style="background-color: #c8e6c9; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
            <p style="margin: 0; color: #2e7d32;"><strong>✅ Your booking is confirmed!</strong></p>
            <p style="margin: 10px 0 0 0; color: #2e7d32;">You will receive further instructions soon via email and WhatsApp.</p>
        </div>
        
        <p style="color: #666; font-size: 12px; margin-top: 30px;">
            Best regards,<br>
            <strong>33 Koti Dham Team</strong><br>
            Bringing Divine Blessings to Your Home
        </p>
    </div>
</body>
</html>"""
        
        # Email notifications are temporarily disabled per request - only WhatsApp will be sent
        email_sent = False
        logger.info(f"✉️ Email confirmation skipped for booking {booking.id} (WhatsApp-only mode)")

        # WhatsApp notification with enhanced details
        whatsapp_sent = False
        try:
            logger.info(f"💬 Building WhatsApp confirmation message...")
            logger.info(f"💬 User phone for WhatsApp: '{user_phone}'")
            
            if not user_phone or user_phone.strip() == "":
                logger.warning(f"⚠️ SKIPPING WHATSAPP: No valid phone number provided")
                whatsapp_sent = False
            else:
                logger.info(f"✅ Phone number valid, proceeding with WhatsApp confirmation")
                
                # Check if this is a temple booking (temple_id set, puja_id not set)
                is_temple_booking = hasattr(booking, 'temple') and booking.temple and not booking.puja
                
                # Try using WhatsApp templates first (production)
                template_sent = False
                try:
                    from whatsapp_template_sender import WhatsAppTemplateSender
                    sender = WhatsAppTemplateSender()
                    
                    if is_temple_booking:
                        # Use temple booking template for confirmation
                        logger.info(f"📋 Using TEMPLE booking template for CONFIRMED status")
                        template_sent = sender.send_temple_booking(
                            phone=user_phone,
                            booking_id=booking.id,
                            status="CONFIRMED",
                            booking_date=booking.booking_date.strftime('%d-%m-%Y %H:%M') if booking.booking_date else "N/A",
                            temple_name=booking.temple.name if booking.temple else "N/A",
                            location=booking.temple.location if booking.temple and booking.temple.location else "N/A",
                            total_amount=str(NotificationService._calculate_booking_total(booking)),
                            gotra=booking.gotra or "N/A",
                            mobile=booking.mobile_number or user_phone
                        )
                    else:
                        # Use puja success template for CONFIRMED bookings
                        logger.info(f"📋 Using PUJA SUCCESS template for CONFIRMED status")
                        puja_date = booking.puja.date if booking.puja and booking.puja.date else "N/A"
                        puja_time_obj = booking.puja.time if booking.puja and booking.puja.time else None
                        
                        # Format time to 12-hour IST format
                        if puja_time_obj and puja_time_obj != "N/A":
                            try:
                                if isinstance(puja_time_obj, str):
                                    time_obj = datetime.strptime(puja_time_obj, "%H:%M:%S").time()
                                else:
                                    time_obj = puja_time_obj
                                puja_time = datetime.combine(datetime.today(), time_obj).strftime("%I:%M %p") + " IST"
                            except:
                                puja_time = f"{puja_time_obj} IST"
                        else:
                            puja_time = "N/A"
                        
                        template_sent = sender.send_booking_confirmed(
                            phone=user_phone,
                            booking_id=booking.id,
                            puja_name=booking.puja.name if booking.puja else "N/A",
                            plan_name=booking.plan.name if booking.plan else "N/A",
                            location=booking.puja.temple_address if booking.puja else "N/A",
                            puja_date=str(puja_date),
                            puja_time=puja_time,
                            total_amount=str(NotificationService._calculate_booking_total(booking))
                        )
                    
                    if template_sent:
                        logger.info(f"✅ WhatsApp CONFIRMATION template sent successfully")
                        whatsapp_sent = True
                    else:
                        logger.warning(f"⚠️ Confirmation template not configured or failed, falling back to free-form message")
                        
                except Exception as template_err:
                    logger.warning(f"⚠️ Template sending failed: {template_err}")
                    logger.info(f"   Falling back to free-form WhatsApp message")
                
                # Fallback to free-form message if template failed or not configured
                if not template_sent:
                    logger.info(f"📝 Using free-form WhatsApp confirmation message (sandbox/fallback)")
                    whatsapp_body = f"""✅ *Booking Confirmed!* ✅

{NotificationService.format_booking_details_whatsapp(booking)}

Your booking is now confirmed! 🎉

Further instructions will be sent to you shortly.

Thank you for choosing 33 Koti Dham! 🙏
"""
                    
                    # Get puja image URL for WhatsApp media attachment
                    media_url = None
                    if booking.puja and booking.puja.images:
                        img_url = booking.puja.images[0].image_url if booking.puja.images else ""
                        if img_url:
                            media_url = NotificationService._normalize_image_url(img_url)
                    
                    whatsapp_sent = NotificationService.send_whatsapp_notification(user_phone, whatsapp_body, media_url=media_url)
                    
                    # If failed and media was included, retry without media
                    if not whatsapp_sent and media_url:
                        logger.warning(f"⚠️ WhatsApp with media failed, retrying WITHOUT media...")
                        whatsapp_sent = NotificationService.send_whatsapp_notification(user_phone, whatsapp_body, media_url=None)
                        if whatsapp_sent:
                            logger.info(f"✅ WhatsApp sent successfully WITHOUT media")
                
                logger.info(f"💬 WhatsApp confirmation: {'✅ Sent' if whatsapp_sent else '❌ Failed'}")
                
        except Exception as e:
            logger.error(f"❌ WhatsApp confirmation error: {str(e)}", exc_info=True)
            whatsapp_sent = False

        return {
            "email_sent": email_sent,
            "whatsapp_sent": whatsapp_sent,
            "booking_id": booking.id
        }


# Global instances
notification_service = NotificationService()
