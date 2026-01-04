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
    template_name: str  # e.g., "33koti_promo" or "puja_promp"
    template_params: Optional[List[str]] = None  # For templates with variables
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
    current_user: User = Depends(get_admin_user),
    skip_failed: bool = False
):
    """
    Send WhatsApp template message to multiple numbers (Admin only).
    
    Set skip_failed=true to automatically skip numbers that previously failed with error 63049.
    
    Example 1 - Generic Promo (33koti_promo):
    ```json
    {
        "phone_numbers": ["+91 97149 20830", "076985 92808"],
        "template_name": "33koti_promo"
    }
    ```
    
    Example 2 - Puja Specific (puja_promp):
    ```json
    {
        "phone_numbers": ["+91 97149 20830", "076985 92808"],
        "template_name": "puja_promp",
        "template_params": [
            "Participate in Baglamukhi Puja to remove all your horoscope Doshas for Prosperity and Maa Baglamukhi blessings.",
            "Remove horoscope Doshas",
            "https://www.33kotidham.com/puja/64"
        ]
    }
    ```
    
    Note: template_params maps to Meta template variables:
    - template_params[0] → {{1}} (Puja message)
    - template_params[1] → {{2}} (Benefit)  
    - template_params[2] → {{3}} (URL)
    
    Media URLs should be configured in the Meta template itself, not sent separately.
    """
    if not request.phone_numbers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone numbers list cannot be empty"
        )
    
    if not request.template_name or len(request.template_name.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template name cannot be empty"
        )
    
    # Validate template name
    valid_templates = ["33koti_promo", "puja_promp"]
    if request.template_name not in valid_templates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid template name. Must be one of: {', '.join(valid_templates)}"
        )
    
    # Validate template params for puja_promp
    if request.template_name == "puja_promp":
        if not request.template_params or len(request.template_params) != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="puja_promp template requires 3 parameters: [message, benefit, url]"
            )
    
    logger.info(f"🔵 Bulk WhatsApp Send Request by {current_user.mobile}")
    logger.info(f"   Template: {request.template_name}")
    logger.info(f"   Total numbers: {len(request.phone_numbers)}")
    logger.info(f"   Template params: {request.template_params or 'None'}")
    logger.info(f"   Media URL: {request.media_url or 'None'}")
    
    results = []
    successful = 0
    failed = 0
    
    for phone in request.phone_numbers:
        try:
            # Normalize phone number
            normalized_phone = normalize_phone_number(phone)
            print(f"\n{'='*70}")
            print(f"📱 Processing: {phone} → {normalized_phone}")
            print(f"   Template: {request.template_name}")
            print(f"{'='*70}")
            logger.info(f"📱 Sending to {phone} (normalized: {normalized_phone})")
            
            # Send WhatsApp template message
            sent = NotificationService.send_whatsapp_template(
                phone_number=normalized_phone,
                template_name=request.template_name,
                template_params=request.template_params or [],
                media_url=request.media_url
            )
            
            print(f"📊 Send result: {sent}")
            print(f"{'='*70}\n")
            
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
                    "error": "WhatsApp send failed - check server logs for details"
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
