from decouple import config
from typing import List

class Settings:
    # Database
    DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./33kotidham.db")
    
    # JWT
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-change-this-in-production")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # Razorpay
    RAZORPAY_KEY_ID: str = config("RAZORPAY_KEY_ID", default="")
    RAZORPAY_KEY_SECRET: str = config("RAZORPAY_KEY_SECRET", default="")
    
    # Twilio
    TWILIO_ACCOUNT_SID: str = config("TWILIO_ACCOUNT_SID", default="")
    TWILIO_AUTH_TOKEN: str = config("TWILIO_AUTH_TOKEN", default="")
    TWILIO_PHONE_NUMBER: str = config("TWILIO_PHONE_NUMBER", default="")
    TWILIO_WHATSAPP_NUMBER: str = config("TWILIO_WHATSAPP_NUMBER", default="whatsapp:+19804808487")
    
    # WhatsApp Template SIDs (Content Templates)
    WHATSAPP_TEMPLATE_BOOKING_PENDING: str = config("WHATSAPP_TEMPLATE_BOOKING_PENDING", default="")
    WHATSAPP_TEMPLATE_BOOKING_CONFIRMED: str = config("WHATSAPP_TEMPLATE_BOOKING_CONFIRMED", default="")
    WHATSAPP_TEMPLATE_TEMPLE_BOOKING: str = config("WHATSAPP_TEMPLATE_TEMPLE_BOOKING", default="")
    
    # SMS Provider Selection
    SMS_PROVIDER: str = config("SMS_PROVIDER", default="auto")  # auto, twilio, msg91
    
    # MSG91 (Indian SMS Service)
    MSG91_API_KEY: str = config("MSG91_API_KEY", default="")
    MSG91_TEMPLATE_ID: str = config("MSG91_TEMPLATE_ID", default="")
    MSG91_SENDER_ID: str = config("MSG91_SENDER_ID", default="33KOTI")
    
    # Redis
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379")
    
    # Email
    SMTP_HOST: str = config("SMTP_HOST", default="smtp.gmail.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USERNAME: str = config("SMTP_USERNAME", default="")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", default="")
    SMTP_FROM_EMAIL: str = config("SMTP_FROM_EMAIL", default="")
    
    # WhatsApp
    WHATSAPP_ENABLED: bool = config("WHATSAPP_ENABLED", default=False, cast=bool)
    WHATSAPP_API_URL: str = config("WHATSAPP_API_URL", default="https://graph.instagram.com/v18.0")
    WHATSAPP_PHONE_NUMBER_ID: str = config("WHATSAPP_PHONE_NUMBER_ID", default="")
    WHATSAPP_API_TOKEN: str = config("WHATSAPP_API_TOKEN", default="")
    
    # Notification Settings
    SEND_BOOKING_NOTIFICATIONS: bool = config("SEND_BOOKING_NOTIFICATIONS", default=True, cast=bool)
    SEND_EMAIL_ON_BOOKING: bool = config("SEND_EMAIL_ON_BOOKING", default=True, cast=bool)
    SEND_WHATSAPP_ON_BOOKING: bool = config("SEND_WHATSAPP_ON_BOOKING", default=False, cast=bool)
    
    # Application
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    ENVIRONMENT: str = config("ENVIRONMENT", default="production")
    
    # Security
    ALLOWED_HOSTS: List[str] = config("ALLOWED_HOSTS", default="*", cast=lambda v: [s.strip() for s in v.split(',')])
    
    # Production Database
    PRODUCTION_DATABASE_URL: str = config("PRODUCTION_DATABASE_URL", default="")
    CORS_ORIGINS: List[str] = config("CORS_ORIGINS", default="http://localhost:3000,http://localhost:8080,https://api.33kotidham.in,https://api.33kotidham.com,https://33kotidham.com").split(",")
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # Shipping Configuration
    SHIPPING_CHARGE: int = config("SHIPPING_CHARGE", default=50, cast=int)
    FREE_SHIPPING_THRESHOLD: int = config("FREE_SHIPPING_THRESHOLD", default=500, cast=int)

settings = Settings()
