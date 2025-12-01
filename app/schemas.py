from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from typing import Optional, List, Any, Dict
from datetime import datetime
import datetime as dt
from decimal import Decimal
from app.models import UserRole, BookingStatus, PaymentStatus
from app import models


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
    is_active: bool = False


class PujaCreate(PujaBase):
    benefits: Optional[List['PujaBenefitBase']] = None
    plan_ids: Optional[List[int]] = None
    chadawa_ids: Optional[List[int]] = None
    category: List[str] = []  # Update to accept a list of strings


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
    category: List[str] = []  # Update to accept a list of strings
    benefits: Optional[List['PujaBenefitBase']] = None
    plan_ids: Optional[List[int]] = None
    chadawa_ids: Optional[List[int]] = None
    is_active: Optional[bool] = None


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
    is_active: bool
    benefits: Optional[List[PujaBenefitResponse]] = []
    images: List[PujaImageResponse] = []
    plan_ids: List[int] = []
    chadawas: List['ChadawaResponse'] = []

    @validator("plan_ids", pre=True, each_item=False)
    def extract_plan_ids(cls, value):
        if isinstance(value, list) and all(isinstance(plan, models.Plan) for plan in value):
            return [plan.id for plan in value]
        return value


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
    temple_id: Optional[int] = None
    plan_id: Optional[int] = None
    booking_date: Optional[datetime] = None
    # personal details
    mobile_number: Optional[str] = None
    whatsapp_number: Optional[str] = None
    gotra: Optional[str] = None


class BookingCreate(BookingBase):
    chadawas: List[BookingChadawaCreate] = []
    chadawa_ids: Optional[List[int]] = None


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
    temple: Optional["TempleResponse"] = None
    plan: Optional[PlanResponse] = None
    booking_chadawas: List[BookingChadawaResponse] = []


class RazorpayBookingResponse(BaseModel):
    booking: BookingResponse
    razorpay_order_id: str
    razorpay_order: Dict[str, Any]

    class Config:
        from_attributes = True


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
    category_ids: List[int] = []  # Changed from single category_id to a list
    is_featured: bool = False
    is_active: bool = True
    publish_time: Optional[datetime] = None
    slug: Optional[str] = None


