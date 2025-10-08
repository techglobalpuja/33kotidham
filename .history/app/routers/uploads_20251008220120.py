from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, crud
from app.auth import get_admin_user
from app.models import User
from app.utils import FileManager

router = APIRouter(prefix="/uploads", tags=["uploads"])


@router.post("/images", response_model=schemas.FileUploadResponse)
async def upload_image(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_admin_user)
):
    """Upload an image file (Admin only)."""
    try:
        file_path = await FileManager.upload_image(file, "images")
        # Return relative URL starting with uploads
        file_url = f"uploads{file_path}"
        
        return schemas.FileUploadResponse(
            filename=file.filename,
            file_url=file_url
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/puja-images/{puja_id}")
async def upload_puja_image(
    puja_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Upload image for a specific puja (Admin only)."""
    # Verify puja exists
    puja = crud.PujaCRUD.get_puja(db, puja_id)
    if not puja:
        raise HTTPException(status_code=404, detail="Puja not found")
    
    try:
        file_path = await FileManager.upload_image(file, f"pujas/{puja_id}")
        # Return relative URL starting with /uploads
        file_url = f"/uploads{file_path}"
        
        # Create puja image record
        from app.models import PujaImage
        puja_image = PujaImage(puja_id=puja_id, image_url=file_url)
        db.add(puja_image)
        db.commit()
        db.refresh(puja_image)
        
        return {
            "message": "Image uploaded successfully",
            "image_id": puja_image.id,
            "file_url": file_url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/puja-images/{image_id}")
def delete_puja_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete puja image (Admin only)."""
    from app.models import PujaImage
    
    puja_image = db.query(PujaImage).filter(PujaImage.id == image_id).first()
    if not puja_image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete file from filesystem
    file_path = puja_image.image_url.replace(str(request.base_url).rstrip('/'), '')
    FileManager.delete_image(file_path)
    
    # Delete database record
    db.delete(puja_image)
    db.commit()
    
    return {"message": "Image deleted successfully"}
