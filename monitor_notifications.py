#!/usr/bin/env python
"""
Server Notification Monitor
Real-time monitoring of booking notifications (Email + WhatsApp)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from decouple import config
from datetime import datetime, timedelta
from twilio.rest import Client

# Configuration
TWILIO_ACCOUNT_SID = config("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = config("TWILIO_AUTH_TOKEN", default="")
TWILIO_WHATSAPP_NUMBER = config("TWILIO_WHATSAPP_NUMBER", default="+14155238886")
SEND_WHATSAPP_ON_BOOKING = config("SEND_WHATSAPP_ON_BOOKING", default=False, cast=bool)
SEND_EMAIL_ON_BOOKING = config("SEND_EMAIL_ON_BOOKING", default=False, cast=bool)
SEND_BOOKING_NOTIFICATIONS = config("SEND_BOOKING_NOTIFICATIONS", default=False, cast=bool)


def check_notification_config():
    """Check notification configuration."""
    print("\n" + "="*80)
    print("⚙️  NOTIFICATION CONFIGURATION")
    print("="*80)
    print(f"SEND_BOOKING_NOTIFICATIONS: {SEND_BOOKING_NOTIFICATIONS}")
    print(f"SEND_EMAIL_ON_BOOKING: {SEND_EMAIL_ON_BOOKING}")
    print(f"SEND_WHATSAPP_ON_BOOKING: {SEND_WHATSAPP_ON_BOOKING}")
    print(f"TWILIO_ACCOUNT_SID: {'✅ SET' if TWILIO_ACCOUNT_SID else '❌ NOT SET'}")
    print(f"TWILIO_AUTH_TOKEN: {'✅ SET' if TWILIO_AUTH_TOKEN else '❌ NOT SET'}")
    print(f"TWILIO_WHATSAPP_NUMBER: {TWILIO_WHATSAPP_NUMBER}")
    print("="*80 + "\n")


def check_recent_bookings(hours_back=24, limit=10):
    """Check recent bookings and their notification status."""
    print("\n" + "="*80)
    print(f"📋 RECENT BOOKINGS (Last {hours_back} hours)")
    print("="*80)
    
    db = SessionLocal()
    try:
        # Get recent bookings
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        bookings = db.query(models.Booking)\
            .filter(models.Booking.booking_date >= cutoff_time)\
            .order_by(models.Booking.booking_date.desc())\
            .limit(limit)\
            .all()
        
        if not bookings:
            print(f"📭 No bookings found in the last {hours_back} hours\n")
            return
        
        print(f"✅ Found {len(bookings)} booking(s)\n")
        
        for booking in bookings:
            print("-"*80)
            print(f"📋 Booking #{booking.id}")
            print(f"   User: {booking.user.name if booking.user else 'N/A'}")
            print(f"   Email: {booking.user.email if booking.user else 'N/A'}")
            print(f"   Mobile: {booking.mobile_number or 'N/A'}")
            print(f"   WhatsApp: {booking.whatsapp_number or 'N/A'}")
            print(f"   Status: {booking.status.upper()}")
            print(f"   Created: {booking.booking_date}")
            
            if booking.puja:
                print(f"   Puja: {booking.puja.name}")
            if booking.plan:
                print(f"   Plan: {booking.plan.name}")
        
        print("-"*80 + "\n")
        
    except Exception as e:
        print(f"❌ Error fetching bookings: {str(e)}")
    finally:
        db.close()


def check_whatsapp_messages(hours_back=24):
    """Check WhatsApp message delivery status."""
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        print("⚠️  Twilio credentials not configured - skipping WhatsApp check\n")
        return
    
    print("\n" + "="*80)
    print(f"💬 WHATSAPP MESSAGES (Last {hours_back} hours)")
    print("="*80)
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        date_after = datetime.utcnow() - timedelta(hours=hours_back)
        
        messages = client.messages.list(
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            date_sent_after=date_after,
            limit=50
        )
        
        if not messages:
            print("📭 No WhatsApp messages sent in this period\n")
            return
        
        print(f"✅ Found {len(messages)} message(s)\n")
        
        # Group by status
        status_groups = {}
        for msg in messages:
            status = msg.status
            if status not in status_groups:
                status_groups[status] = []
            status_groups[status].append(msg)
        
        # Display by status
        for status, msgs in status_groups.items():
            icon = "⏳" if status == "queued" else "✅" if status in ["sent", "delivered"] else "❌"
            print(f"{icon} {status.upper()}: {len(msgs)} message(s)")
            
            for msg in msgs[:3]:  # Show first 3 of each status
                print(f"   • To: {msg.to}")
                print(f"     SID: {msg.sid}")
                print(f"     Date: {msg.date_sent}")
                if msg.error_message:
                    print(f"     Error: {msg.error_message}")
            
            if len(msgs) > 3:
                print(f"   ... and {len(msgs) - 3} more")
            print()
        
        # Warning for queued messages
        if "queued" in status_groups:
            print("⚠️  QUEUED MESSAGES DETECTED!")
            print("   Recipients need to join the WhatsApp Sandbox:")
            print(f"   Send 'join ancient-science' to {TWILIO_WHATSAPP_NUMBER}\n")
        
    except Exception as e:
        print(f"❌ Error checking WhatsApp: {str(e)}\n")


def check_celery_tasks():
    """Check if Celery is running and processing tasks."""
    print("\n" + "="*80)
    print("🔄 CELERY WORKER STATUS")
    print("="*80)
    
    try:
        from app.celery_config import celery_app
        
        # Check active workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if not active_workers:
            print("❌ No Celery workers are running!")
            print("\n🔧 To start Celery worker:")
            print("   Windows: .\\start-worker.ps1")
            print("   Linux: celery -A app.celery_config worker --loglevel=info\n")
            return False
        
        print(f"✅ Found {len(active_workers)} active worker(s)\n")
        
        for worker_name, tasks in active_workers.items():
            print(f"Worker: {worker_name}")
            if tasks:
                print(f"   Active tasks: {len(tasks)}")
                for task in tasks[:3]:
                    print(f"   • {task['name']}")
            else:
                print(f"   Status: Idle (ready for tasks)")
        
        # Check registered tasks
        registered = inspect.registered()
        if registered:
            worker_name = list(registered.keys())[0]
            notification_tasks = [t for t in registered[worker_name] if 'notification' in t.lower()]
            if notification_tasks:
                print(f"\n✅ Notification tasks registered:")
                for task in notification_tasks:
                    print(f"   • {task}")
        
        print()
        return True
        
    except Exception as e:
        print(f"⚠️  Could not check Celery status: {str(e)}")
        print("   This is normal if Celery is not installed or not running\n")
        return False


def monitor_full_system():
    """Run full system monitoring."""
    print("\n" + "="*100)
    print(" "*30 + "📊 NOTIFICATION SYSTEM MONITOR")
    print("="*100)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check configuration
    check_notification_config()
    
    # Check if notifications are enabled
    if not SEND_BOOKING_NOTIFICATIONS:
        print("⚠️  WARNING: SEND_BOOKING_NOTIFICATIONS is FALSE")
        print("   Notifications are disabled globally!\n")
    
    if not SEND_WHATSAPP_ON_BOOKING:
        print("⚠️  WARNING: SEND_WHATSAPP_ON_BOOKING is FALSE")
        print("   WhatsApp notifications are disabled!\n")
    
    # Check Celery
    celery_running = check_celery_tasks()
    
    # Check recent bookings
    check_recent_bookings(hours_back=72, limit=10)
    
    # Check WhatsApp messages
    if SEND_WHATSAPP_ON_BOOKING:
        check_whatsapp_messages(hours_back=72)
    
    # Final recommendations
    print("\n" + "="*100)
    print("💡 RECOMMENDATIONS")
    print("="*100)
    
    issues = []
    
    if not SEND_BOOKING_NOTIFICATIONS:
        issues.append("Set SEND_BOOKING_NOTIFICATIONS=true in .env")
    
    if not SEND_WHATSAPP_ON_BOOKING:
        issues.append("Set SEND_WHATSAPP_ON_BOOKING=true in .env")
    
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
        issues.append("Configure Twilio credentials in .env")
    
    if not celery_running:
        issues.append("Start Celery worker to process notifications")
    
    if issues:
        print("\n⚠️  Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("\n✅ System appears to be configured correctly!")
        print("   If messages aren't received, check WhatsApp Sandbox opt-in")
    
    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "config":
            check_notification_config()
        elif command == "bookings":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            check_recent_bookings(hours_back=hours)
        elif command == "whatsapp":
            hours = int(sys.argv[2]) if len(sys.argv) > 2 else 24
            check_whatsapp_messages(hours_back=hours)
        elif command == "celery":
            check_celery_tasks()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python monitor_notifications.py              # Full system check")
            print("  python monitor_notifications.py config       # Check configuration")
            print("  python monitor_notifications.py bookings [hours]  # Check recent bookings")
            print("  python monitor_notifications.py whatsapp [hours]  # Check WhatsApp messages")
            print("  python monitor_notifications.py celery       # Check Celery status")
    else:
        # Full system monitoring
        monitor_full_system()
