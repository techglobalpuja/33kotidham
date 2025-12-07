from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from app.auth import get_admin_user
from app.models import User
from app.services import NotificationService
import re
import logging

router = APIRouter(prefix="/bulk-whatsapp", tags=["bulk_whatsapp"])
logger = logging.getLogger(__name__)


class BulkWhatsAppRequest(BaseModel):
    phone_numbers: List[str]
    message: str
    media_url: Optional[str] = None


class BulkWhatsAppResponse(BaseModel):
    total_numbers: int
    successful: int
    failed: int
    results: List[dict]


def normalize_phone_number(phone: str) -> str:
    """
    Normalize phone number to international format.
    Handles formats like:
    - +91 97149 20830
    - 076985 92808
    - +91-9876543210
    """
    # Remove all spaces, hyphens, and other non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # If it starts with +91, keep it
    if cleaned.startswith('+91'):
        return cleaned
    
    # If it starts with 91 (without +), add +
    if cleaned.startswith('91') and len(cleaned) == 12:
        return '+' + cleaned
    
    # If it's a 10-digit number, add +91
    if len(cleaned) == 10:
        return '+91' + cleaned
    
    # If it's an 11-digit number starting with 0, remove 0 and add +91
    if len(cleaned) == 11 and cleaned.startswith('0'):
        return '+91' + cleaned[1:]
    
    # Return as-is if we can't determine the format
    return cleaned if cleaned.startswith('+') else '+91' + cleaned


@router.post("/send", response_model=BulkWhatsAppResponse)
def send_bulk_whatsapp(
    request: BulkWhatsAppRequest,
    current_user: User = Depends(get_admin_user)
):
    """
    Send WhatsApp message to multiple numbers (Admin only).
    
    Example:
    ```json
    {
        "phone_numbers": [
            "+91 97149 20830",
            "076985 92808",
            "+91 88394 08775"
        ],
        "message": "Hello! This is a test message from 33 Koti Dham.",
        "media_url": "https://api.33kotidham.in/uploads/images/example.png"
    }
    ```
    """
    if not request.phone_numbers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone numbers list cannot be empty"
        )
    
    if not request.message or len(request.message.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    logger.info(f"🔵 Bulk WhatsApp Send Request by {current_user.mobile}")
    logger.info(f"   Total numbers: {len(request.phone_numbers)}")
    logger.info(f"   Message length: {len(request.message)}")
    logger.info(f"   Media URL: {request.media_url or 'None'}")
    
    results = []
    successful = 0
    failed = 0
    
    for phone in request.phone_numbers:
        try:
            # Normalize phone number
            normalized_phone = normalize_phone_number(phone)
            
            logger.info(f"📱 Sending to {phone} (normalized: {normalized_phone})")
            
            # Send WhatsApp message
            sent = NotificationService.send_whatsapp_notification(
                phone_number=normalized_phone,
                message=request.message,
                media_url=request.media_url
            )
            
            if sent:
                successful += 1
                results.append({
                    "phone": phone,
                    "normalized": normalized_phone,
                    "status": "success",
                    "error": None
                })
                logger.info(f"✅ Sent to {normalized_phone}")
            else:
                failed += 1
                results.append({
                    "phone": phone,
                    "normalized": normalized_phone,
                    "status": "failed",
                    "error": "WhatsApp send failed"
                })
                logger.warning(f"❌ Failed to send to {normalized_phone}")
                
        except Exception as e:
            failed += 1
            error_msg = str(e)
            results.append({
                "phone": phone,
                "normalized": normalized_phone if 'normalized_phone' in locals() else phone,
                "status": "error",
                "error": error_msg
            })
            logger.error(f"❌ Error sending to {phone}: {error_msg}")
    
    logger.info(f"📊 Bulk send complete: {successful} successful, {failed} failed")
    
    return BulkWhatsAppResponse(
        total_numbers=len(request.phone_numbers),
        successful=successful,
        failed=failed,
        results=results
    )


@router.post("/test-normalize")
def test_normalize_numbers(
    phone_numbers: List[str],
    current_user: User = Depends(get_admin_user)
):
    """
    Test phone number normalization without sending messages (Admin only).
    
    Example:
    ```json
    {
        "phone_numbers": [
            "+91 97149 20830",
            "076985 92808",
            "88394 08775"
        ]
    }
    ```
    """
    results = []
    
    for phone in phone_numbers:
        normalized = normalize_phone_number(phone)
        results.append({
            "original": phone,
            "normalized": normalized
        })
    
    return {
        "total": len(phone_numbers),
        "results": results
    }
