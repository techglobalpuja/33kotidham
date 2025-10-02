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
    
    # Application
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    ENVIRONMENT: str = config("ENVIRONMENT", default="production")
    
    # Security
    ALLOWED_HOSTS: List[str] = config("ALLOWED_HOSTS", default="*", cast=lambda v: [s.strip() for s in v.split(',')])
    
    # Production Database
    PRODUCTION_DATABASE_URL: str = config("PRODUCTION_DATABASE_URL", default="")
    CORS_ORIGINS: List[str] = config("CORS_ORIGINS", default="http://localhost:3000,http://localhost:8080").split(",")
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

settings = Settings()
