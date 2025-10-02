from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.database import get_db
from app import schemas, models
from app.auth import get_admin_user
from app.models import User
from decimal import Decimal

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get dashboard statistics (Admin only)."""
    
    # Total users
    total_users = db.query(func.count(models.User.id)).scalar()
    
    # Total bookings
    total_bookings = db.query(func.count(models.Booking.id)).scalar()
    
    # Total revenue (sum of successful payments)
    total_revenue = db.query(
        func.coalesce(func.sum(models.Payment.amount), 0)
    ).filter(
        models.Payment.status == models.PaymentStatus.SUCCESS.value
    ).scalar() or Decimal('0')
    
    # Pending bookings
    pending_bookings = db.query(func.count(models.Booking.id)).filter(
        models.Booking.status == models.BookingStatus.PENDING.value
    ).scalar()
    
    # Completed bookings
    completed_bookings = db.query(func.count(models.Booking.id)).filter(
        models.Booking.status == models.BookingStatus.COMPLETED.value
    ).scalar()
    
    return schemas.DashboardStats(
        total_users=total_users,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        pending_bookings=pending_bookings,
        completed_bookings=completed_bookings
    )


@router.get("/bookings/pending", response_model=List[schemas.BookingResponse])
def get_pending_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all pending bookings (Admin only)."""
    return db.query(models.Booking).filter(
        models.Booking.status == models.BookingStatus.PENDING.value
    ).offset(skip).limit(limit).all()


@router.get("/bookings/recent", response_model=List[schemas.BookingResponse])
def get_recent_bookings(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get recent bookings (Admin only)."""
    return db.query(models.Booking).order_by(
        models.Booking.created_at.desc()
    ).limit(limit).all()


@router.get("/users/recent", response_model=List[schemas.UserResponse])
def get_recent_users(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get recently registered users (Admin only)."""
    return db.query(models.User).order_by(
        models.User.created_at.desc()
    ).limit(limit).all()


@router.get("/payments/recent", response_model=List[schemas.PaymentResponse])
def get_recent_payments(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get recent payments (Admin only)."""
    return db.query(models.Payment).order_by(
        models.Payment.created_at.desc()
    ).limit(limit).all()


@router.get("/revenue/monthly")
def get_monthly_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get monthly revenue statistics (Admin only)."""
    # This is a simplified version - you might want to use more sophisticated date handling
    monthly_revenue = db.query(
        func.date_trunc('month', models.Payment.created_at).label('month'),
        func.sum(models.Payment.amount).label('revenue')
    ).filter(
        models.Payment.status == models.PaymentStatus.SUCCESS.value
    ).group_by(
        func.date_trunc('month', models.Payment.created_at)
    ).order_by('month').all()
    
    return [
        {"month": str(month), "revenue": float(revenue)}
        for month, revenue in monthly_revenue
    ]


@router.get("/bookings/status-distribution")
def get_booking_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get booking status distribution (Admin only)."""
    status_distribution = db.query(
        models.Booking.status,
        func.count(models.Booking.id).label('count')
    ).group_by(models.Booking.status).all()
    
    return [
        {"status": status, "count": count}
        for status, count in status_distribution
    ]
