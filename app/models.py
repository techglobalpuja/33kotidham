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
    # Active flag: admin can enable/disable puja. Default is False.
    is_active = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    # When a Puja is deleted we want its images removed as well.
    # Use ORM cascade so SQLAlchemy deletes child rows instead of setting FK to NULL
    images = relationship(
        "PujaImage",
        back_populates="puja",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    bookings = relationship("Booking", back_populates="puja")
    puja_plans = relationship(
        "PujaPlan",
        back_populates="puja",
        cascade="all, delete-orphan",
        passive_deletes=True
    )
    puja_chadawas = relationship("PujaChadawa", back_populates="puja")
    # Ensure benefits are deleted when parent Puja is deleted
    benefits = relationship(
        "PujaBenefit",
        back_populates="puja",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Plans
    plan_ids = relationship(
        "Plan",
        secondary="puja_plans",
        back_populates="pujas",
        overlaps="puja_plans"
    )
    # temples that recommend this puja (many-to-many)
    temples = relationship(
        "temple",
        secondary="temple_recommended_pujas",
        back_populates="recommended_pujas",
        overlaps="puja_chadawas,puja_plans",
    )


class PujaImage(Base):
    __tablename__ = "puja_images"

    id = Column(Integer, primary_key=True, index=True)
    puja_id = Column(Integer, ForeignKey("pujas.id", ondelete="CASCADE"), nullable=False)
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
    puja_plans = relationship(
        "PujaPlan",
        back_populates="plan",
        overlaps="plan_ids"
    )
    pujas = relationship(
        "Puja",
        secondary="puja_plans",
        back_populates="plan_ids",
        overlaps="puja_plans"
    )


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
    # temples that offer this chadawa
    temples = relationship(
        "temple",
        secondary="temple_chadawas",
        back_populates="chadawas"
    )


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    puja_id = Column(Integer, ForeignKey("pujas.id"), nullable=True)
    temple_id = Column(Integer, ForeignKey("temple.id"), nullable=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=True)
    booking_date = Column(DateTime(timezone=True), server_default=func.now())
    # Personal details supplied at booking time
    mobile_number = Column(String(30), nullable=True)
    whatsapp_number = Column(String(30), nullable=True)
    gotra = Column(String(100), nullable=True)
    status = Column(String(20), default=BookingStatus.PENDING.value, nullable=False)
    puja_link = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="bookings")
    puja = relationship("Puja", back_populates="bookings")
    temple = relationship("temple", back_populates="bookings")
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
    # Set ON DELETE CASCADE so that when a Booking is removed the Payment row
    # is automatically removed at the database level. Note: updating an
    # existing database requires an Alembic migration or a manual ALTER TABLE
    # (see scripts/set_payments_fk_ondelete.py included with the project).
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
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
    puja = relationship(
        "Puja",
        back_populates="puja_plans",
        overlaps="plan_ids,pujas"
    )
    plan = relationship(
        "Plan",
        back_populates="puja_plans",
        overlaps="plan_ids,pujas"
    )


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
    puja_id = Column(Integer, ForeignKey("pujas.id", ondelete="CASCADE"), nullable=False)
    benefit_title = Column(String(200), nullable=False)
    benefit_description = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    puja = relationship("Puja", back_populates="benefits")


# Association table for many-to-many relationship between blogs and categories
blog_categories = Table(
    "blog_categories",
    Base.metadata,
    Column("blog_id", Integer, ForeignKey("blogs.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
)

# Association table for recommended pujas for temples (many-to-many)
temple_recommended_pujas = Table(
    "temple_recommended_pujas",
    Base.metadata,
    Column("temple_id", Integer, ForeignKey("temple.id", ondelete="CASCADE"), primary_key=True),
    Column("puja_id", Integer, ForeignKey("pujas.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for temples and chadawas (many-to-many)
temple_chadawas = Table(
    "temple_chadawas",
    Base.metadata,
    Column("temple_id", Integer, ForeignKey("temple.id", ondelete="CASCADE"), primary_key=True),
    Column("chadawa_id", Integer, ForeignKey("chadawas.id", ondelete="CASCADE"), primary_key=True),
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    blogs = relationship(
        "Blog",
        secondary=blog_categories,
        back_populates="categories"
    )


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    subtitle = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)  # Rich text content with images and special characters
    thumbnail_image = Column(String(500), nullable=True)  # Featured/thumbnail image URL
    meta_description = Column(String(160), nullable=True)  # SEO meta description
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Publishing settings
    is_featured = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    publish_time = Column(DateTime(timezone=True), nullable=True)  # Scheduled publish time
    
    # SEO and URL
    slug = Column(String(255), nullable=True, unique=True)  # URL-friendly version of title
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    author = relationship("User")
    categories = relationship(
        "Category",
        secondary=blog_categories,
        back_populates="blogs"
    )



class temple(Base):
    __tablename__ = "temple"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    location = Column(String(100), nullable=True)
    slug = Column(String(100), nullable=True)
    # recommended pujas (many-to-many)
    recommended_pujas = relationship(
        "Puja",
        secondary="temple_recommended_pujas",
        back_populates="temples",
        lazy="joined",
    )
    # chadawas available/offered at this temple
    chadawas = relationship(
        "Chadawa",
        secondary="temple_chadawas",
        back_populates="temples",
        lazy="joined",
    )
    # bookings made for this temple
    bookings = relationship("Booking", back_populates="temple")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


