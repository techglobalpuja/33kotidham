from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
import random
import string
from app import models, schemas
from app.utils import FileManager
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
        return db.query(models.Puja).options(
            joinedload(models.Puja.puja_chadawas).joinedload(models.PujaChadawa.chadawa),
            joinedload(models.Puja.plan_ids)
        ).filter(models.Puja.id == puja_id).first()
    
    @staticmethod
    def get_pujas(db: Session, skip: int = 0, limit: int = 100) -> List[models.Puja]:
        return db.query(models.Puja).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_puja(db: Session, puja: schemas.PujaCreate) -> models.Puja:
        # exclude non-model fields (benefits, plan_ids, chadawa_ids) when constructing the ORM model
        db_puja = models.Puja(**puja.dict(exclude={"benefits", "plan_ids", "chadawa_ids"}))
        db.add(db_puja)
        db.commit()
        db.refresh(db_puja)

        # Add benefits if provided
        if puja.benefits:
            for benefit in puja.benefits:
                benefit_data = schemas.PujaBenefitCreate(
                    puja_id=db_puja.id,
                    benefit_title=benefit.benefit_title,
                    benefit_description=benefit.benefit_description
                )
                PujaBenefitCRUD.create_puja_benefit(db, benefit_data)

        # Add plans if provided
        if puja.plan_ids:
            for plan_id in puja.plan_ids:
                plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
                if plan:
                    db_puja.plan_ids.append(plan)

        # Add chadawas if provided
        if getattr(puja, 'chadawa_ids', None):
            for ch_id in puja.chadawa_ids:
                ch = db.query(models.Chadawa).filter(models.Chadawa.id == ch_id).first()
                if ch:
                    # attach association object to the parent so ORM knows about the relationship
                    db_pc = models.PujaChadawa(chadawa=ch)
                    db_puja.puja_chadawas.append(db_pc)

        db.commit()
        db.refresh(db_puja)
        return db_puja
    
    @staticmethod
    def update_puja(db: Session, puja_id: int, puja_update: schemas.PujaUpdate) -> Optional[models.Puja]:
        db_puja = db.query(models.Puja).filter(models.Puja.id == puja_id).first()
        if not db_puja:
            return None
        
        update_data = puja_update.dict(exclude_unset=True)

        # Handle plan_ids (relationship) - convert ids to Plan model instances
        if 'plan_ids' in update_data:
            plan_ids = update_data.pop('plan_ids') or []
            if plan_ids:
                plans = db.query(models.Plan).filter(models.Plan.id.in_(plan_ids)).all()
            else:
                plans = []
            # Clear existing association rows safely to avoid StaleDataError
            db.query(models.PujaPlan).filter(models.PujaPlan.puja_id == puja_id).delete(synchronize_session=False)
            db.flush()
            db_puja.plan_ids = plans

        # Handle benefits - replace existing benefits with new ones if provided
        if 'benefits' in update_data:
            benefits = update_data.pop('benefits') or []
            # delete existing benefits
            db.query(models.PujaBenefit).filter(models.PujaBenefit.puja_id == puja_id).delete()
            db.commit()
            # add new benefits
            for b in benefits:
                # b is expected to be a dict-like with benefit_title and benefit_description
                benefit_title = b.get('benefit_title') if isinstance(b, dict) else getattr(b, 'benefit_title', None)
                benefit_description = b.get('benefit_description') if isinstance(b, dict) else getattr(b, 'benefit_description', None)
                if benefit_title and benefit_description:
                    db_benefit = models.PujaBenefit(
                        puja_id=puja_id,
                        benefit_title=benefit_title,
                        benefit_description=benefit_description
                    )
                    db.add(db_benefit)

        # Handle category field which may be provided as list in schemas but stored as string in model
        if 'category' in update_data:
            category_value = update_data.pop('category')
            if isinstance(category_value, list):
                db_puja.category = ','.join(category_value)
            else:
                db_puja.category = category_value

        # Handle chadawa_ids - replace existing PujaChadawa associations
        if 'chadawa_ids' in update_data:
            chadawa_ids = update_data.pop('chadawa_ids') or []
            # delete existing association rows safely
            db.query(models.PujaChadawa).filter(models.PujaChadawa.puja_id == puja_id).delete(synchronize_session=False)
            db.flush()
            # add new associations
            for ch_id in chadawa_ids:
                ch = db.query(models.Chadawa).filter(models.Chadawa.id == ch_id).first()
                if ch:
                    db_pc = models.PujaChadawa(chadawa=ch)
                    db_puja.puja_chadawas.append(db_pc)

        # Set remaining simple fields
        for field, value in update_data.items():
            setattr(db_puja, field, value)

        db.commit()
        db.refresh(db_puja)
        return db_puja
    
    @staticmethod
    def delete_puja(db: Session, puja_id: int) -> bool:
        # If there are bookings referencing this puja, nullify the puja_id on those bookings
        # to avoid foreign key constraint violations while preserving booking records.
        db.query(models.Booking).filter(models.Booking.puja_id == puja_id).update({"puja_id": None}, synchronize_session=False)

        # Remove association rows that have no ON DELETE CASCADE at DB level
        # Delete PujaPlan association rows
        db.query(models.PujaPlan).filter(models.PujaPlan.puja_id == puja_id).delete(synchronize_session=False)
        # Delete PujaChadawa association rows to avoid FK constraint when deleting the Puja
        db.query(models.PujaChadawa).filter(models.PujaChadawa.puja_id == puja_id).delete(synchronize_session=False)
        # Finally delete the Puja itself
        db.query(models.Puja).filter(models.Puja.id == puja_id).delete(synchronize_session=False)
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


