from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas, crud
from app.auth import get_admin_user, get_current_active_user
from app.models import User

router = APIRouter(prefix="/temples", tags=["temples"])


@router.get("/", response_model=List[schemas.TempleResponse])
def get_temples(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return crud.TempleCRUD.get_temples(db, skip=skip, limit=limit)


@router.get("/{temple_id}", response_model=schemas.TempleResponse)
def get_temple(temple_id: int, db: Session = Depends(get_db)):
    temple = crud.TempleCRUD.get_temple(db, temple_id)
    if not temple:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")
    return temple


@router.post("/", response_model=schemas.TempleResponse)
def create_temple(
    temple: schemas.TempleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    return crud.TempleCRUD.create_temple(db, temple)


@router.put("/{temple_id}", response_model=schemas.TempleResponse)
def update_temple(
    temple_id: int,
    temple_update: schemas.TempleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    temple = crud.TempleCRUD.update_temple(db, temple_id, temple_update)
    if not temple:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")
    return temple


@router.delete("/{temple_id}")
def delete_temple(
    temple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    success = crud.TempleCRUD.delete_temple(db, temple_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")
    return {"message": "Temple deleted successfully"}


@router.post("/{temple_id}/recommended", response_model=schemas.TempleResponse)
def set_recommended_pujas(
    temple_id: int,
    puja_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    temple = crud.TempleCRUD.set_recommended_pujas(db, temple_id, puja_ids)
    if not temple:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temple not found")
    return temple
