from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.models.sql import company as company_model, user as user_model
from app.schemas import purchase as purchase_schema
from app.services import purchase_service
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


@router.post(
    "/",
    response_model=purchase_schema.PurchaseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase(
    purchase: purchase_schema.PurchaseWithItemsCreate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Create a new purchase invoice with items.
    This will automatically:
    - Update inventory if purchase is ISSUED/PAID/PARTIAL
    - Create accounting journal entry
    """
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    try:
        return service.create_purchase(purchase, company_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating purchase: {str(e)}"
        )


@router.post("/extract-from-pdf")
async def extract_from_pdf(
    file: UploadFile = File(...),
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Upload a purchase invoice PDF and extract supplier and items using Gemini.
    """
    _verify_company(db, company_id)
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un PDF")
        
    try:
        content = await file.read()
        service = purchase_service.PurchaseService(db)
        result = service.extract_from_pdf(content, company_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando PDF: {str(e)}")


@router.get("/", response_model=List[purchase_schema.PurchaseResponse])
def get_purchases(
    company_id: int = Query(...),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    partner_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """Get all purchases for a company with optional filters"""
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    return service.get_purchases(
        company_id, skip=skip, limit=limit, status=status, partner_id=partner_id
    )


@router.get("/statistics", response_model=purchase_schema.PurchaseStatistics)
def get_purchase_statistics(
    company_id: int = Query(...),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """Get purchase statistics for a company"""
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    return service.get_statistics(company_id, start_date=start_date, end_date=end_date)


@router.get("/accounts-payable")
def get_accounts_payable(
    company_id: int = Query(...),
    days_ahead: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Get accounts payable summary including overdue and upcoming due invoices.
    
    - days_ahead: Number of days to consider as 'upcoming' (default 7)
    Returns:
    - overdue_invoices: Invoices past due date
    - upcoming_invoices: Invoices due within days_ahead
    - pending_invoices: All other unpaid invoices
    - summary: Total amounts and counts
    """
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    return service.get_accounts_payable(company_id, days_ahead)


@router.get("/{purchase_id}", response_model=purchase_schema.PurchaseResponse)
def get_purchase(
    purchase_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """Get a specific purchase by ID"""
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    purchase = service.get_purchase_by_id(purchase_id, company_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")
    return purchase


@router.put("/{purchase_id}", response_model=purchase_schema.PurchaseResponse)
def update_purchase(
    purchase_id: int,
    purchase: purchase_schema.PurchaseUpdate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """Update a purchase"""
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    try:
        updated = service.update_purchase(purchase_id, purchase, company_id)
        if not updated:
            raise HTTPException(status_code=404, detail="Purchase not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{purchase_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase(
    purchase_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """Delete a purchase (only DRAFT status)"""
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    try:
        success = service.delete_purchase(purchase_id, company_id)
        if not success:
            raise HTTPException(status_code=404, detail="Purchase not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{purchase_id}/cancel", response_model=purchase_schema.PurchaseResponse)
def cancel_purchase(
    purchase_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Cancel a purchase and reverse its effects (inventory, accounting, treasury)
    """
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    try:
        return service.cancel_purchase(purchase_id, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error cancelling purchase: {str(e)}"
        )


@router.post(
    "/{purchase_id}/pay", response_model=purchase_schema.PurchasePaymentResponse
)
def register_payment(
    purchase_id: int,
    payment: purchase_schema.PurchasePaymentCreate,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Register a payment for a purchase.
    This will automatically:
    - Update purchase status (PAID/PARTIAL)
    - Create treasury transaction if not credit payment
    """
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    try:
        return service.register_payment(
            purchase_id, payment, company_id, current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{purchase_id}/balance")
def get_purchase_balance(
    purchase_id: int,
    company_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """Get the remaining balance for a purchase"""
    _verify_company(db, company_id)
    service = purchase_service.PurchaseService(db)
    purchase = service.get_purchase_by_id(purchase_id, company_id)
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase not found")

    balance = service.calculate_balance_due(purchase_id)
    return {
        "purchase_id": purchase_id,
        "total_amount": purchase.total_amount,
        "balance_due": balance,
    }
