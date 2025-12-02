"""
WhatsApp Template Message Sender for Production

This module handles sending WhatsApp messages using approved Content Templates.
For production WhatsApp, you MUST use pre-approved templates.
"""

from twilio.rest import Client
from app.config import settings
from typing import Dict, List, Optional
import json


class WhatsAppTemplateSender:
    """Send WhatsApp messages using Twilio Content Templates."""
    
    def __init__(self):
        if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
            raise Exception("Twilio credentials not configured")
        
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number to WhatsApp format."""
        # Remove all non-numeric characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Add country code if not present
        if not phone.startswith("91") and len(phone) == 10:
            phone = "91" + phone
        
        return f"whatsapp:+{phone}"
    
    def send_booking_pending(
        self,
        phone: str,
        booking_id: int,
        booking_date: str,
        puja_name: str,
        plan_name: str,
        location: str,
        puja_date: str,
        puja_time: str,
        plan_price: str,
        total_amount: str,
        gotra: str,
        mobile: str
    ) -> Optional[str]:
        """
        Send booking pending notification using template.
        
        Template: booking_pending_notification
        Variables: {{1}} to {{11}}
        """
        if not settings.WHATSAPP_TEMPLATE_BOOKING_PENDING:
            print("⚠️ WHATSAPP_TEMPLATE_BOOKING_PENDING not configured")
            return None
        
        try:
            to_number = self._normalize_phone(phone)
            
            # Build template variables
            content_variables = {
                "1": str(booking_id),
                "2": booking_date,
                "3": puja_name,
                "4": plan_name,
                "5": location,
                "6": puja_date,
                "7": puja_time,
                "8": plan_price,
                "9": total_amount,
                "10": gotra,
                "11": mobile
            }
            
            print(f"📤 Sending WhatsApp Template: booking_pending_notification")
            print(f"   To: {to_number}")
            print(f"   Variables: {content_variables}")
            
            message = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=to_number,
                content_sid=settings.WHATSAPP_TEMPLATE_BOOKING_PENDING,
                content_variables=json.dumps(content_variables)
            )
            
            print(f"✅ WhatsApp sent! SID: {message.sid}")
            return message.sid
            
        except Exception as e:
            print(f"❌ WhatsApp template send failed: {e}")
            return None
    
    def send_booking_confirmed(
        self,
        phone: str,
        booking_id: int,
        puja_name: str,
        plan_name: str,
        location: str,
        puja_date: str,
        puja_time: str,
        total_amount: str
    ) -> Optional[str]:
        """
        Send booking confirmed notification using template.
        
        Template: booking_confirmed_notification
        Variables: {{1}} to {{7}}
        """
        if not settings.WHATSAPP_TEMPLATE_BOOKING_CONFIRMED:
            print("⚠️ WHATSAPP_TEMPLATE_BOOKING_CONFIRMED not configured")
            return None
        
        try:
            to_number = self._normalize_phone(phone)
            
            content_variables = {
                "1": str(booking_id),
                "2": puja_name,
                "3": plan_name,
                "4": location,
                "5": puja_date,
                "6": puja_time,
                "7": total_amount
            }
            
            print(f"📤 Sending WhatsApp Template: booking_confirmed_notification")
            print(f"   To: {to_number}")
            
            message = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=to_number,
                content_sid=settings.WHATSAPP_TEMPLATE_BOOKING_CONFIRMED,
                content_variables=json.dumps(content_variables)
            )
            
            print(f"✅ WhatsApp sent! SID: {message.sid}")
            return message.sid
            
        except Exception as e:
            print(f"❌ WhatsApp template send failed: {e}")
            return None
    
    def send_temple_booking(
        self,
        phone: str,
        booking_id: int,
        status: str,
        booking_date: str,
        temple_name: str,
        location: str,
        total_amount: str,
        gotra: str,
        mobile: str
    ) -> Optional[str]:
        """
        Send temple booking notification using template.
        
        Template: temple_booking_notification
        Variables: {{1}} to {{8}}
        """
        if not settings.WHATSAPP_TEMPLATE_TEMPLE_BOOKING:
            print("⚠️ WHATSAPP_TEMPLATE_TEMPLE_BOOKING not configured")
            return None
        
        try:
            to_number = self._normalize_phone(phone)
            
            content_variables = {
                "1": str(booking_id),
                "2": status,
                "3": booking_date,
                "4": temple_name,
                "5": location,
                "6": total_amount,
                "7": gotra,
                "8": mobile
            }
            
            print(f"📤 Sending WhatsApp Template: temple_booking_notification")
            print(f"   To: {to_number}")
            
            message = self.client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=to_number,
                content_sid=settings.WHATSAPP_TEMPLATE_TEMPLE_BOOKING,
                content_variables=json.dumps(content_variables)
            )
            
            print(f"✅ WhatsApp sent! SID: {message.sid}")
            return message.sid
            
        except Exception as e:
            print(f"❌ WhatsApp template send failed: {e}")
            return None


# Test function
def test_template_sender():
    """Test the template sender with sample data."""
    sender = WhatsAppTemplateSender()
    
    print("\n" + "="*70)
    print("TESTING WHATSAPP TEMPLATE SENDER")
    print("="*70)
    
    # Test booking pending
    result = sender.send_booking_pending(
        phone="8962507486",
        booking_id=106,
        booking_date="01-12-2025 18:30",
        puja_name="Ganesh Puja",
        plan_name="Premium Plan",
        location="Siddhivinayak Temple, Mumbai",
        puja_date="15-12-2025",
        puja_time="10:00 AM IST",
        plan_price="2500",
        total_amount="3000",
        gotra="Kashyap",
        mobile="8962507486"
    )
    
    print(f"\n{'='*70}")
    print(f"Result: {result}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    test_template_sender()
