import logging
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

logger = logging.getLogger("app")

from app.models.sql import company as company_model
from app.models.sql import user as user_model
from app.schemas import company as company_schema
from app.schemas import dian_billing as db_schema
from app.core.database import get_db
from app.core import security
from app.core.config import settings
from app.services import accounting_service
from app.services import dian_billing_range_service as dbr_service
from app.api.v1.deps import get_current_user

router = APIRouter()


@router.post(
    "/",
    response_model=company_schema.CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    company: company_schema.CompanyCreate, db: Session = Depends(get_db)
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.nit == company.nit)
        .first()
    )
    if db_company:
        raise HTTPException(
            status_code=400, detail="Company with this NIT already exists"
        )

    company_data = company.model_dump(exclude={"admin_user"})
    db_company = company_model.Company(**company_data)
    db.add(db_company)
    db.flush()

    if company.admin_user:
        existing = (
            db.query(user_model.User)
            .filter(
                (user_model.User.email == company.admin_user.email)
                | (user_model.User.username == company.admin_user.username)
            )
            .first()
        )
        if existing:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="User email or username already exists",
            )
        hashed_password = security.get_password_hash(company.admin_user.password)
        admin = user_model.User(
            email=company.admin_user.email,
            username=company.admin_user.username,
            hashed_password=hashed_password,
            full_name=company.admin_user.full_name,
            is_active=True,
            is_superuser=True,
            role="ADMINISTRADOR",
            company_id=db_company.id,
        )
        db.add(admin)

    db.commit()
    db.refresh(db_company)

    accounting_svc = accounting_service.AccountingService(db)
    accounting_svc.create_default_chart_of_accounts(db_company.id)

    return db_company


@router.post("/{company_id}/logo")
def upload_company_logo(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG and WebP images are allowed",
        )

    content = file.file.read()
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File size must be less than 2MB",
        )

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    logo_dir = os.path.join(settings.UPLOAD_DIR, "logos")
    try:
        os.makedirs(logo_dir, exist_ok=True)
    except PermissionError:
        logger.error(
            f"Permission denied creating logo directory '{logo_dir}'. "
            f"Ensure the directory exists and is writable by the application user."
        )
        raise HTTPException(
            status_code=500,
            detail="Server cannot save uploaded files. Contact the administrator to fix upload directory permissions.",
        )
    filepath = os.path.join(logo_dir, filename)

    with open(filepath, "wb") as f:
        f.write(content)

    db_company.logo_url = f"/uploads/logos/{filename}"
    db.commit()
    db.refresh(db_company)

    return {"logo_url": db_company.logo_url}


@router.get("/", response_model=List[company_schema.CompanyResponse])
def read_companies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    companies = db.query(company_model.Company).offset(skip).limit(limit).all()
    return companies


@router.get("/{company_id}", response_model=company_schema.CompanyResponse)
def read_company(company_id: int, db: Session = Depends(get_db)):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    return db_company


@router.put("/{company_id}", response_model=company_schema.CompanyResponse)
def update_company(
    company_id: int,
    company: company_schema.CompanyBase,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    company_data = company.model_dump()
    for key, value in company_data.items():
        setattr(db_company, key, value)

    db.commit()
    db.refresh(db_company)
    return db_company


# Dian Billing Range endpoints
@router.post(
    "/{company_id}/billing-ranges/",
    response_model=db_schema.DianBillingRangeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_billing_range(
    company_id: int,
    range_data: db_schema.DianBillingRangeCreate,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")

    service = dbr_service.DianBillingRangeService(db)
    return service.create_range(range_data, company_id)


@router.get(
    "/{company_id}/billing-ranges/",
    response_model=List[db_schema.DianBillingRangeResponse],
)
def list_billing_ranges(
    company_id: int,
    active: bool = False,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    service = dbr_service.DianBillingRangeService(db)
    if active:
        return service.get_active_ranges(company_id)
    return service.get_ranges(company_id)


@router.get("/{company_id}/billing-ranges/next-number/")
def get_next_billing_number(
    company_id: int,
    prefix: str,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    service = dbr_service.DianBillingRangeService(db)
    next_num = service.get_next_number(company_id, prefix)
    if next_num is None:
        raise HTTPException(
            status_code=404,
            detail="No active billing range found for this prefix",
        )
    return {"next_number": next_num, "prefix": prefix}


@router.post("/{company_id}/billing-ranges/{range_id}/consume/")
def consume_billing_number(
    company_id: int,
    range_id: int,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    service = dbr_service.DianBillingRangeService(db)
    success = service.consume_number(range_id, company_id)
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to consume number (range exhausted or not found)",
        )
    return {"message": "Number consumed successfully"}
