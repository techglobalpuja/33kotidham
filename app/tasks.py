"""
Celery Tasks for Booking Notifications
Independent message queue system - processes one message at a time per user
"""
from app.celery_config import celery_app
from app.database import SessionLocal
from app import crud
from app.services import NotificationService
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name='app.tasks.send_booking_notification',
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True
)
def send_booking_notification(self, booking_id: int, notification_type: str):
    """
    Send booking notification asynchronously via Celery queue.
    
    This task is processed independently from the web request.
    Messages are queued and processed one by one.
    
    Args:
        booking_id: The booking ID to send notification for
        notification_type: Type of notification ('pending', 'confirmed', 'completed')
    
    Retries:
        - Max 3 retries with exponential backoff
        - 60 seconds delay between retries
        - Jitter added to prevent thundering herd
    """
    db = None
    try:
        # Create new database session for this task
        db = SessionLocal()
        
        logger.info(f"📬 Processing notification for booking {booking_id}, type: {notification_type}")
        
        # Fetch booking with user details
        booking = crud.BookingCRUD.get_booking(db, booking_id)
        if not booking:
            logger.error(f"❌ Booking {booking_id} not found")
            return {"status": "error", "message": "Booking not found"}
        
        # Get user contact information
        user = booking.user
        user_email = user.email or ""
        user_phone = booking.whatsapp_number or booking.mobile_number or getattr(user, 'mobile', None) or ""
        
        # Check if we have any contact info
        if not user_email and not user_phone:
            logger.warning(f"⚠️ No contact info for booking {booking_id}")
            return {"status": "skipped", "message": "No contact information available"}
        
        logger.info(f"📧 Email: {user_email if user_email else 'None'}")
        logger.info(f"📱 Phone: {user_phone if user_phone else 'None'}")
        
        # Send appropriate notification based on type
        result = None
        if notification_type == "pending":
            result = NotificationService.send_booking_pending_notification(
                booking,
                user_email=user_email,
                user_phone=user_phone
            )
        elif notification_type == "confirmed":
            result = NotificationService.send_booking_confirmed_notification(
                booking,
                user_email=user_email,
                user_phone=user_phone
            )
        elif notification_type == "completed":
            result = NotificationService.send_booking_completed_notification(
                booking,
                user_email=user_email,
                user_phone=user_phone
            )
        else:
            logger.error(f"❌ Unknown notification type: {notification_type}")
            return {"status": "error", "message": f"Unknown notification type: {notification_type}"}
        
        logger.info(f"✅ Notification sent successfully for booking {booking_id}")
        logger.info(f"   Result: {result}")
        
        return {
            "status": "success",
            "booking_id": booking_id,
            "notification_type": notification_type,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"❌ Error sending notification for booking {booking_id}: {str(e)}", exc_info=True)
        
        # Retry the task
        try:
            raise self.retry(exc=e)
        except self.MaxRetriesExceededError:
            logger.error(f"❌ Max retries exceeded for booking {booking_id}")
            return {
                "status": "failed",
                "booking_id": booking_id,
                "error": str(e),
                "message": "Max retries exceeded"
            }
    
    finally:
        # Always close the database session
        if db:
            db.close()


@celery_app.task(name='app.tasks.test_celery')
def test_celery():
    """Test task to verify Celery is working"""
    logger.info("✅ Celery is working!")
    return {"status": "success", "message": "Celery is working!"}
