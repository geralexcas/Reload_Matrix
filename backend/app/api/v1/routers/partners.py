from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.sql import company as company_model
from app.models.sql import user as user_model
from app.models.sql import partners as partner_model
from app.schemas import partners as partner_schema
from app.services import partner_service
from app.core.database import get_db
from app.api.v1.deps import verify_company_membership, require_permission

router = APIRouter()


# Partner endpoints
@router.post(
    "/",
    response_model=partner_schema.PartnerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_partner(
    partner: partner_schema.PartnerCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("partners", "create")),
):
    """
    Create a new partner (supplier or customer).
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = partner_service.PartnerService(db)
    try:
        created_partner = service.create_partner(partner, company_id)
        
        # Additional verification: ensure the partner can be retrieved
        verify_partner = (
            db.query(partner_model.Partner)
            .filter(
                partner_model.Partner.id == created_partner.id,
                partner_model.Partner.company_id == company_id
            )
            .first()
        )
        
        if not verify_partner:
            # Log the issue for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Partner creation verification failed for partner_id={created_partner.id}, company_id={company_id}")
            raise HTTPException(
                status_code=500, 
                detail="Partner creation failed: unable to verify record in database"
            )
            
        return created_partner
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch any other database errors
        raise HTTPException(
            status_code=500, 
            detail=f"Database error: {str(e)}"
        )


@router.get("/", response_model=List[partner_schema.PartnerResponse])
def read_partners(
    company_id: int,
    skip: int = 0,
    limit: int = 1000,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("partners", "read")),
):
    """
    Retrieve partners for a company.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = partner_service.PartnerService(db)
    return service.get_partners(company_id, skip=skip, limit=limit)


@router.get("/{partner_id}", response_model=partner_schema.PartnerResponse)
def read_partner(
    partner_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("partners", "read")),
):
    """
    Retrieve a specific partner.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = partner_service.PartnerService(db)
    db_partner = service.get_partner_by_id(partner_id, company_id)
    if db_partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return db_partner


@router.put("/{partner_id}", response_model=partner_schema.PartnerResponse)
def update_partner(
    partner_id: int,
    partner: partner_schema.PartnerCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("partners", "update")),
):
    """
    Update a partner.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = partner_service.PartnerService(db)
    db_partner = service.update_partner(partner_id, partner, company_id)
    if db_partner is None:
        raise HTTPException(status_code=404, detail="Partner not found")
    return db_partner


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_partner(
    partner_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("partners", "delete")),
):
    """
    Delete a partner.
    """
    # Verify company exists
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = partner_service.PartnerService(db)
    success = service.delete_partner(partner_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Partner not found")
    return None
