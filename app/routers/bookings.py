from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from app.database import get_db
from app import schemas, crud
from app.auth import get_current_active_user, get_admin_user
from app.models import User, BookingStatus
from app.services import create_razorpay_order
from app.services import calculate_booking_amount, verify_razorpay_signature

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=List[schemas.BookingResponse])
def get_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's bookings."""
    # Regular users can only see their own bookings
    user_id = None if current_user.role in ["admin", "super_admin"] else current_user.id
    return crud.BookingCRUD.get_bookings(db, skip=skip, limit=limit, user_id=user_id)


@router.get("/my", response_model=List[schemas.BookingResponse])
def get_my_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current user's bookings."""
    return crud.BookingCRUD.get_bookings(db, skip=skip, limit=limit, user_id=current_user.id)


@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get booking by ID."""
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user can access this booking
    if current_user.role not in ["admin", "super_admin"] and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this booking"
        )
    
    return booking


@router.post("/", response_model=schemas.BookingResponse)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new booking."""
    # Validate puja exists
    if booking.puja_id:
        puja = crud.PujaCRUD.get_puja(db, booking.puja_id)
        if not puja:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Puja not found"
            )
    
    # Validate plan exists
    if booking.plan_id:
        plan = crud.PlanCRUD.get_plan(db, booking.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )
    
    # Validate chadawas exist (support chadawa_ids shorthand)
    chadawa_ids = booking.chadawa_ids if getattr(booking, 'chadawa_ids', None) else [c.chadawa_id for c in booking.chadawas]
    for ch_id in chadawa_ids:
        chadawa = crud.ChadawaCRUD.get_chadawa(db, ch_id)
        if not chadawa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chadawa with ID {ch_id} not found"
            )
        # If the chadawa requires a note and the client passed objects, validate note
        if chadawa.requires_note and getattr(booking, 'chadawa_ids', None) is None:
            # client used detailed objects
            # find the object
            obj = next((c for c in booking.chadawas if c.chadawa_id == ch_id), None)
            if obj is None or not obj.note:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Note is required for chadawa: {chadawa.name}"
                )
    
    return crud.BookingCRUD.create_booking(db, booking, current_user.id)


@router.put("/{booking_id}", response_model=schemas.BookingResponse)
def update_booking(
    booking_id: int,
    booking_update: schemas.BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update booking (Admin only for status updates)."""
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Only admins can update booking status and puja link
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update booking"
        )
    
    updated_booking = crud.BookingCRUD.update_booking(db, booking_id, booking_update)
    return updated_booking


@router.put("/{booking_id}/cancel")
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel booking."""
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Check if user can cancel this booking
    if current_user.role not in ["admin", "super_admin"] and booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )
    
    # Check if booking can be cancelled
    if booking.status in [BookingStatus.COMPLETED.value, BookingStatus.CANCELLED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel completed or already cancelled booking"
        )
    
    booking_update = schemas.BookingUpdate(status=BookingStatus.CANCELLED)
    crud.BookingCRUD.update_booking(db, booking_id, booking_update)
    
    return {"message": "Booking cancelled successfully"}


@router.put("/{booking_id}/confirm")
def confirm_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Confirm booking (Admin only)."""
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bookings can be confirmed"
        )
    
    booking_update = schemas.BookingUpdate(status=BookingStatus.CONFIRMED)
    crud.BookingCRUD.update_booking(db, booking_id, booking_update)
    
    return {"message": "Booking confirmed successfully"}


@router.put("/{booking_id}/complete")
def complete_booking(
    booking_id: int,
    puja_link: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Complete booking (Admin only)."""
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status != BookingStatus.CONFIRMED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed bookings can be completed"
        )
    
    booking_update = schemas.BookingUpdate(
        status=BookingStatus.COMPLETED,
        puja_link=puja_link
    )
    crud.BookingCRUD.update_booking(db, booking_id, booking_update)
    
    return {"message": "Booking completed successfully"}


@router.post("/razorpay-booking", response_model=schemas.RazorpayBookingResponse)
def create_booking_with_razorpay(
    booking: schemas.BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new booking and Razorpay order."""
    # Normalize puja_id/plan_id: treat 0 or falsy integers as None (client may send 0)
    if getattr(booking, 'puja_id', None) in (0, ''):
        booking.puja_id = None
    if getattr(booking, 'plan_id', None) in (0, ''):
        booking.plan_id = None

    # Validate puja exists (if provided)
    if getattr(booking, 'puja_id', None):
        puja = crud.PujaCRUD.get_puja(db, booking.puja_id)
        if not puja:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Puja not found"
            )

    # Validate plan exists (if provided)
    if getattr(booking, 'plan_id', None):
        plan = crud.PlanCRUD.get_plan(db, booking.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )

    # Validate chadawas exist. Support both detailed objects (booking.chadawas)
    # and shorthand id list (booking.chadawa_ids).
    chadawa_ids = None
    if getattr(booking, 'chadawa_ids', None):
        chadawa_ids = booking.chadawa_ids
    else:
        chadawa_ids = [getattr(c, 'chadawa_id', None) for c in getattr(booking, 'chadawas', [])]

    for ch_id in chadawa_ids:
        # skip None
        if ch_id is None:
            continue
        chadawa = crud.ChadawaCRUD.get_chadawa(db, ch_id)
        if not chadawa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chadawa with ID {ch_id} not found"
            )
        # If the chadawa requires a note and client passed detailed objects, validate note
        if chadawa.requires_note and getattr(booking, 'chadawa_ids', None) is None:
            obj = next((c for c in getattr(booking, 'chadawas', []) if getattr(c, 'chadawa_id', None) == ch_id), None)
            if obj is None or not getattr(obj, 'note', None):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Note is required for chadawa: {chadawa.name}"
                )
    # Persist booking first (status PENDING), then calculate authoritative amount server-side
    db_booking = crud.BookingCRUD.create_booking(db, booking, current_user.id)
    # Calculate authoritative amount server-side using the persisted booking (safer)
    amount = calculate_booking_amount(db, db_booking)
    # Create Razorpay order
    razorpay_order = create_razorpay_order(float(amount), db_booking.id)
    payment = schemas.PaymentCreate(booking_id=db_booking.id, amount=amount)
    db_payment = crud.PaymentCRUD.create_payment(db, payment, razorpay_order["id"])
    # Return booking and Razorpay order info
    # Build a proper response object so Pydantic can serialize the booking ORM object
    response = schemas.RazorpayBookingResponse(
        booking=schemas.BookingResponse.from_orm(db_booking),
        razorpay_order_id=razorpay_order["id"],
        razorpay_order=razorpay_order,
    )
    return response


@router.post('/verify-payment')
def verify_payment(
    booking_id: int,
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verify razorpay payment signature and update payment record."""
    # Verify ownership
    booking = crud.BookingCRUD.get_booking(db, booking_id)
    if not booking or booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    valid = verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
    if not valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment signature")

    # Update payment record
    payment = crud.PaymentCRUD.get_payment_by_booking(db, booking_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.status = 'success'
    db.commit()
    db.refresh(payment)

    # Update booking status if needed
    booking_update = schemas.BookingUpdate(status=BookingStatus.CONFIRMED)
    crud.BookingCRUD.update_booking(db, booking_id, booking_update)

    return {"message": "Payment verified and booking confirmed", "payment_id": payment.id}
