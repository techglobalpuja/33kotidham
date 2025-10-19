from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import schemas, crud
from app.auth import get_admin_user, get_current_active_user
from app.models import User  # Import only User
from app import models  # Import the entire models module

router = APIRouter(prefix="/pujas", tags=["pujas"])


@router.get("/", response_model=List[schemas.PujaResponse])
def get_pujas(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all pujas (Public endpoint)."""
    return crud.PujaCRUD.get_pujas(db, skip=skip, limit=limit)


@router.get("/{puja_id}", response_model=schemas.PujaResponse)
def get_puja(puja_id: int, db: Session = Depends(get_db)):
    """Get puja by ID (Public endpoint)."""
    puja = db.query(models.Puja).filter(models.Puja.id == puja_id).first()
    if not puja:
        raise HTTPException(status_code=404, detail="Puja not found")

    # Populate plan_ids with the IDs of associated Plan objects
    puja_response = schemas.PujaResponse.from_orm(puja)
    puja_response.plan_ids = [plan.id for plan in puja.plan_ids]
    # Populate chadawas from association objects
    puja_response.chadawas = [schemas.ChadawaResponse.from_orm(pc.chadawa) for pc in puja.puja_chadawas]

    return puja_response


@router.post("/", response_model=schemas.PujaResponse)
def create_puja(
    puja: schemas.PujaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Create a new puja (Admin only)."""
    # Coerce category if client sent a comma-separated string
    if isinstance(puja.category, str):
        puja.category = [c.strip() for c in puja.category.split(',') if c.strip()]

    # Validate chadawa_ids if provided
    if getattr(puja, 'chadawa_ids', None):
        chadawas = db.query(models.Chadawa).filter(models.Chadawa.id.in_(puja.chadawa_ids)).all()
        if len(chadawas) != len(set(puja.chadawa_ids)):
            existing_ids = {c.id for c in chadawas}
            missing = [str(i) for i in puja.chadawa_ids if i not in existing_ids]
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid chadawa_ids: {', '.join(missing)}")

    created_puja = crud.PujaCRUD.create_puja(db, puja)

    # Associate plan_ids if provided
    if puja.plan_ids:
        for plan_id in puja.plan_ids:
            crud.PujaPlanCRUD.create_puja_plan(db, schemas.PujaPlanCreate(puja_id=created_puja.id, plan_id=plan_id))
    # Re-fetch the puja to include the updated plan and chadawa associations in the response
    created_puja = crud.PujaCRUD.get_puja(db, created_puja.id)

    # Build response model so nested chadawas list is populated correctly
    puja_response = schemas.PujaResponse.from_orm(created_puja)
    puja_response.plan_ids = [plan.id for plan in created_puja.plan_ids]
    puja_response.chadawas = [schemas.ChadawaResponse.from_orm(pc.chadawa) for pc in created_puja.puja_chadawas]

    return puja_response


@router.put("/{puja_id}", response_model=schemas.PujaResponse)
def update_puja(
    puja_id: int,
    puja_update: schemas.PujaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Update puja (Admin only)."""
    # allow comma-separated category input
    if hasattr(puja_update, 'category') and isinstance(puja_update.category, str):
        puja_update.category = [c.strip() for c in puja_update.category.split(',') if c.strip()]

    puja = crud.PujaCRUD.update_puja(db, puja_id, puja_update)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )

    # Update plan_ids if provided
    if puja_update.plan_ids is not None:
        crud.PujaPlanCRUD.update_puja_plans(db, puja_id, puja_update.plan_ids)
        # Re-fetch the puja so its relationships reflect the updated associations
        puja = crud.PujaCRUD.get_puja(db, puja_id)

    # Return a response model to populate nested chadawas and plan_ids
    puja_response = schemas.PujaResponse.from_orm(puja)
    puja_response.plan_ids = [plan.id for plan in puja.plan_ids]
    puja_response.chadawas = [schemas.ChadawaResponse.from_orm(pc.chadawa) for pc in puja.puja_chadawas]

    return puja_response


@router.delete("/{puja_id}")
def delete_puja(
    puja_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete puja (Admin only)."""
    success = crud.PujaCRUD.delete_puja(db, puja_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )

    # Delete associated PujaPlan entries
    crud.PujaPlanCRUD.delete_puja_plans(db, puja_id)

    return {"message": "Puja deleted successfully"}


# Puja Benefits endpoints
@router.get("/{puja_id}/benefits", response_model=List[schemas.PujaBenefitResponse])
def get_puja_benefits(puja_id: int, db: Session = Depends(get_db)):
    """Get benefits for a specific puja (Public endpoint)."""
    # Verify puja exists
    puja = crud.PujaCRUD.get_puja(db, puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    return crud.PujaBenefitCRUD.get_puja_benefits(db, puja_id)


@router.post("/{puja_id}/benefits", response_model=schemas.PujaBenefitResponse)
def create_puja_benefit(
    puja_id: int,
    benefit: schemas.PujaBenefitBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Add benefit to puja (Admin only)."""
    # Verify puja exists
    puja = crud.PujaCRUD.get_puja(db, puja_id)
    if not puja:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Puja not found"
        )
    
    benefit_data = schemas.PujaBenefitCreate(
        puja_id=puja_id,
        benefit_title=benefit.benefit_title,
        benefit_description=benefit.benefit_description
    )
    return crud.PujaBenefitCRUD.create_puja_benefit(db, benefit_data)


@router.delete("/benefits/{benefit_id}")
def delete_puja_benefit(
    benefit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Delete puja benefit (Admin only)."""
    success = crud.PujaBenefitCRUD.delete_puja_benefit(db, benefit_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benefit not found"
        )
    return {"message": "Benefit deleted successfully"}
