#!/usr/bin/env python3
"""
Script to list all available blog categories
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category

def list_categories():
    """List all available categories"""
    print("📂 Available Blog Categories:")
    print("=" * 50)
    
    db = next(get_db())
    try:
        categories = db.query(Category).filter(Category.is_active == True).all()
        
        if not categories:
            print("❌ No categories found. Please create some categories first.")
            return
        
        for category in categories:
            print(f"ID: {category.id:2d} | Name: {category.name}")
            if category.description:
                print(f"        Description: {category.description}")
            print("-" * 50)
        
        print(f"\n✅ Total categories: {len(categories)}")
        print("\n💡 Usage in API:")
        print("   - Use category_id: null for no category")
        print("   - Use category_id: <ID> to assign to a category")
        print("   - Don't use category_id: 0 (invalid)")
        
    except Exception as e:
        print(f"❌ Error fetching categories: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_categories()