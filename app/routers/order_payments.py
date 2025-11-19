from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import schemas, models
from app.auth import get_current_active_user
from decimal import Decimal
import razorpay
from app.config import settings

router = APIRouter(prefix="/order-payments", tags=["order_payments"])

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@router.post("/create-razorpay-order")
def create_razorpay_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create Razorpay order for payment (User endpoint)."""
    # Get the order
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order payment method is online
    if order.payment_method != "online":
        raise HTTPException(
            status_code=400,
            detail="This order uses Cash on Delivery payment method"
        )
    
    # Check if payment already exists
    existing_payment = db.query(models.OrderPayment).filter(
        models.OrderPayment.order_id == order_id
    ).first()
    
    if existing_payment and existing_payment.status in ["success", "pending"]:
        return {
            "razorpay_order_id": existing_payment.razorpay_order_id,
            "amount": float(existing_payment.amount),
            "currency": existing_payment.currency,
            "order_id": order_id,
            "order_number": order.order_number
        }
    
    # Create Razorpay order
    amount_in_paise = int(order.total_amount * 100)  # Convert to paise
    
    razorpay_order = razorpay_client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "receipt": order.order_number,
        "notes": {
            "order_id": str(order_id),
            "user_id": str(current_user.id)
        }
    })
    
    # Create or update order payment record
    if existing_payment:
        existing_payment.razorpay_order_id = razorpay_order["id"]
        existing_payment.amount = order.total_amount
        existing_payment.status = "created"
    else:
        db_payment = models.OrderPayment(
            order_id=order_id,
            razorpay_order_id=razorpay_order["id"],
            amount=order.total_amount,
            currency="INR",
            status="created"
        )
        db.add(db_payment)
    
    db.commit()
    
    return {
        "razorpay_order_id": razorpay_order["id"],
        "amount": amount_in_paise,
        "currency": "INR",
        "order_id": order_id,
        "order_number": order.order_number,
        "key_id": settings.RAZORPAY_KEY_ID
    }


@router.post("/verify-payment")
def verify_razorpay_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Verify Razorpay payment and update order status (User endpoint)."""
    # Get the payment record
    payment = db.query(models.OrderPayment).filter(
        models.OrderPayment.razorpay_order_id == razorpay_order_id
    ).first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    # Get the order
    order = db.query(models.Order).filter(
        models.Order.id == payment.order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Verify signature
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Update payment record
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.status = "success"
        
        # Update order status
        order.payment_status = "success"
        order.status = "confirmed"
        
        db.commit()
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status
        }
        
    except razorpay.errors.SignatureVerificationError:
        # Update payment status to failed
        payment.status = "failed"
        order.payment_status = "failed"
        
        # Restore stock since payment failed
        for item in order.order_items:
            product = db.query(models.Product).filter(
                models.Product.id == item.product_id
            ).first()
            if product:
                product.stock_quantity += item.quantity
                product.total_sales -= item.quantity
        
        db.commit()
        
        raise HTTPException(
            status_code=400,
            detail="Payment signature verification failed"
        )


@router.get("/{order_id}/payment-status")
def get_payment_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get payment status for an order (User endpoint)."""
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    payment = db.query(models.OrderPayment).filter(
        models.OrderPayment.order_id == order_id
    ).first()
    
    return {
        "order_id": order_id,
        "order_number": order.order_number,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "order_status": order.status,
        "total_amount": float(order.total_amount),
        "payment_details": {
            "razorpay_order_id": payment.razorpay_order_id if payment else None,
            "razorpay_payment_id": payment.razorpay_payment_id if payment else None,
            "payment_status": payment.status if payment else None
        } if payment else None
    }
