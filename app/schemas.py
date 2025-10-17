from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
import datetime as dt
from decimal import Decimal
from app.models import UserRole, BookingStatus, PaymentStatus


# Base schemas
class BaseResponse(BaseModel):
    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    mobile: str


class UserCreate(UserBase):
    password: Optional[str] = None
    role: Optional[UserRole] = UserRole.USER


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    is_active: Optional[bool] = None
    email_verified: Optional[bool] = None


class UserResponse(UserBase, BaseResponse):
    id: int
    role: str
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime


class UserLogin(BaseModel):
    mobile: str
    password: Optional[str] = None


class AdminLogin(BaseModel):
    username: str  # Can be mobile or email
    password: str


class AdminCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    mobile: str
    password: str
    role: UserRole = UserRole.ADMIN


# OTP schemas
class OTPRequest(BaseModel):
    mobile: str


class OTPVerify(BaseModel):
    mobile: str
    otp_code: str


class OTPResponse(BaseResponse):
    id: int
    user_id: int
    expires_at: datetime
    is_verified: bool


# Puja schemas
class PujaBase(BaseModel):
    name: str
    sub_heading: str
    description: Optional[str] = None
    date: Optional[dt.date] = None
    time: Optional[dt.time] = None
    
    # Temple details
    temple_image_url: Optional[str] = None
    temple_address: Optional[str] = None
    temple_description: Optional[str] = None
    
    # Prasad
    prasad_price: Optional[int] = None
    is_prasad_active: bool = False
    
    # Dakshina
    dakshina_prices_inr: Optional[str] = None
    dakshina_prices_usd: Optional[str] = None
    is_dakshina_active: bool = False
    
    # Manokamna
    manokamna_prices_inr: Optional[str] = None
    manokamna_prices_usd: Optional[str] = None
    is_manokamna_active: bool = False
    
    # General
    category: Optional[str] = None


class PujaCreate(PujaBase):
    benefits: Optional[List['PujaBenefitBase']] = None


class PujaUpdate(BaseModel):
    name: Optional[str] = None
    sub_heading: Optional[str] = None
    description: Optional[str] = None
    date: Optional[dt.date] = None
    time: Optional[dt.time] = None
    
    # Temple details
    temple_image_url: Optional[str] = None
    temple_address: Optional[str] = None
    temple_description: Optional[str] = None
    
    # Prasad
    prasad_price: Optional[int] = None
    is_prasad_active: Optional[bool] = None
    
    # Dakshina
    dakshina_prices_inr: Optional[str] = None
    dakshina_prices_usd: Optional[str] = None
    is_dakshina_active: Optional[bool] = None
    
    # Manokamna
    manokamna_prices_inr: Optional[str] = None
    manokamna_prices_usd: Optional[str] = None
    is_manokamna_active: Optional[bool] = None
    
    # General
    category: Optional[str] = None


class PujaImageResponse(BaseResponse):
    id: int
    image_url: str


class PujaBenefitBase(BaseModel):
    benefit_title: str
    benefit_description: str


class PujaBenefitCreate(PujaBenefitBase):
    puja_id: int


class PujaBenefitResponse(PujaBenefitBase, BaseResponse):
    id: int
    puja_id: int
    created_at: datetime


class PujaResponse(PujaBase, BaseResponse):
    id: int
    created_at: datetime
    updated_at: datetime
    benefits: Optional[List[PujaBenefitResponse]] = []
    images: List[PujaImageResponse] = []


# Plan schemas
class PlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    actual_price: Decimal
    discounted_price: Optional[Decimal] = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    actual_price: Optional[Decimal] = None
    discounted_price: Optional[Decimal] = None


class PlanResponse(PlanBase, BaseResponse):
    id: int
    created_at: datetime


# Chadawa schemas
class ChadawaBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Decimal
    requires_note: bool = False


class ChadawaCreate(ChadawaBase):
    pass


class ChadawaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[Decimal] = None
    requires_note: Optional[bool] = None


class ChadawaResponse(ChadawaBase, BaseResponse):
    id: int


# Booking schemas
class BookingChadawaCreate(BaseModel):
    chadawa_id: int
    note: Optional[str] = None


class BookingChadawaResponse(BaseResponse):
    id: int
    chadawa_id: int
    note: Optional[str] = None
    chadawa: Optional[ChadawaResponse] = None


class BookingBase(BaseModel):
    puja_id: Optional[int] = None
    plan_id: Optional[int] = None
    booking_date: Optional[datetime] = None


class BookingCreate(BookingBase):
    chadawas: List[BookingChadawaCreate] = []


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None
    puja_link: Optional[str] = None


class BookingResponse(BookingBase, BaseResponse):
    id: int
    user_id: int
    status: str
    puja_link: Optional[str] = None
    created_at: datetime
    user: Optional[UserResponse] = None
    puja: Optional[PujaResponse] = None
    plan: Optional[PlanResponse] = None
    booking_chadawas: List[BookingChadawaResponse] = []


# Payment schemas
class PaymentCreate(BaseModel):
    booking_id: int
    amount: Decimal


class PaymentUpdate(BaseModel):
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    status: Optional[PaymentStatus] = None


class PaymentResponse(BaseResponse):
    id: int
    booking_id: int
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount: Decimal
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime


# Association schemas
class PujaPlanCreate(BaseModel):
    puja_id: int
    plan_id: int


class PujaChadawaCreate(BaseModel):
    puja_id: int
    chadawa_id: int


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    mobile: Optional[str] = None


# File upload schema
class FileUploadResponse(BaseModel):
    filename: str
    file_url: str


# Dashboard schemas
class DashboardStats(BaseModel):
    total_users: int
    total_bookings: int
    total_revenue: Decimal
    pending_bookings: int
    completed_bookings: int


# Pagination schema
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 100

    @validator('limit')
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError('Limit cannot exceed 100')
        return v


# Category schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase, BaseResponse):
    id: int
    created_at: datetime
    updated_at: datetime


# Blog schemas
class BlogBase(BaseModel):
    title: str
    subtitle: Optional[str] = None
    content: str
    thumbnail_image: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None  # Comma-separated tags
    category_id: Optional[int] = None
    is_featured: bool = False
    is_active: bool = True
    publish_time: Optional[datetime] = None
    slug: Optional[str] = None
    
    @validator('category_id')
    def validate_category_id(cls, v):
        if v is not None and v <= 0:
            return None  # Convert invalid category_id to None
        return v


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    thumbnail_image: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    publish_time: Optional[datetime] = None
    slug: Optional[str] = None
    
    @validator('category_id')
    def validate_category_id(cls, v):
        if v is not None and v <= 0:
            return None  # Convert invalid category_id to None
        return v


class BlogResponse(BlogBase, BaseResponse):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    author: Optional[UserResponse] = None


class BlogListResponse(BaseResponse):
    id: int
    title: str
    subtitle: Optional[str] = None
    thumbnail_image: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None
    category_id: Optional[int] = None
    is_featured: bool
    is_active: bool
    publish_time: Optional[datetime] = None
    slug: Optional[str] = None
    author_id: int
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
