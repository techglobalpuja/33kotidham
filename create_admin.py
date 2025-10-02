#!/usr/bin/env python3
"""
Script to create a super admin user
"""

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas, crud
from app.models import UserRole

def create_super_admin():
    """Create a super admin user."""
    db: Session = SessionLocal()
    
    try:
        # Check if super admin already exists
        existing_admin = db.query(crud.models.User).filter(
            crud.models.User.role == UserRole.SUPER_ADMIN.value
        ).first()
        
        if existing_admin:
            print(f"Super admin already exists: {existing_admin.name} ({existing_admin.mobile})")
            return
        
        # Create super admin
        admin_data = schemas.UserCreate(
            name="Super Admin",
            email="admin@33kotidham.com",
            mobile="+919999999999",
            password="admin123",  # Simple password for development
            role=UserRole.SUPER_ADMIN
        )
        
        admin_user = crud.UserCRUD.create_user(db, admin_data)
        print(f"Super admin created successfully!")
        print(f"Name: {admin_user.name}")
        print(f"Email: {admin_user.email}")
        print(f"Mobile: {admin_user.mobile}")
        print(f"Role: {admin_user.role}")
        print(f"Active: {admin_user.is_active}")
        
    except Exception as e:
        print(f"Error creating super admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_super_admin()
