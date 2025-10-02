from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import schemas, crud
from app.auth import get_current_active_user, get_admin_user
from app.models import User, BookingStatus

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
    
    # Validate chadawas exist
    for chadawa_data in booking.chadawas:
        chadawa = crud.ChadawaCRUD.get_chadawa(db, chadawa_data.chadawa_id)
        if not chadawa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chadawa with ID {chadawa_data.chadawa_id} not found"
            )
        
        # Check if note is required
        if chadawa.requires_note and not chadawa_data.note:
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
