from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app import schemas, crud
from app.auth import verify_password, create_access_token, get_current_active_user, get_super_admin_user
from app.config import settings
from app.models import User, UserRole

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user already exists
    if crud.UserCRUD.get_user_by_mobile(db, user.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    if user.email and crud.UserCRUD.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    return crud.UserCRUD.create_user(db, user)


@router.post("/register-with-otp")
def register_with_otp(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user and send OTP."""
    # Check if user already exists
    if crud.UserCRUD.get_user_by_mobile(db, user.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    if user.email and crud.UserCRUD.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    new_user = crud.UserCRUD.create_user(db, user)
    
    # Generate and send OTP
    otp = crud.OTPCRUD.create_otp(db, new_user.id)
    
    # Send OTP via SMS
    from app.services import notification_service
    sms_sent = notification_service.send_otp(new_user.mobile, otp.otp_code)
    
    if sms_sent:
        return {"message": "User registered successfully. OTP sent to your mobile number"}
    else:
        # For development - show OTP in response when SMS service is not configured
        from app.config import settings
        if settings.DEBUG:
            return {
                "message": "User registered. SMS service not configured. OTP for development:", 
                "otp": otp.otp_code,
                "note": "This OTP is shown only in DEBUG mode"
            }
        else:
            return {"message": "User registered. OTP generated but SMS service not configured."}


@router.post("/login", response_model=schemas.Token)
def login_user(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login with mobile and password."""
    user = crud.UserCRUD.get_user_by_mobile(db, user_credentials.mobile)
    
    if not user or not user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not verify_password(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mobile}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/admin-login", response_model=schemas.Token)
def admin_login(admin_credentials: schemas.AdminLogin, db: Session = Depends(get_db)):
    """Admin login with username (mobile/email) and password."""
    # Try to find user by mobile first, then by email
    user = crud.UserCRUD.get_user_by_mobile(db, admin_credentials.username)
    if not user:
        user = crud.UserCRUD.get_user_by_email(db, admin_credentials.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user has admin role
    if user.role not in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )
    
    # Verify password
    if not user.password or not verify_password(admin_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive admin account"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mobile, "role": user.role}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/create-admin", response_model=schemas.UserResponse)
def create_admin(
    admin_data: schemas.AdminCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin_user)
):
    """Create a new admin user. Only super admins can create other admins."""
    # Check if user already exists
    if crud.UserCRUD.get_user_by_mobile(db, admin_data.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    if admin_data.email and crud.UserCRUD.get_user_by_email(db, admin_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Convert AdminCreate to UserCreate
    user_create = schemas.UserCreate(
        name=admin_data.name,
        email=admin_data.email,
        mobile=admin_data.mobile,
        password=admin_data.password,
        role=admin_data.role
    )
    
    return crud.UserCRUD.create_user(db, user_create)


@router.post("/setup-super-admin", response_model=schemas.UserResponse)
def setup_super_admin(admin_data: schemas.AdminCreate, db: Session = Depends(get_db)):
    """Create the first super admin. Only works if no super admin exists."""
    # Check if any super admin already exists
    existing_super_admin = db.query(User).filter(User.role == UserRole.SUPER_ADMIN.value).first()
    if existing_super_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Super admin already exists. Use /create-admin endpoint instead."
        )
    
    # Check if user already exists
    if crud.UserCRUD.get_user_by_mobile(db, admin_data.mobile):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile number already registered"
        )
    
    if admin_data.email and crud.UserCRUD.get_user_by_email(db, admin_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Force role to be SUPER_ADMIN
    user_create = schemas.UserCreate(
        name=admin_data.name,
        email=admin_data.email,
        mobile=admin_data.mobile,
        password=admin_data.password,
        role=UserRole.SUPER_ADMIN
    )
    
    return crud.UserCRUD.create_user(db, user_create)


@router.post("/request-otp")
def request_otp(otp_request: schemas.OTPRequest, db: Session = Depends(get_db)):
    """Request OTP for mobile login."""
    user = crud.UserCRUD.get_user_by_mobile(db, otp_request.mobile)
    
    if not user:
        # Return message asking for registration details
        return {
            "message": "User not found. Please register first.",
            "requires_registration": True,
            "mobile": otp_request.mobile
        }
    
    # User exists, generate and send OTP
    otp = crud.OTPCRUD.create_otp(db, user.id)
    
    # Send OTP via SMS
    from app.services import notification_service
    sms_sent = notification_service.send_otp(user.mobile, otp.otp_code)
    
    if sms_sent:
        return {"message": "OTP sent successfully to your mobile number"}
    else:
        # For development - show OTP in response when SMS service is not configured
        from app.config import settings
        if settings.DEBUG:
            return {
                "message": "SMS service not configured. OTP for development:", 
                "otp": otp.otp_code,
                "note": "This OTP is shown only in DEBUG mode"
            }
        else:
            return {"message": "OTP generated but SMS service not configured."}


@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(otp_verify: schemas.OTPVerify, db: Session = Depends(get_db)):
    """Verify OTP and login."""
    user = crud.OTPCRUD.verify_otp(db, otp_verify.mobile, otp_verify.otp_code)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP"
        )
    
    if not user.is_active:
        # Activate user on first successful OTP verification
        crud.UserCRUD.update_user(db, user.id, schemas.UserUpdate(is_active=True))
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mobile}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.put("/me", response_model=schemas.UserResponse)
def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    return crud.UserCRUD.update_user(db, current_user.id, user_update)
