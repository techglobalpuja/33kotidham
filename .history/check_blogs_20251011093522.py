import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Blog
from app.config import settings

def check_blogs():
    # Database setup
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        total_blogs = db.query(Blog).count()
        active_blogs = db.query(Blog).filter(Blog.is_active == True).count()
        
        print(f"Total blogs in database: {total_blogs}")
        print(f"Active blogs: {active_blogs}")
        
        # Check inactive blogs
        inactive_blogs = db.query(Blog).filter(Blog.is_active == False).count()
        print(f"Inactive blogs: {inactive_blogs}")
        
        # Check blogs with future publish times
        from datetime import datetime
        future_blogs = db.query(Blog).filter(
            Blog.is_active == True,
            Blog.publish_time != None,
            Blog.publish_time > datetime.now()
        ).count()
        print(f"Blogs scheduled for future publishing: {future_blogs}")
        
        # Show details of all blogs
        print("\nBlog details:")
        blogs = db.query(Blog).order_by(Blog.created_at.desc()).all()
        for blog in blogs:
            print(f"ID: {blog.id}, Title: {blog.title}, Active: {blog.is_active}, Publish Time: {blog.publish_time}, Created At: {blog.created_at}")
            
    except Exception as e:
        print(f"Error checking blogs: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_blogs()