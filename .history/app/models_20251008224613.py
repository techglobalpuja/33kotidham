from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime, Date, Time, Enum, Table, Text, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


# Enums
class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    CREATED = "created"
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class UserRole(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    mobile = Column(String(15), unique=True, nullable=False)
    password = Column(String(255), nullable=True)  # Hashed password
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)  # Default inactive for regular users
    email_verified = Column(Boolean, default=False, nullable=False)  # Email verification status
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="user")
    otp_logins = relationship("OTPLogin", back_populates="user")
    
    def __init__(self, **kwargs):
        # Set is_active to True by default for admin roles
        if 'role' in kwargs and kwargs['role'] in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
            kwargs.setdefault('is_active', True)
        super().__init__(**kwargs)


class OTPLogin(Base):
    __tablename__ = "otp_logins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    otp_code = Column(String(6), nullable=False)
    is_verified = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="otp_logins")


class Puja(Base):
    __tablename__ = "pujas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    sub_heading = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    date = Column(Date, nullable=True)
    time = Column(Time, nullable=True)

    # Temple details
    temple_image_url = Column(String(500), nullable=True)
    temple_address = Column(Text, nullable=True)
    temple_description = Column(Text, nullable=True)

    # Prasad
    prasad_price = Column(Integer, nullable=True)
    is_prasad_active = Column(Boolean, default=False)

    # Dakshina
    dakshina_prices_inr = Column(String, nullable=True)
    dakshina_prices_usd = Column(String, nullable=True)
    is_dakshina_active = Column(Boolean, default=False)

    # Manokamna
    manokamna_prices_inr = Column(String, nullable=True)
    manokamna_prices_usd = Column(String, nullable=True)
    is_manokamna_active = Column(Boolean, default=False)

    # General
    category = Column(String(100), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    images = relationship("PujaImage", back_populates="puja")
    bookings = relationship("Booking", back_populates="puja")
    puja_plans = relationship("PujaPlan", back_populates="puja")
    puja_chadawas = relationship("PujaChadawa", back_populates="puja")
    benefits = relationship("PujaBenefit", back_populates="puja")


class PujaImage(Base):
    __tablename__ = "puja_images"

    id = Column(Integer, primary_key=True, index=True)
    puja_id = Column(Integer, ForeignKey("pujas.id"), nullable=False)
    image_url = Column(Text, nullable=False)

    # Relationships
    puja = relationship("Puja", back_populates="images")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    actual_price = Column(Numeric(10, 2), nullable=False)
    discounted_price = Column(Numeric(10, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    bookings = relationship("Booking", back_populates="plan")
    
    # Association object relationships
    puja_plans = relationship("PujaPlan", back_populates="plan")


class Chadawa(Base):
    __tablename__ = "chadawas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    requires_note = Column(Boolean, default=False)

    # Relationships
    booking_chadawas = relationship("BookingChadawa", back_populates="chadawa")
    
    # Association object relationships
    puja_chadawas = relationship("PujaChadawa", back_populates="chadawa")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    puja_id = Column(Integer, ForeignKey("pujas.id"), nullable=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    booking_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default=BookingStatus.PENDING.value, nullable=False)
    puja_link = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookings")
    puja = relationship("Puja", back_populates="bookings")
    plan = relationship("Plan", back_populates="bookings")
    booking_chadawas = relationship("BookingChadawa", back_populates="booking")
    payment = relationship("Payment", back_populates="booking", uselist=False)


class BookingChadawa(Base):
    __tablename__ = "booking_chadawas"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    chadawa_id = Column(Integer, ForeignKey("chadawas.id"), nullable=True)
    note = Column(Text, nullable=True)

    # Relationships
    booking = relationship("Booking", back_populates="booking_chadawas")
    chadawa = relationship("Chadawa", back_populates="booking_chadawas")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    razorpay_order_id = Column(String(100), nullable=False)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(10), default="INR")
    status = Column(String(20), default=PaymentStatus.CREATED.value, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    booking = relationship("Booking", back_populates="payment")


# Association table models
class PujaPlan(Base):
    __tablename__ = "puja_plans"

    id = Column(Integer, primary_key=True, index=True)
    puja_id = Column(Integer, ForeignKey("pujas.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)

    # Relationships
    puja = relationship("Puja", back_populates="puja_plans")
    plan = relationship("Plan", back_populates="puja_plans")


class PujaChadawa(Base):
    __tablename__ = "puja_chadawas"

    id = Column(Integer, primary_key=True, index=True)
    puja_id = Column(Integer, ForeignKey("pujas.id"), nullable=False)
    chadawa_id = Column(Integer, ForeignKey("chadawas.id"), nullable=False)

    # Relationships
    puja = relationship("Puja", back_populates="puja_chadawas")
    chadawa = relationship("Chadawa", back_populates="puja_chadawas")


class PujaBenefit(Base):
    __tablename__ = "puja_benefits"

    id = Column(Integer, primary_key=True, index=True)
    puja_id = Column(Integer, ForeignKey("pujas.id"), nullable=False)
    benefit_title = Column(String(200), nullable=False)
    benefit_description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    puja = relationship("Puja", back_populates="benefits")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    blogs = relationship("Blog", back_populates="category")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)  # Rich text content with images and special characters
    thumbnail_image = Column(String(500), nullable=True)  # Featured/thumbnail image URL
    meta_description = Column(String(160), nullable=True)  # SEO meta description
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # Publishing settings
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    publish_time = Column(DateTime(timezone=True), nullable=True)  # Scheduled publish time
    
    # Author information
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # SEO and URL
    slug = Column(String(255), nullable=True, unique=True)  # URL-friendly version of title
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    author = relationship("User")
    category = relationship("Category", back_populates="blogs")
