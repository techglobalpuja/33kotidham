from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas, crud
from app.auth import get_admin_user
from app.models import User

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("/", response_model=List[schemas.PlanResponse])
def get_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all plans (Public endpoint)."""
    return crud.PlanCRUD.get_plans(db, skip=skip, limit=limit)


@router.get("/{plan_id}", response_model=schemas.PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get plan by ID (Public endpoint)."""
    plan = crud.PlanCRUD.get_plan(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.post("/", response_model=schemas.PlanResponse)
def create_plan(
    plan: schemas.PlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new plan (Admin only)."""
    return crud.PlanCRUD.create_plan(db, plan)


@router.put("/{plan_id}", response_model=schemas.PlanResponse)
def update_plan(
    plan_id: int,
    plan_update: schemas.PlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update plan (Admin only)."""
    plan = crud.PlanCRUD.update_plan(db, plan_id, plan_update)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.delete("/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete plan (Admin only)."""
    success = crud.PlanCRUD.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return {"message": "Plan deleted successfully"}