# Temple schemas
class TempleBase(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[str] = None
    slug: Optional[str] = None


class TempleCreate(TempleBase):
    recommended_puja_ids: Optional[List[int]] = None
    chadawa_ids: Optional[List[int]] = None


class TempleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    location: Optional[str] = None
    slug: Optional[str] = None
    recommended_puja_ids: Optional[List[int]] = None
    chadawa_ids: Optional[List[int]] = None


class TempleResponse(TempleBase, BaseResponse):
    id: int
    created_at: datetime
    updated_at: datetime
    recommended_pujas: Optional[List[PujaResponse]] = []
    chadawas: Optional[List[ChadawaResponse]] = []

    class Config:
        from_attributes = True


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    content: Optional[str] = None
    thumbnail_image: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None
    category_ids: Optional[List[int]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    publish_time: Optional[datetime] = None
    slug: Optional[str] = None


class BlogResponse(BlogBase, BaseResponse):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryResponse] = []  # Updated to include a list of categories
    author: Optional[UserResponse] = None


class BlogListResponse(BaseResponse):
    id: int
    title: str
    subtitle: Optional[str] = None
    thumbnail_image: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None
    is_featured: bool
    is_active: bool
    publish_time: Optional[datetime] = None
    slug: Optional[str] = None
    author_id: int
    created_at: datetime
    updated_at: datetime
    categories: List[CategoryResponse] = []  # Add categories list to response


# ==================== PRODUCT SCHEMAS ====================

# Product Category schemas
class ProductCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(ProductCategoryBase, BaseResponse):
    id: int
    created_at: datetime
    updated_at: datetime


# Product Image schemas
class ProductImageBase(BaseModel):
    image_url: str
    is_primary: Optional[bool] = False
    display_order: Optional[int] = 0


class ProductImageCreate(ProductImageBase):
    pass


class ProductImageResponse(ProductImageBase, BaseResponse):
    id: int
    product_id: int
    created_at: datetime


# Product schemas
class ProductBase(BaseModel):
    name: str
    slug: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    mrp: Decimal
    selling_price: Decimal
    discount_percentage: Optional[Decimal] = None
    stock_quantity: Optional[int] = 0
    sku: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    material: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None
    is_featured: Optional[bool] = False
    is_active: Optional[bool] = True
    allow_cod: Optional[bool] = False
    shipping_charge: Optional[Decimal] = Decimal(0)
    free_shipping_above: Optional[Decimal] = None


class ProductCreate(ProductBase):
    category_id: Optional[int] = None
    image_urls: Optional[List[str]] = None  # List of image URLs to add
    
    @validator('category_id')
    def validate_category_id(cls, v):
        if v == 0:
            return None
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    category_id: Optional[int] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    mrp: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    discount_percentage: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    sku: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    material: Optional[str] = None
    meta_description: Optional[str] = None
    tags: Optional[str] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    allow_cod: Optional[bool] = None
    shipping_charge: Optional[Decimal] = None
    free_shipping_above: Optional[Decimal] = None


class ProductResponse(ProductBase, BaseResponse):
    id: int
    category_id: Optional[int] = None
    category: Optional[ProductCategoryResponse] = None
    images: List[ProductImageResponse] = []
    total_sales: int
    created_at: datetime
    updated_at: datetime


class ProductListResponse(BaseResponse):
    id: int
    name: str
    slug: str
    short_description: Optional[str] = None
    mrp: Decimal
    selling_price: Decimal
    discount_percentage: Optional[Decimal] = None
    stock_quantity: int
    is_featured: bool
    is_active: bool
    category: Optional[ProductCategoryResponse] = None
    images: List[ProductImageResponse] = []
    created_at: datetime


# Promo Code schemas
class PromoCodeBase(BaseModel):
    code: str
    description: Optional[str] = None
    discount_type: str  # "percentage" or "fixed"
    discount_value: Decimal
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = 1
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    applicable_to_products: Optional[bool] = True
    applicable_to_pujas: Optional[bool] = False
    is_active: Optional[bool] = True


class PromoCodeCreate(PromoCodeBase):
    pass


class PromoCodeUpdate(BaseModel):
    code: Optional[str] = None
    description: Optional[str] = None
    discount_type: Optional[str] = None
    discount_value: Optional[Decimal] = None
    max_uses: Optional[int] = None
    max_uses_per_user: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    min_order_amount: Optional[Decimal] = None
    max_discount_amount: Optional[Decimal] = None
    applicable_to_products: Optional[bool] = None
    applicable_to_pujas: Optional[bool] = None
    is_active: Optional[bool] = None


class PromoCodeResponse(PromoCodeBase, BaseResponse):
    id: int
    current_uses: int
    created_at: datetime
    updated_at: datetime


class PromoCodeValidate(BaseModel):
    code: str
    order_amount: Decimal
    is_product_order: Optional[bool] = True


class PromoCodeValidateResponse(BaseModel):
    valid: bool
    message: str
    discount_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None


# Order schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(BaseResponse):
    id: int
    order_id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    created_at: datetime


class OrderBase(BaseModel):
    shipping_name: str
    shipping_mobile: str
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_pincode: str
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    items: List[OrderItemCreate]
    promo_code: Optional[str] = None
    payment_method: str = "online"  # online or cod
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in ["online", "cod"]:
            raise ValueError('payment_method must be "online" or "cod"')
        return v


class OrderUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    tracking_number: Optional[str] = None
    notes: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class OrderResponse(OrderBase, BaseResponse):
    id: int
    user_id: int
    order_number: str
    subtotal: Decimal
    discount_amount: Decimal
    shipping_charges: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    status: str
    payment_status: str
    payment_method: str
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    promo_code: Optional[PromoCodeResponse] = None
    order_items: List[OrderItemResponse] = []


class OrderListResponse(BaseResponse):
    id: int
    user_id: int
    order_number: str
    total_amount: Decimal
    status: str
    payment_status: str
    created_at: datetime


# Order Payment schemas
class OrderPaymentCreate(BaseModel):
    order_id: int
    amount: Decimal


class OrderPaymentResponse(BaseResponse):
    id: int
    order_id: int
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount: Decimal
    currency: str
    status: str
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Resolve forward references for Pydantic models that reference each other
BookingResponse.update_forward_refs()
PujaResponse.update_forward_refs()
TempleResponse.update_forward_refs()
