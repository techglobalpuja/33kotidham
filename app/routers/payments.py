from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import razorpay
from app.database import get_db
from app import schemas, crud, models
from app.auth import get_current_active_user, get_admin_user
from app.models import User, PaymentStatus
from app.config import settings
from decimal import Decimal

router = APIRouter(prefix="/payments", tags=["payments"])

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@router.post("/create-order", response_model=schemas.PaymentResponse)
def create_payment_order(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a Razorpay payment order."""
    # Verify booking exists and belongs to user
    booking = crud.BookingCRUD.get_booking(db, payment.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user can access this booking
    if current_user.role not in ["admin", "super_admin"] and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for this booking"
        )
    
    # Check if payment already exists
    existing_payment = crud.PaymentCRUD.get_payment_by_booking(db, payment.booking_id)
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this booking"
        )
    
    try:
        # Create Razorpay order
        razorpay_order = razorpay_client.order.create({
            "amount": int(payment.amount * 100),  # Amount in paise
            "currency": "INR",
            "receipt": f"booking_{payment.booking_id}",
            "notes": {
                "booking_id": str(payment.booking_id),
                "user_id": str(current_user.id)
            }
        })
        
        # Create payment record in database
        db_payment = crud.PaymentCRUD.create_payment(
            db, payment, razorpay_order["id"]
        )
        
        return db_payment
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/verify")
def verify_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verify Razorpay payment."""
    # Get payment record
    payment = db.query(models.Payment).filter(
        models.Payment.razorpay_order_id == razorpay_order_id
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Verify booking belongs to user
    booking = crud.BookingCRUD.get_booking(db, payment.booking_id)
    if current_user.role not in ["admin", "super_admin"] and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to verify this payment"
        )
    
    try:
        # Verify signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
        
        # Update payment status
        payment_update = schemas.PaymentUpdate(
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature,
            status=PaymentStatus.SUCCESS
        )
        
        updated_payment = crud.PaymentCRUD.update_payment(db, payment.id, payment_update)
        
        # Update booking status to confirmed
        booking_update = schemas.BookingUpdate(status=models.BookingStatus.CONFIRMED)
        crud.BookingCRUD.update_booking(db, payment.booking_id, booking_update)
        
        return {"message": "Payment verified successfully", "payment_id": payment.id}
        
    except razorpay.errors.SignatureVerificationError:
        # Update payment status to failed
        payment_update = schemas.PaymentUpdate(status=PaymentStatus.FAILED)
        crud.PaymentCRUD.update_payment(db, payment.id, payment_update)
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment verification failed"
        )


@router.get("/", response_model=List[schemas.PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all payments (Admin only)."""
    return db.query(models.Payment).all()


@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payment by ID."""
    payment = crud.PaymentCRUD.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if user can access this payment
    booking = crud.BookingCRUD.get_booking(db, payment.booking_id)
    if current_user.role not in ["admin", "super_admin"] and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payment"
        )
    
    return payment


@router.get("/booking/{booking_id}", response_model=schemas.PaymentResponse)
def get_payment_by_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get payment by booking ID."""
    # Verify booking exists and user can access it
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if current_user.role not in ["admin", "super_admin"] and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payment"
        )
    
    payment = crud.PaymentCRUD.get_payment_by_booking(db, booking_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this booking"
        )
    
    return payment


@router.post("/{payment_id}/refund")
def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Refund payment (Admin only)."""
    payment = crud.PaymentCRUD.get_payment(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.SUCCESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only successful payments can be refunded"
        )
    
    try:
        # Create refund in Razorpay
        refund = razorpay_client.payment.refund(payment.razorpay_payment_id, {
            "amount": int(payment.amount * 100),  # Amount in paise
            "speed": "normal"
        })
        
        # Update payment status
        payment_update = schemas.PaymentUpdate(status=PaymentStatus.REFUNDED)
        crud.PaymentCRUD.update_payment(db, payment_id, payment_update)
        
        # Update booking status to cancelled
        booking_update = schemas.BookingUpdate(status=models.BookingStatus.CANCELLED)
        crud.BookingCRUD.update_booking(db, payment.booking_id, booking_update)
        
        return {"message": "Payment refunded successfully", "refund_id": refund["id"]}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process refund: {str(e)}"
        )
