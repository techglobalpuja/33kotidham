from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import random
import string
from app import models, schemas
from app.auth import get_password_hash


# User CRUD operations
class UserCRUD:
    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    @staticmethod
    def get_user_by_mobile(db: Session, mobile: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.mobile == mobile).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.User]:
        return db.query(models.User).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_user(db: Session, user: schemas.UserCreate) -> models.User:
        hashed_password = None
        if user.password:
            hashed_password = get_password_hash(user.password)
        
        db_user = models.User(
            name=user.name,
            email=user.email,
            mobile=user.mobile,
            password=hashed_password,
            role=user.role.value if user.role else models.UserRole.USER.value
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate) -> Optional[models.User]:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        db_user = db.query(models.User).filter(models.User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True


# OTP CRUD operations
class OTPCRUD:
    @staticmethod
    def create_otp(db: Session, user_id: int) -> models.OTPLogin:
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=10)  # OTP expires in 10 minutes
        
        db_otp = models.OTPLogin(
            user_id=user_id,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(db_otp)
        db.commit()
        db.refresh(db_otp)
        return db_otp
    
    @staticmethod
    def verify_otp(db: Session, mobile: str, otp_code: str) -> Optional[models.User]:
        user = UserCRUD.get_user_by_mobile(db, mobile)
        if not user:
            return None
        
        otp = db.query(models.OTPLogin).filter(
            and_(
                models.OTPLogin.user_id == user.id,
                models.OTPLogin.otp_code == otp_code,
                models.OTPLogin.is_verified == False,
                models.OTPLogin.expires_at > datetime.utcnow()
            )
        ).first()
        
        if otp:
            otp.is_verified = True
            db.commit()
            return user
        return None


# Puja CRUD operations
class PujaCRUD:
    @staticmethod
    def get_puja(db: Session, puja_id: int) -> Optional[models.Puja]:
        return db.query(models.Puja).filter(models.Puja.id == puja_id).first()
    
    @staticmethod
    def get_pujas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Puja]:
        return db.query(models.Puja).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_puja(db: Session, puja: schemas.PujaCreate) -> models.Puja:
        db_puja = models.Puja(**puja.dict())
        db.add(db_puja)
        db.commit()
        db.refresh(db_puja)
        return db_puja
    
    @staticmethod
    def update_puja(db: Session, puja_id: int, puja_update: schemas.PujaUpdate) -> Optional[models.Puja]:
        db_puja = db.query(models.Puja).filter(models.Puja.id == puja_id).first()
        if not db_puja:
            return None
        
        update_data = puja_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_puja, field, value)
        
        db.commit()
        db.refresh(db_puja)
        return db_puja
    
    @staticmethod
    def delete_puja(db: Session, puja_id: int) -> bool:
        db_puja = db.query(models.Puja).filter(models.Puja.id == puja_id).first()
        if not db_puja:
            return False
        
        db.delete(db_puja)
        db.commit()
        return True


# Plan CRUD operations
class PlanCRUD:
    @staticmethod
    def get_plan(db: Session, plan_id: int) -> Optional[models.Plan]:
        return db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    
    @staticmethod
    def get_plans(db: Session, skip: int = 0, limit: int = 100) -> List[models.Plan]:
        return db.query(models.Plan).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_plan(db: Session, plan: schemas.PlanCreate) -> models.Plan:
        db_plan = models.Plan(**plan.dict())
        db.add(db_plan)
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    @staticmethod
    def update_plan(db: Session, plan_id: int, plan_update: schemas.PlanUpdate) -> Optional[models.Plan]:
        db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
        if not db_plan:
            return None
        
        update_data = plan_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_plan, field, value)
        
        db.commit()
        db.refresh(db_plan)
        return db_plan
    
    @staticmethod
    def delete_plan(db: Session, plan_id: int) -> bool:
        db_plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
        if not db_plan:
            return False
        
        db.delete(db_plan)
        db.commit()
        return True


