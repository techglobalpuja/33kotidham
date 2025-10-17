from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import schemas, crud
from app.auth import get_admin_user, get_current_active_user
from app.models import User, Category

router = APIRouter(prefix="/blogs", tags=["blogs"])


# Public endpoints for viewing blogs
@router.get("/", response_model=List[schemas.BlogListResponse])
def get_blogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # Changed default to 10 for better performance
    featured_only: bool = Query(False),
    category_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all published blogs (Public endpoint)."""
    blogs = crud.BlogCRUD.get_blogs(
        db, 
        skip=skip, 
        limit=limit,
        featured_only=featured_only,
        category_id=category_id,
        published_only=True
    )
    return blogs


@router.get("/search", response_model=List[schemas.BlogListResponse])
def search_blogs(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),  # Changed default to 10 for better performance
    db: Session = Depends(get_db)
):
    """Search blogs by title, subtitle, content, or tags (Public endpoint)."""
    blogs = crud.BlogCRUD.search_blogs(db, q, skip=skip, limit=limit)
    return blogs


@router.get("/featured", response_model=List[schemas.BlogListResponse])
def get_featured_blogs(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get featured blogs (Public endpoint)."""
    blogs = crud.BlogCRUD.get_blogs(db, skip=0, limit=limit, featured_only=True)
    return blogs


@router.get("/{blog_id}", response_model=schemas.BlogResponse)
def get_blog(blog_id: int, db: Session = Depends(get_db)):
    """Get blog by ID (Public endpoint)."""
    blog = crud.BlogCRUD.get_blog(db, blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    return blog


@router.get("/slug/{slug}", response_model=schemas.BlogResponse)
def get_blog_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get blog by slug (Public endpoint)."""
    blog = crud.BlogCRUD.get_blog_by_slug(db, slug)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    return blog


# Admin endpoints for managing blogs
@router.get("/admin/all", response_model=List[schemas.BlogResponse])
def get_all_blogs_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),  # Changed default to 50 for better performance
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Get all blogs including inactive and scheduled (Admin only)."""
    blogs = crud.BlogCRUD.get_admin_blogs(db, skip=skip, limit=limit)
    return blogs


@router.post("/", response_model=schemas.BlogResponse)
def create_blog(
    blog: schemas.BlogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new blog (Admin only)."""
    try:
        # Validate category IDs
        categories = db.query(Category).filter(Category.id.in_(blog.category_ids)).all()
        if len(categories) != len(blog.category_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more category IDs are invalid."
            )

        return crud.BlogCRUD.create_blog(db, blog, current_user.id, categories)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{blog_id}", response_model=schemas.BlogResponse)
def update_blog(
    blog_id: int,
    blog_update: schemas.BlogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update blog (Admin only)."""
    # Validate category IDs
    categories = db.query(Category).filter(Category.id.in_(blog_update.category_ids)).all()
    if len(categories) != len(blog_update.category_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more category IDs are invalid."
        )

    blog = crud.BlogCRUD.update_blog(db, blog_id, blog_update, categories)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    return blog


@router.delete("/{blog_id}")
def delete_blog(
    blog_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete blog (Admin only)."""
    success = crud.BlogCRUD.delete_blog(db, blog_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    return {"message": "Blog deleted successfully"}


# Category endpoints
@router.get("/categories/", response_model=List[schemas.CategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),  # Changed default to 50 for better performance
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all categories (Public endpoint)."""
    return crud.CategoryCRUD.get_categories(db, skip=skip, limit=limit, active_only=active_only)


@router.post("/categories/", response_model=schemas.CategoryResponse)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new category (Admin only)."""
    return crud.CategoryCRUD.create_category(db, category)


@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    category_update: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update category (Admin only)."""
    category = crud.CategoryCRUD.update_category(db, category_id, category_update)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete category (Admin only)."""
    success = crud.CategoryCRUD.delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return {"message": "Category deleted successfully"}