# Temple CRUD operations
class TempleCRUD:
    @staticmethod
    def get_temple(db: Session, temple_id: int) -> Optional[models.temple]:
        return db.query(models.temple).filter(models.temple.id == temple_id).first()

    @staticmethod
    def get_temples(db: Session, skip: int = 0, limit: int = 100) -> List[models.temple]:
        return db.query(models.temple).offset(skip).limit(limit).all()

    @staticmethod
    def create_temple(db: Session, temple: 'schemas.TempleCreate') -> models.temple:
        # create base temple
        db_temple = models.temple(
            name=temple.name,
            description=temple.description,
            image_url=temple.image_url,
            location=temple.location,
            slug=temple.slug,
        )
        db.add(db_temple)
        db.flush()

        # attach recommended pujas if provided
        if getattr(temple, 'recommended_puja_ids', None):
            pujas = db.query(models.Puja).filter(models.Puja.id.in_(temple.recommended_puja_ids)).all()
            for p in pujas:
                db_temple.recommended_pujas.append(p)
        # attach chadawas if provided
        if getattr(temple, 'chadawa_ids', None):
            chs = db.query(models.Chadawa).filter(models.Chadawa.id.in_(temple.chadawa_ids)).all()
            for c in chs:
                db_temple.chadawas.append(c)

        db.commit()
        db.refresh(db_temple)
        return db_temple

    @staticmethod
    def update_temple(db: Session, temple_id: int, temple_update: 'schemas.TempleUpdate') -> Optional[models.temple]:
        db_temple = db.query(models.temple).filter(models.temple.id == temple_id).first()
        if not db_temple:
            return None

        update_data = temple_update.dict(exclude_unset=True)
        # handle recommended puja ids replacement
        if 'recommended_puja_ids' in update_data:
            rpids = update_data.pop('recommended_puja_ids') or []
            # clear existing
            db_temple.recommended_pujas = []
            if rpids:
                pujas = db.query(models.Puja).filter(models.Puja.id.in_(rpids)).all()
                db_temple.recommended_pujas = pujas
        # handle chadawa ids replacement
        if 'chadawa_ids' in update_data:
            cids = update_data.pop('chadawa_ids') or []
            db_temple.chadawas = []
            if cids:
                chs = db.query(models.Chadawa).filter(models.Chadawa.id.in_(cids)).all()
                db_temple.chadawas = chs

        for field, value in update_data.items():
            setattr(db_temple, field, value)

        db.commit()
        db.refresh(db_temple)
        return db_temple

    @staticmethod
    def delete_temple(db: Session, temple_id: int) -> bool:
        db_temple = db.query(models.temple).filter(models.temple.id == temple_id).first()
        if not db_temple:
            return False
        db.delete(db_temple)
        db.commit()
        return True

    @staticmethod
    def set_recommended_pujas(db: Session, temple_id: int, puja_ids: List[int]) -> Optional[models.temple]:
        db_temple = db.query(models.temple).filter(models.temple.id == temple_id).first()
        if not db_temple:
            return None
        db_temple.recommended_pujas = []
        if puja_ids:
            pujas = db.query(models.Puja).filter(models.Puja.id.in_(puja_ids)).all()
            db_temple.recommended_pujas = pujas
        db.commit()
        db.refresh(db_temple)
        return db_temple


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
        # Defensive normalization: treat falsy or non-positive IDs as None to avoid FK errors
        puja_id = booking.puja_id if getattr(booking, 'puja_id', None) and int(getattr(booking, 'puja_id', 0)) > 0 else None
        temple_id = booking.temple_id if getattr(booking, 'temple_id', None) and int(getattr(booking, 'temple_id', 0)) > 0 else None
        plan_id = booking.plan_id if getattr(booking, 'plan_id', None) and int(getattr(booking, 'plan_id', 0)) > 0 else None

        db_booking = models.Booking(
            user_id=user_id,
            puja_id=puja_id,
            temple_id=temple_id,
            plan_id=plan_id,
            booking_date=booking.booking_date or datetime.utcnow(),
            mobile_number=getattr(booking, 'mobile_number', None),
            whatsapp_number=getattr(booking, 'whatsapp_number', None),
            gotra=getattr(booking, 'gotra', None),
        )
        db.add(db_booking)
        db.flush()  # Get the booking ID
        
        # Add chadawas provided either as objects or as IDs
        # If client sends plain chadawa_ids: [1,2], convert to BookingChadawa entries
        if getattr(booking, 'chadawa_ids', None):
            for ch_id in booking.chadawa_ids:
                db_booking_chadawa = models.BookingChadawa(
                    booking_id=db_booking.id,
                    chadawa_id=ch_id,
                    note=None
                )
                db.add(db_booking_chadawa)
        else:
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