# Chadawa CRUD operations
class ChadawaCRUD:
    @staticmethod
    def get_chadawa(db: Session, chadawa_id: int) -> Optional[models.Chadawa]:
        return db.query(models.Chadawa).filter(models.Chadawa.id == chadawa_id).first()
    
    @staticmethod
    def get_chadawas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Chadawa]:
        return db.query(models.Chadawa).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_chadawa(db: Session, chadawa: schemas.ChadawaCreate) -> models.Chadawa:
        db_chadawa = models.Chadawa(**chadawa.dict())
        db.add(db_chadawa)
        db.commit()
        db.refresh(db_chadawa)
        return db_chadawa
    
    @staticmethod
    def update_chadawa(db: Session, chadawa_id: int, chadawa_update: schemas.ChadawaUpdate) -> Optional[models.Chadawa]:
        db_chadawa = db.query(models.Chadawa).filter(models.Chadawa.id == chadawa_id).first()
        if not db_chadawa:
            return None
        
        update_data = chadawa_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chadawa, field, value)
        
        db.commit()
        db.refresh(db_chadawa)
        return db_chadawa
    
    @staticmethod
    def delete_chadawa(db: Session, chadawa_id: int) -> bool:
        db_chadawa = db.query(models.Chadawa).filter(models.Chadawa.id == chadawa_id).first()
        if not db_chadawa:
            return False
        
        db.delete(db_chadawa)
        db.commit()
        return True


# Booking CRUD operations
class BookingCRUD:
    @staticmethod
    def get_booking(db: Session, booking_id: int) -> Optional[models.Booking]:
        return db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    
    @staticmethod
    def get_bookings(db: Session, skip: int = 0, limit: int = 100, user_id: Optional[int] = None) -> List[models.Booking]:
        query = db.query(models.Booking)
        if user_id:
            query = query.filter(models.Booking.user_id == user_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_booking(db: Session, booking: schemas.BookingCreate, user_id: int) -> models.Booking:
        db_booking = models.Booking(
            user_id=user_id,
            puja_id=booking.puja_id,
            plan_id=booking.plan_id,
            booking_date=booking.booking_date or datetime.utcnow()
        )
        db.add(db_booking)
        db.flush()  # Get the booking ID
        
        # Add chadawas
        for chadawa_data in booking.chadawas:
            db_booking_chadawa = models.BookingChadawa(
                booking_id=db_booking.id,
                chadawa_id=chadawa_data.chadawa_id,
                note=chadawa_data.note
            )
            db.add(db_booking_chadawa)
        
        db.commit()
        db.refresh(db_booking)
        return db_booking
    
    @staticmethod
    def update_booking(db: Session, booking_id: int, booking_update: schemas.BookingUpdate) -> Optional[models.Booking]:
        db_booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
        if not db_booking:
            return None
        
        update_data = booking_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and isinstance(value, models.BookingStatus):
                setattr(db_booking, field, value.value)
            else:
                setattr(db_booking, field, value)
        
        db.commit()
        db.refresh(db_booking)
        return db_booking


# Payment CRUD operations
class PaymentCRUD:
    @staticmethod
    def get_payment(db: Session, payment_id: int) -> Optional[models.Payment]:
        return db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    
    @staticmethod
    def get_payment_by_booking(db: Session, booking_id: int) -> Optional[models.Payment]:
        return db.query(models.Payment).filter(models.Payment.booking_id == booking_id).first()
    
    @staticmethod
    def create_payment(db: Session, payment: schemas.PaymentCreate, razorpay_order_id: str) -> models.Payment:
        db_payment = models.Payment(
            booking_id=payment.booking_id,
            razorpay_order_id=razorpay_order_id,
            amount=payment.amount
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    
    @staticmethod
    def update_payment(db: Session, payment_id: int, payment_update: schemas.PaymentUpdate) -> Optional[models.Payment]:
        db_payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
        if not db_payment:
            return None
        
        update_data = payment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field == "status" and isinstance(value, models.PaymentStatus):
                setattr(db_payment, field, value.value)
            else:
                setattr(db_payment, field, value)
        
        db.commit()
        db.refresh(db_payment)
        return db_payment


# PujaBenefit CRUD operations
class PujaBenefitCRUD:
    @staticmethod
    def get_puja_benefits(db: Session, puja_id: int) -> List[models.PujaBenefit]:
        return db.query(models.PujaBenefit).filter(models.PujaBenefit.puja_id == puja_id).all()
    
    @staticmethod
    def create_puja_benefit(db: Session, benefit: schemas.PujaBenefitCreate) -> models.PujaBenefit:
        db_benefit = models.PujaBenefit(**benefit.dict())
        db.add(db_benefit)
        db.commit()
        db.refresh(db_benefit)
        return db_benefit
    
    @staticmethod
    def delete_puja_benefit(db: Session, benefit_id: int) -> bool:
        db_benefit = db.query(models.PujaBenefit).filter(models.PujaBenefit.id == benefit_id).first()
        if not db_benefit:
            return False
        
        db.delete(db_benefit)
        db.commit()
        return True
