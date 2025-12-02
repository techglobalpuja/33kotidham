from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import schemas, models
from app.auth import get_admin_user, get_current_active_user
from app.config import settings
from decimal import Decimal
from datetime import datetime
import secrets
import string

router = APIRouter(tags=["promo_codes_and_orders"])


# ==================== PROMO CODES ====================

@router.get("/promo-codes", response_model=List[schemas.PromoCodeResponse])
def get_promo_codes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Get all promo codes (Admin only)."""
    query = db.query(models.PromoCode)
    
    if is_active is not None:
        query = query.filter(models.PromoCode.is_active == is_active)
    
    promo_codes = query.offset(skip).limit(limit).all()
    return promo_codes


@router.get("/promo-codes/{promo_code_id}", response_model=schemas.PromoCodeResponse)
def get_promo_code(
    promo_code_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Get promo code by ID (Admin only)."""
    promo_code = db.query(models.PromoCode).filter(
        models.PromoCode.id == promo_code_id
    ).first()
    
    if not promo_code:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    return promo_code


@router.post("/promo-codes/validate", response_model=schemas.PromoCodeValidateResponse)
def validate_promo_code(
    validation: schemas.PromoCodeValidate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Validate promo code and calculate discount (User endpoint)."""
    promo_code = db.query(models.PromoCode).filter(
        models.PromoCode.code == validation.code.upper(),
        models.PromoCode.is_active == True
    ).first()
    
    if not promo_code:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="Invalid promo code"
        )
    
    # Check applicability
    if validation.is_product_order and not promo_code.applicable_to_products:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="This promo code is not applicable to product orders"
        )
    
    if not validation.is_product_order and not promo_code.applicable_to_pujas:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="This promo code is not applicable to puja bookings"
        )
    
    # Check validity period
    now = datetime.now()
    if promo_code.valid_from and now < promo_code.valid_from:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="This promo code is not yet valid"
        )
    
    if promo_code.valid_until and now > promo_code.valid_until:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="This promo code has expired"
        )
    
    # Check usage limits
    if promo_code.max_uses and promo_code.current_uses >= promo_code.max_uses:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="This promo code has reached its usage limit"
        )
    
    # Check per-user usage limit
    user_usage = db.query(models.Order).filter(
        models.Order.user_id == current_user.id,
        models.Order.promo_code_id == promo_code.id
    ).count()
    
    if user_usage >= promo_code.max_uses_per_user:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message="You have already used this promo code"
        )
    
    # Check minimum order amount
    if promo_code.min_order_amount and validation.order_amount < promo_code.min_order_amount:
        return schemas.PromoCodeValidateResponse(
            valid=False,
            message=f"Minimum order amount of ₹{promo_code.min_order_amount} required"
        )
    
    # Calculate discount
    discount_amount = Decimal(0)
    if promo_code.discount_type == "percentage":
        discount_amount = (validation.order_amount * promo_code.discount_value) / 100
        # Apply max discount cap if set
        if promo_code.max_discount_amount and discount_amount > promo_code.max_discount_amount:
            discount_amount = promo_code.max_discount_amount
    else:  # fixed
        discount_amount = promo_code.discount_value
    
    # Ensure discount doesn't exceed order amount
    if discount_amount > validation.order_amount:
        discount_amount = validation.order_amount
    
    final_amount = validation.order_amount - discount_amount
    
    return schemas.PromoCodeValidateResponse(
        valid=True,
        message="Promo code applied successfully",
        discount_amount=discount_amount,
        final_amount=final_amount
    )


@router.post("/promo-codes", response_model=schemas.PromoCodeResponse)
def create_promo_code(
    promo_code: schemas.PromoCodeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Create a new promo code (Admin only)."""
    # Check if code already exists
    existing = db.query(models.PromoCode).filter(
        models.PromoCode.code == promo_code.code.upper()
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Promo code with this code already exists"
        )
    
    # Validate discount type
    if promo_code.discount_type not in ["percentage", "fixed"]:
        raise HTTPException(
            status_code=400,
            detail="Discount type must be 'percentage' or 'fixed'"
        )
    
    promo_data = promo_code.dict()
    promo_data["code"] = promo_data["code"].upper()
    
    db_promo = models.PromoCode(**promo_data)
    db.add(db_promo)
    db.commit()
    db.refresh(db_promo)
    return db_promo


@router.put("/promo-codes/{promo_code_id}", response_model=schemas.PromoCodeResponse)
def update_promo_code(
    promo_code_id: int,
    promo_code: schemas.PromoCodeUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Update promo code (Admin only)."""
    db_promo = db.query(models.PromoCode).filter(
        models.PromoCode.id == promo_code_id
    ).first()
    
    if not db_promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    # Check code uniqueness if updating
    if promo_code.code and promo_code.code.upper() != db_promo.code:
        existing = db.query(models.PromoCode).filter(
            models.PromoCode.code == promo_code.code.upper()
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Promo code with this code already exists"
            )
    
    update_data = promo_code.dict(exclude_unset=True)
    if "code" in update_data:
        update_data["code"] = update_data["code"].upper()
    
    for key, value in update_data.items():
        setattr(db_promo, key, value)
    
    db.commit()
    db.refresh(db_promo)
    return db_promo


@router.delete("/promo-codes/{promo_code_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_promo_code(
    promo_code_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Delete promo code (Admin only)."""
    db_promo = db.query(models.PromoCode).filter(
        models.PromoCode.id == promo_code_id
    ).first()
    
    if not db_promo:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    db.delete(db_promo)
    db.commit()
    return None


# ==================== ORDERS ====================

def generate_order_number():
    """Generate unique order number."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"ORD{timestamp}{random_suffix}"


@router.post("/orders", response_model=schemas.OrderResponse)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new order (User endpoint)."""
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")
    
    # Calculate subtotal and validate products
    subtotal = Decimal(0)
    order_items_data = []
    all_products_support_cod = True
    
    for item in order.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id,
            models.Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found or inactive"
            )
        
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product.name}. Available: {product.stock_quantity}"
            )
        
        # Check if COD is supported for all products
        if not product.allow_cod:
            all_products_support_cod = False
        
        item_total = product.selling_price * item.quantity
        subtotal += item_total
        
        order_items_data.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": product.selling_price,
            "total_price": item_total
        })
    
    # Validate payment method
    if order.payment_method == "cod" and not all_products_support_cod:
        raise HTTPException(
            status_code=400,
            detail="Cash on Delivery is not available for one or more products in your cart"
        )
    
    # Apply promo code if provided
    discount_amount = Decimal(0)
    promo_code_id = None
    
    if order.promo_code:
        promo_code = db.query(models.PromoCode).filter(
            models.PromoCode.code == order.promo_code.upper(),
            models.PromoCode.is_active == True
        ).first()
        
        if promo_code:
            # Validate promo code
            validation = schemas.PromoCodeValidate(
                code=order.promo_code,
                order_amount=subtotal,
                is_product_order=True
            )
            
            # Use validation logic (simplified here)
            if promo_code.applicable_to_products:
                promo_code_id = promo_code.id
                
                if promo_code.discount_type == "percentage":
                    discount_amount = (subtotal * promo_code.discount_value) / 100
                    if promo_code.max_discount_amount and discount_amount > promo_code.max_discount_amount:
                        discount_amount = promo_code.max_discount_amount
                else:
                    discount_amount = promo_code.discount_value
                
                if discount_amount > subtotal:
                    discount_amount = subtotal
    
    # Calculate shipping charges dynamically per product
    shipping_charges = Decimal(0)
    for item in order.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()
        
        if product:
            # Check if product has free shipping threshold
            if product.free_shipping_above and subtotal >= product.free_shipping_above:
                # Free shipping if order total exceeds product's threshold
                continue
            else:
                # Add product's shipping charge from database (multiplied by quantity)
                shipping_charges += Decimal(product.shipping_charge) * item.quantity
    
    tax_amount = Decimal(0)  # Add tax calculation if needed
    
    total_amount = subtotal - discount_amount + shipping_charges + tax_amount
    
    # Set payment status based on payment method
    payment_status = "pending" if order.payment_method == "online" else "pending"
    order_status = "pending"
    
    # Create order
    db_order = models.Order(
        user_id=current_user.id,
        promo_code_id=promo_code_id,
        order_number=generate_order_number(),
        subtotal=subtotal,
        discount_amount=discount_amount,
        shipping_charges=shipping_charges,
        tax_amount=tax_amount,
        total_amount=total_amount,
        shipping_name=order.shipping_name,
        shipping_mobile=order.shipping_mobile,
        shipping_address=order.shipping_address,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_pincode=order.shipping_pincode,
        notes=order.notes,
        payment_method=order.payment_method,
        status=order_status,
        payment_status=payment_status
    )
    db.add(db_order)
    db.flush()
    
    # Create order items and update stock
    for item_data in order_items_data:
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_order_item)
        
        # Update product stock and sales
        product = db.query(models.Product).filter(
            models.Product.id == item_data["product_id"]
        ).first()
        product.stock_quantity -= item_data["quantity"]
        product.total_sales += item_data["quantity"]
    
    # Update promo code usage
    if promo_code_id:
        promo_code = db.query(models.PromoCode).filter(
            models.PromoCode.id == promo_code_id
        ).first()
        promo_code.current_uses += 1
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders", response_model=List[schemas.OrderListResponse])
def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get user's orders (User endpoint)."""
    query = db.query(models.Order).filter(models.Order.user_id == current_user.id)
    
    if status:
        query = query.filter(models.Order.status == status)
    
    orders = query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/orders/all", response_model=List[schemas.OrderListResponse])
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Get all orders (Admin only)."""
    query = db.query(models.Order)
    
    if status:
        query = query.filter(models.Order.status == status)
    
    if payment_status:
        query = query.filter(models.Order.payment_status == payment_status)
    
    orders = query.order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()
    return orders


@router.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get order by ID (User can only view their own orders)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order or is admin
    if order.user_id != current_user.id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this order")
    
    return order


@router.put("/orders/{order_id}", response_model=schemas.OrderResponse)
def update_order(
    order_id: int,
    order: schemas.OrderUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Update order status (Admin only)."""
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    for key, value in order.dict(exclude_unset=True).items():
        setattr(db_order, key, value)
    
    db.commit()
    db.refresh(db_order)
    return db_order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Cancel order (User can cancel their own pending orders)."""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user owns this order
    if order.user_id != current_user.id and current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this order")
    
    # Only allow cancellation of pending orders
    if order.status not in ["pending", "confirmed"]:
        raise HTTPException(status_code=400, detail="Cannot cancel order in current status")
    
    # Restore stock
    for item in order.order_items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id
        ).first()
        if product:
            product.stock_quantity += item.quantity
            product.total_sales -= item.quantity
    
    order.status = "cancelled"
    db.commit()
    return None
