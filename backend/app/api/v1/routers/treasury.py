from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.sql import company as company_model, user as user_model
from app.schemas import treasury as treasury_schema
from app.services import treasury_service
from app.core.database import get_db
from app.api.v1.deps import get_current_user

router = APIRouter()


def _verify_company(db: Session, company_id: int):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")


# ──────────────────────────────────────────────
# Bank Accounts
# ──────────────────────────────────────────────


@router.post(
    "/bank-accounts/",
    response_model=treasury_schema.BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_bank_account(
    data: treasury_schema.BankAccountCreate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.create_bank_account(data, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/bank-accounts/", response_model=List[treasury_schema.BankAccountResponse])
def get_bank_accounts(
    company_id: int = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_bank_accounts(company_id, skip=skip, limit=limit)


@router.get(
    "/bank-accounts/{bank_id}", response_model=treasury_schema.BankAccountResponse
)
def get_bank_account(
    bank_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    result = service.get_bank_account_by_id(bank_id, company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bank account not found")
    return result


@router.put(
    "/bank-accounts/{bank_id}", response_model=treasury_schema.BankAccountResponse
)
def update_bank_account(
    bank_id: int,
    data: treasury_schema.BankAccountUpdate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    result = service.update_bank_account(bank_id, data, company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Bank account not found")
    return result


@router.delete("/bank-accounts/{bank_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_bank_account(
    bank_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        success = service.deactivate_bank_account(bank_id, company_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bank account not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/bank-accounts/{bank_id}/transactions/",
    response_model=List[treasury_schema.TreasuryTransactionResponse],
)
def get_bank_account_transactions(
    bank_id: int,
    company_id: int = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_bank_account_transactions(
        bank_id, company_id, skip=skip, limit=limit
    )


# ──────────────────────────────────────────────
# Cash Accounts
# ──────────────────────────────────────────────


@router.post(
    "/cash-accounts/",
    response_model=treasury_schema.CashAccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_cash_account(
    data: treasury_schema.CashAccountCreate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.create_cash_account(data, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cash-accounts/", response_model=List[treasury_schema.CashAccountResponse])
def get_cash_accounts(
    company_id: int = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_cash_accounts(company_id, skip=skip, limit=limit)


@router.get(
    "/cash-accounts/{cash_id}", response_model=treasury_schema.CashAccountResponse
)
def get_cash_account(
    cash_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    result = service.get_cash_account_by_id(cash_id, company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cash account not found")
    return result


@router.put(
    "/cash-accounts/{cash_id}", response_model=treasury_schema.CashAccountResponse
)
def update_cash_account(
    cash_id: int,
    data: treasury_schema.CashAccountUpdate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    result = service.update_cash_account(cash_id, data, company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Cash account not found")
    return result


@router.delete("/cash-accounts/{cash_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_cash_account(
    cash_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        success = service.deactivate_cash_account(cash_id, company_id)
        if not success:
            raise HTTPException(status_code=404, detail="Cash account not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/cash-accounts/{cash_id}/transactions/",
    response_model=List[treasury_schema.TreasuryTransactionResponse],
)
def get_cash_account_transactions(
    cash_id: int,
    company_id: int = Query(...),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_cash_account_transactions(
        cash_id, company_id, skip=skip, limit=limit
    )


# ──────────────────────────────────────────────
# Operations: Deposit, Withdrawal, Transfer
# ──────────────────────────────────────────────


@router.post(
    "/deposit/",
    response_model=treasury_schema.TreasuryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def deposit(
    data: treasury_schema.DepositRequest,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.deposit(
            account_type=data.account_type,
            account_id=data.account_id,
            amount=data.amount,
            description=data.description or "",
            reference=data.reference or "",
            company_id=company_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/withdraw/",
    response_model=treasury_schema.TreasuryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def withdraw(
    data: treasury_schema.WithdrawalRequest,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.withdraw(
            account_type=data.account_type,
            account_id=data.account_id,
            amount=data.amount,
            description=data.description or "",
            reference=data.reference or "",
            company_id=company_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/transfer/",
    response_model=List[treasury_schema.TreasuryTransactionResponse],
    status_code=status.HTTP_201_CREATED,
)
def transfer(
    data: treasury_schema.TransferRequest,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.transfer(
            from_account_type=data.from_account_type,
            from_account_id=data.from_account_id,
            to_account_type=data.to_account_type,
            to_account_id=data.to_account_id,
            amount=data.amount,
            description=data.description or "",
            reference=data.reference or "",
            company_id=company_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ──────────────────────────────────────────────
# Bank Fees & Interest
# ──────────────────────────────────────────────


@router.post(
    "/bank-accounts/{bank_id}/fee/",
    response_model=treasury_schema.TreasuryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_bank_fee(
    bank_id: int,
    amount: float = Query(..., gt=0),
    description: str = Query(""),
    reference: str = Query(""),
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.record_bank_fee(
            bank_account_id=bank_id,
            amount=amount,
            description=description,
            reference=reference,
            company_id=company_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/bank-accounts/{bank_id}/interest/",
    response_model=treasury_schema.TreasuryTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def record_bank_interest(
    bank_id: int,
    amount: float = Query(..., gt=0),
    description: str = Query(""),
    reference: str = Query(""),
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.record_bank_interest(
            bank_account_id=bank_id,
            amount=amount,
            description=description,
            reference=reference,
            company_id=company_id,
            user_id=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ──────────────────────────────────────────────
# Check Register
# ──────────────────────────────────────────────


@router.post(
    "/checks/",
    response_model=treasury_schema.CheckRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def issue_check(
    data: treasury_schema.CheckRegisterCreate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.issue_check(data, company_id, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/checks/", response_model=List[treasury_schema.CheckRegisterResponse])
def get_checks(
    company_id: int = Query(...),
    bank_account_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_checks(
        company_id,
        bank_account_id=bank_account_id,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.put(
    "/checks/{check_id}/status/", response_model=treasury_schema.CheckRegisterResponse
)
def update_check_status(
    check_id: int,
    data: treasury_schema.CheckStatusUpdate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        result = service.update_check_status(
            check_id, data.status, company_id, user_id=current_user.id
        )
        if not result:
            raise HTTPException(status_code=404, detail="Check not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ──────────────────────────────────────────────
# Summary & Reports
# ──────────────────────────────────────────────


@router.get("/summary/")
def get_treasury_summary(
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_treasury_summary(company_id)


@router.get("/cash-flow/")
def get_cash_flow(
    company_id: int = Query(...),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_cash_flow(company_id, date_from=date_from, date_to=date_to)


@router.get(
    "/transactions/", response_model=List[treasury_schema.TreasuryTransactionResponse]
)
def get_treasury_transactions(
    company_id: int = Query(...),
    account_type: Optional[str] = None,
    transaction_type: Optional[str] = None,
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_treasury_transactions(
        company_id,
        account_type=account_type,
        transaction_type=transaction_type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


# ──────────────────────────────────────────────
# Bank Reconciliation
# ──────────────────────────────────────────────


@router.post(
    "/reconciliations/",
    response_model=treasury_schema.BankReconciliationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reconciliation(
    data: treasury_schema.BankReconciliationCreate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.create_reconciliation(data, company_id, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/reconciliations/", response_model=List[treasury_schema.BankReconciliationResponse]
)
def get_reconciliations(
    company_id: int = Query(...),
    bank_account_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    return service.get_reconciliations(
        company_id, bank_account_id=bank_account_id, skip=skip, limit=limit
    )


@router.get(
    "/reconciliations/{recon_id}/",
    response_model=treasury_schema.BankReconciliationResponse,
)
def get_reconciliation(
    recon_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    result = service.get_reconciliation_by_id(recon_id, company_id)
    if not result:
        raise HTTPException(status_code=404, detail="Reconciliation not found")
    return result


@router.post(
    "/reconciliations/{recon_id}/match/",
    response_model=treasury_schema.ReconciliationLineResponse,
    status_code=status.HTTP_201_CREATED,
)
def match_transaction(
    recon_id: int,
    data: treasury_schema.MatchTransactionRequest,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.match_transaction(recon_id, data, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/reconciliations/{recon_id}/outstanding/",
    response_model=treasury_schema.ReconciliationLineResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_outstanding_item(
    recon_id: int,
    data: treasury_schema.AddOutstandingItemRequest,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.add_outstanding_item(recon_id, data, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/reconciliations/{recon_id}/complete/",
    response_model=treasury_schema.BankReconciliationResponse,
)
def complete_reconciliation(
    recon_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    _verify_company(db, company_id)
    service = treasury_service.TreasuryService(db)
    try:
        return service.complete_reconciliation(
            recon_id, company_id, user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
