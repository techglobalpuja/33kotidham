#!/usr/bin/env python3
"""
Script to create a super admin user with properly hashed password
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt directly."""
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_super_admin():
    """Create a super admin user with hashed password."""
    db: Session = SessionLocal()
    
    try:
        # Check if super admin already exists
        existing_admin = db.query(User).filter(
            User.role == UserRole.SUPER_ADMIN.value
        ).first()
        
        if existing_admin:
            print(f"Super admin already exists: {existing_admin.name} ({existing_admin.mobile})")
            # Update existing admin with hashed password if it's null
            if existing_admin.password is None:
                hashed_password = hash_password("admin123")
                existing_admin.password = hashed_password
                db.commit()
                print("Updated existing admin with hashed password")
            return
        
        # Hash the password
        hashed_password = hash_password("admin123")
        
        # Create super admin with hashed password
        admin_user = User(
            name="Super Admin",
            email="admin@33kotidham.com",
            mobile="+919999999999",
            password=hashed_password,  # Properly hashed password
            role=UserRole.SUPER_ADMIN.value,
            is_active=True,  # Activate immediately
            email_verified=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"Super admin created successfully!")
        print(f"Name: {admin_user.name}")
        print(f"Email: {admin_user.email}")
        print(f"Mobile: {admin_user.mobile}")
        print(f"Role: {admin_user.role}")
        print(f"Active: {admin_user.is_active}")
        print(f"Password: admin123 (hashed in database)")
        print(f"Password hash: {admin_user.password[:50]}...")
        
    except Exception as e:
        print(f"Error creating super admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()