# Category CRUD operations
class CategoryCRUD:
    @staticmethod
    def get_category(db: Session, category_id: int) -> Optional[models.Category]:
        return db.query(models.Category).filter(models.Category.id == category_id).first()
    
    @staticmethod
    def get_categories(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[models.Category]:
        query = db.query(models.Category)
        if active_only:
            query = query.filter(models.Category.is_active == True)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
        # Ensure category name is unique (case-insensitive)
        existing = db.query(models.Category).filter(models.Category.name == category.name).first()
        if existing:
            raise ValueError(f"Category '{category.name}' already exists.")

        db_category = models.Category(**category.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def update_category(db: Session, category_id: int, category_update: schemas.CategoryUpdate) -> Optional[models.Category]:
        db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not db_category:
            return None
        
        update_data = category_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        db.commit()
        db.refresh(db_category)
        return db_category
    
    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not db_category:
            return False
        
        db.delete(db_category)
        db.commit()
        return True


# Blog CRUD operations
class BlogCRUD:
    @staticmethod
    def get_blog(db: Session, blog_id: int) -> Optional[models.Blog]:
        return db.query(models.Blog).options(joinedload(models.Blog.categories)).filter(
            models.Blog.id == blog_id,
            models.Blog.is_active == True
        ).first()
    
    @staticmethod
    def get_blog_by_slug(db: Session, slug: str) -> Optional[models.Blog]:
        return db.query(models.Blog).filter(
            models.Blog.slug == slug,
            models.Blog.is_active == True
        ).first()
    
    @staticmethod
    def get_blogs(db: Session, skip: int = 0, limit: int = 100, featured_only: bool = False, 
                  category_id: Optional[int] = None, published_only: bool = True) -> List[models.Blog]:
        query = db.query(models.Blog).options(joinedload(models.Blog.categories)).filter(models.Blog.is_active == True)
        
        if published_only:
            query = query.filter(or_(
                models.Blog.publish_time.is_(None),
                models.Blog.publish_time <= datetime.now()
            ))
        
        if featured_only:
            query = query.filter(models.Blog.is_featured == True)
        
        if category_id:
            query = query.filter(models.Blog.category_id == category_id)
        
        return query.order_by(models.Blog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_admin_blogs(db: Session, skip: int = 0, limit: int = 100) -> List[models.Blog]:
        """Get all blogs for admin (including inactive and scheduled)"""
        return db.query(models.Blog).order_by(models.Blog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_blog(db: Session, blog: schemas.BlogCreate, author_id: int, categories: List[models.Category]) -> models.Blog:
        # Generate slug from title if not provided
        slug = blog.slug
        if not slug:
            slug = blog.title.lower().replace(' ', '-').replace('_', '-')
            # Remove special characters
            import re
            slug = re.sub(r'[^a-z0-9\-]', '', slug)

        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while db.query(models.Blog).filter(models.Blog.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1

        blog_data = blog.model_dump()
        blog_data['slug'] = slug
        blog_data['author_id'] = author_id

        # Remove category_ids from blog_data as it's not a valid Blog model attribute
        blog_data.pop('category_ids', None)

        db_blog = models.Blog(**blog_data)
        db.add(db_blog)
        db.commit()

        # Associate categories with the blog
        # Deduplicate categories based on their IDs
        unique_categories = {category.id: category for category in categories}.values()
        db_blog.categories = list(unique_categories)
        db.commit()
        db.refresh(db_blog)
        return db_blog
    
    @staticmethod
    def update_blog(db: Session, blog_id: int, blog_update: schemas.BlogUpdate, categories: list) -> Optional[models.Blog]:
        db_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
        if not db_blog:
            return None

        # Slug uniqueness check
        if blog_update.slug:
            existing_blog = db.query(models.Blog).filter(models.Blog.slug == blog_update.slug, models.Blog.id != blog_id).first()
            if existing_blog:
                raise ValueError(f"Slug '{blog_update.slug}' already exists for another blog.")

        update_data = blog_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_blog, field, value)
        # Update categories
        db_blog.categories = categories
        db.commit()
        db.refresh(db_blog)
        return db_blog
    
    @staticmethod
    def delete_blog(db: Session, blog_id: int) -> bool:
        db_blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
        if not db_blog:
            return False
        
        db.delete(db_blog)
        db.commit()
        return True
    
    @staticmethod
    def search_blogs(db: Session, search_term: str, skip: int = 0, limit: int = 100) -> List[models.Blog]:
        """Search blogs by title, subtitle, or content"""
        return db.query(models.Blog).filter(
            models.Blog.is_active == True,
            or_(
                models.Blog.publish_time.is_(None),
                models.Blog.publish_time <= datetime.now()
            ),
            or_(
                models.Blog.title.ilike(f"%{search_term}%"),
                models.Blog.subtitle.ilike(f"%{search_term}%"),
                models.Blog.content.ilike(f"%{search_term}%"),
                models.Blog.tags.ilike(f"%{search_term}%")
            )
        ).order_by(models.Blog.created_at.desc()).offset(skip).limit(limit).all()


# PujaPlan CRUD operations
class PujaPlanCRUD:
    @staticmethod
    def create_puja_plan(db: Session, puja_plan: schemas.PujaPlanCreate) -> models.PujaPlan:
        db_puja_plan = models.PujaPlan(**puja_plan.dict())
        db.add(db_puja_plan)
        db.commit()
        db.refresh(db_puja_plan)
        return db_puja_plan

    @staticmethod
    def update_puja_plans(db: Session, puja_id: int, plan_ids: List[int]):
        # Delete existing PujaPlan entries for the puja
        db.query(models.PujaPlan).filter(models.PujaPlan.puja_id == puja_id).delete()
        db.commit()

        # Add new PujaPlan entries
        for plan_id in plan_ids:
            db_puja_plan = models.PujaPlan(puja_id=puja_id, plan_id=plan_id)
            db.add(db_puja_plan)
        db.commit()

    @staticmethod
    def delete_puja_plans(db: Session, puja_id: int):
        db.query(models.PujaPlan).filter(models.PujaPlan.puja_id == puja_id).delete()
        db.commit()
