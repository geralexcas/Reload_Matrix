from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.models.sql import company as company_model
from app.models.sql import user as user_model
from app.schemas import wallet as wallet_schema
from app.services import wallet_service
from app.core.database import get_db
from app.api.v1.deps import verify_company_membership, require_permission

router = APIRouter()


@router.post(
    "/",
    response_model=wallet_schema.WalletResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_wallet(
    wallet: wallet_schema.WalletCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "create")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    result = service.create_wallet(wallet, company_id)
    db.commit()
    return result


@router.get("/", response_model=List[wallet_schema.WalletResponse])
def read_wallets(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "read")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    return service.get_wallets(company_id, skip=skip, limit=limit)


@router.get("/{wallet_id}", response_model=wallet_schema.WalletWithTransactionsResponse)
def read_wallet(
    wallet_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "read")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    db_wallet = service.get_wallet_by_id(wallet_id, company_id)
    if db_wallet is None:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return db_wallet


@router.post(
    "/{wallet_id}/deposit",
    response_model=wallet_schema.WalletTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit_to_wallet(
    wallet_id: int,
    description: str,
    company_id: int,
    amount: Decimal = Query(..., gt=0),
    account_type: Optional[str] = None,
    account_id: Optional[int] = None,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "deposit")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    try:
        result = service.deposit(wallet_id, amount, description, company_id, current_user.id, account_type, account_id)
        db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{wallet_id}/withdraw",
    response_model=wallet_schema.WalletTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdraw_from_wallet(
    wallet_id: int,
    description: str,
    company_id: int,
    amount: Decimal = Query(..., gt=0),
    account_type: Optional[str] = None,
    account_id: Optional[int] = None,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "withdraw")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    try:
        result = service.withdraw(wallet_id, amount, description, company_id, current_user.id, account_type, account_id)
        db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{wallet_id}/transactions",
    response_model=List[wallet_schema.WalletTransactionResponse],
)
def read_wallet_transactions(
    wallet_id: int,
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "read")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    try:
        return service.get_transactions(wallet_id, company_id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{wallet_id}/loyalty/add")
def add_loyalty_points(
    wallet_id: int,
    points: float,
    company_id: int,
    description: str = "",
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "update")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    try:
        wallet = service.add_loyalty_points(
            wallet_id, Decimal(str(points)), company_id, description
        )
        db.commit()
        return {
            "wallet_id": wallet_id,
            "loyalty_points": float(wallet.loyalty_points or 0),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{wallet_id}/loyalty/redeem")
def redeem_loyalty_points(
    wallet_id: int,
    points: float,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "update")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    try:
        wallet = service.redeem_loyalty_points(
            wallet_id, Decimal(str(points)), company_id
        )
        db.commit()
        return {
            "wallet_id": wallet_id,
            "loyalty_points": float(wallet.loyalty_points or 0),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{wallet_id}/loyalty/summary")
def get_loyalty_summary(
    wallet_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(require_permission("wallet", "read")),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = wallet_service.WalletService(db)
    try:
        return service.get_loyalty_summary(wallet_id, company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
