from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas, crud
from app.auth import get_admin_user
from app.models import User

router = APIRouter(prefix="/chadawas", tags=["chadawas"])


@router.get("/", response_model=List[schemas.ChadawaResponse])
def get_chadawas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all chadawas (Public endpoint)."""
    return crud.ChadawaCRUD.get_chadawas(db, skip=skip, limit=limit)


@router.get("/{chadawa_id}", response_model=schemas.ChadawaResponse)
def get_chadawa(chadawa_id: int, db: Session = Depends(get_db)):
    """Get chadawa by ID (Public endpoint)."""
    chadawa = crud.ChadawaCRUD.get_chadawa(db, chadawa_id)
    if not chadawa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa not found"
        )
    return chadawa


@router.post("/", response_model=schemas.ChadawaResponse)
def create_chadawa(
    chadawa: schemas.ChadawaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new chadawa (Admin only)."""
    return crud.ChadawaCRUD.create_chadawa(db, chadawa)


@router.put("/{chadawa_id}", response_model=schemas.ChadawaResponse)
def update_chadawa(
    chadawa_id: int,
    chadawa_update: schemas.ChadawaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update chadawa (Admin only)."""
    chadawa = crud.ChadawaCRUD.update_chadawa(db, chadawa_id, chadawa_update)
    if not chadawa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa not found"
        )
    return chadawa


@router.delete("/{chadawa_id}")
def delete_chadawa(
    chadawa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete chadawa (Admin only)."""
    success = crud.ChadawaCRUD.delete_chadawa(db, chadawa_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chadawa not found"
        )
    return {"message": "Chadawa deleted successfully"}
