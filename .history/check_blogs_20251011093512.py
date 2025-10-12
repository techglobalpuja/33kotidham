import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Blog

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Database setup (adjust this according to your actual database configuration)
DATABASE_URL = "sqlite:///./test.db"  # Adjust this to your actual database URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        pass

def check_blogs():
    db = get_db()
    try:
        total_blogs = db.query(Blog).count()
        active_blogs = db.query(Blog).filter(Blog.is_active == True).count()
        
        print(f"Total blogs in database: {total_blogs}")
        print(f"Active blogs: {active_blogs}")
        
        # Check inactive blogs
        inactive_blogs = db.query(Blog).filter(Blog.is_active == False).count()
        print(f"Inactive blogs: {inactive_blogs}")
        
        # Show details of all blogs
        print("\nBlog details:")
        blogs = db.query(Blog).all()
        for blog in blogs:
            print(f"ID: {blog.id}, Title: {blog.title}, Active: {blog.is_active}, Publish Time: {blog.publish_time}")
            
    except Exception as e:
        print(f"Error checking blogs: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_blogs()