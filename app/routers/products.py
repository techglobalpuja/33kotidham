from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import schemas, models
from app.auth import get_admin_user, get_current_active_user
from decimal import Decimal
from datetime import datetime

router = APIRouter(prefix="/products", tags=["products"])


# ==================== PRODUCT CATEGORIES ====================

@router.get("/categories", response_model=List[schemas.ProductCategoryResponse])
def get_product_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all product categories (Public endpoint)."""
    query = db.query(models.ProductCategory)
    
    if is_active is not None:
        query = query.filter(models.ProductCategory.is_active == is_active)
    
    categories = query.offset(skip).limit(limit).all()
    return categories


@router.get("/categories/{category_id}", response_model=schemas.ProductCategoryResponse)
def get_product_category(category_id: int, db: Session = Depends(get_db)):
    """Get product category by ID (Public endpoint)."""
    category = db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="Product category not found")
    
    return category


@router.post("/categories", response_model=schemas.ProductCategoryResponse)
def create_product_category(
    category: schemas.ProductCategoryCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Create a new product category (Admin only)."""
    # Check if category with same name exists
    existing = db.query(models.ProductCategory).filter(
        models.ProductCategory.name == category.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product category with this name already exists"
        )
    
    db_category = models.ProductCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/categories/{category_id}", response_model=schemas.ProductCategoryResponse)
def update_product_category(
    category_id: int,
    category: schemas.ProductCategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Update product category (Admin only)."""
    db_category = db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Product category not found")
    
    # Check name uniqueness if updating name
    if category.name and category.name != db_category.name:
        existing = db.query(models.ProductCategory).filter(
            models.ProductCategory.name == category.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Product category with this name already exists"
            )
    
    for key, value in category.dict(exclude_unset=True).items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Delete product category (Admin only)."""
    db_category = db.query(models.ProductCategory).filter(
        models.ProductCategory.id == category_id
    ).first()
    
    if not db_category:
        raise HTTPException(status_code=404, detail="Product category not found")
    
    db.delete(db_category)
    db.commit()
    return None


# ==================== PRODUCTS ====================

@router.get("/", response_model=List[schemas.ProductListResponse])
def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products with filters (Public endpoint)."""
    query = db.query(models.Product)
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(models.Product.is_active == is_active)
    
    if is_featured is not None:
        query = query.filter(models.Product.is_featured == is_featured)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (models.Product.name.ilike(search_pattern)) |
            (models.Product.short_description.ilike(search_pattern)) |
            (models.Product.tags.ilike(search_pattern))
        )
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product by ID (Public endpoint)."""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/slug/{slug}", response_model=schemas.ProductResponse)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get product by slug (Public endpoint)."""
    product = db.query(models.Product).filter(
        models.Product.slug == slug
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.post("/", response_model=schemas.ProductResponse)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Create a new product (Admin only)."""
    # Check if category exists if provided
    if product.category_id:
        category = db.query(models.ProductCategory).filter(
            models.ProductCategory.id == product.category_id
        ).first()
        if not category:
            raise HTTPException(
                status_code=404,
                detail=f"Product category with id {product.category_id} not found"
            )
    
    # Check if slug already exists
    existing = db.query(models.Product).filter(
        models.Product.slug == product.slug
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product with this slug already exists"
        )
    
    # Check SKU uniqueness if provided
    if product.sku:
        existing_sku = db.query(models.Product).filter(
            models.Product.sku == product.sku
        ).first()
        if existing_sku:
            raise HTTPException(
                status_code=400,
                detail="Product with this SKU already exists"
            )
    
    # Create product
    product_data = product.dict(exclude={"image_urls"})
    db_product = models.Product(**product_data)
    db.add(db_product)
    db.flush()  # Get product ID without committing
    
    # Add images if provided
    if product.image_urls:
        for idx, image_url in enumerate(product.image_urls):
            db_image = models.ProductImage(
                product_id=db_product.id,
                image_url=image_url,
                is_primary=(idx == 0),  # First image is primary
                display_order=idx
            )
            db.add(db_image)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.put("/{product_id}", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Update product (Admin only)."""
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if category exists if updating
    if product.category_id is not None:
        if product.category_id == 0:
            product.category_id = None
        elif product.category_id:
            category = db.query(models.ProductCategory).filter(
                models.ProductCategory.id == product.category_id
            ).first()
            if not category:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product category with id {product.category_id} not found"
                )
    
    # Check slug uniqueness if updating
    if product.slug and product.slug != db_product.slug:
        existing = db.query(models.Product).filter(
            models.Product.slug == product.slug
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Product with this slug already exists"
            )
    
    # Check SKU uniqueness if updating
    if product.sku and product.sku != db_product.sku:
        existing_sku = db.query(models.Product).filter(
            models.Product.sku == product.sku
        ).first()
        if existing_sku:
            raise HTTPException(
                status_code=400,
                detail="Product with this SKU already exists"
            )
    
    for key, value in product.dict(exclude_unset=True).items():
        setattr(db_product, key, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Delete product (Admin only)."""
    db_product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(db_product)
    db.commit()
    return None


# ==================== PRODUCT IMAGES ====================

@router.post("/{product_id}/images", response_model=schemas.ProductImageResponse)
def add_product_image(
    product_id: int,
    image: schemas.ProductImageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Add image to product (Admin only)."""
    product = db.query(models.Product).filter(
        models.Product.id == product_id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db_image = models.ProductImage(
        product_id=product_id,
        **image.dict()
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


@router.delete("/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Delete product image (Admin only)."""
    db_image = db.query(models.ProductImage).filter(
        models.ProductImage.id == image_id,
        models.ProductImage.product_id == product_id
    ).first()
    
    if not db_image:
        raise HTTPException(status_code=404, detail="Product image not found")
    
    db.delete(db_image)
    db.commit()
    return None


@router.put("/{product_id}/images/{image_id}/primary")
def set_primary_image(
    product_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_admin_user)
):
    """Set image as primary (Admin only)."""
    # Unset all primary images for this product
    db.query(models.ProductImage).filter(
        models.ProductImage.product_id == product_id
    ).update({"is_primary": False})
    
    # Set new primary image
    db_image = db.query(models.ProductImage).filter(
        models.ProductImage.id == image_id,
        models.ProductImage.product_id == product_id
    ).first()
    
    if not db_image:
        raise HTTPException(status_code=404, detail="Product image not found")
    
    db_image.is_primary = True
    db.commit()
    db.refresh(db_image)
    return {"message": "Primary image updated successfully"}
