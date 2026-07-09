from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.sql import company as company_model
from app.models.sql import user as user_model
from app.models.sql.invoicing import Invoice as inv_model, InvoiceItem as inv_item_model
from app.schemas import invoicing as inv_schema
from app.services import invoicing_service
from app.services import credit_debit_note_service as cdn_service
from app.core.database import get_db
from app.api.v1.deps import get_current_user, verify_company_membership, require_permission

router = APIRouter()


@router.post(
    "/", response_model=inv_schema.InvoiceResponse, status_code=status.HTTP_201_CREATED
)
def create_invoice(
    invoice: inv_schema.InvoiceCreate,
    company_id: int,
    company: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
    permission: user_model.User = Depends(require_permission('invoicing','create')),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    # The plain invoice creation endpoint is deprecated.  All invoices must include items.
    # Enforce usage of the "/with-items/" endpoint.
    raise HTTPException(status_code=400, detail="Use POST /with-items/ to create invoices with items.")


@router.post(
    "/with-items/",
    response_model=inv_schema.InvoiceWithItemsResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_invoice_with_items(
    invoice_with_items: inv_schema.InvoiceWithItemsCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = invoicing_service.InvoicingService(db)
    try:
        return service.create_invoice_with_items(invoice_with_items, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[inv_schema.InvoiceResponse])
def read_invoices(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = invoicing_service.InvoicingService(db)
    return service.get_invoices(company_id, skip=skip, limit=limit)


@router.get("/{invoice_id}", response_model=inv_schema.InvoiceWithItemsResponse)
def read_invoice(
    invoice_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = invoicing_service.InvoicingService(db)
    db_invoice = service.get_invoice_with_items(invoice_id, company_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


@router.put("/{invoice_id}", response_model=inv_schema.InvoiceResponse)
def update_invoice(
    invoice_id: int,
    invoice: inv_schema.InvoiceCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = invoicing_service.InvoicingService(db)
    db_invoice = service.update_invoice(invoice_id, invoice, company_id)
    if db_invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return db_invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = invoicing_service.InvoicingService(db)
    success = service.delete_invoice(invoice_id, company_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return None


@router.post("/{invoice_id}/cancel", response_model=inv_schema.InvoiceResponse)
def cancel_invoice(
    invoice_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    """
    Cancel an invoice and reverse its effects (inventory, accounting, treasury)
    """
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = invoicing_service.InvoicingService(db)
    try:
        return service.cancel_invoice(invoice_id, company_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error cancelling invoice: {str(e)}"
        )


# Credit / Debit Note endpoints
@router.post(
    "/credit-debit-notes/",
    response_model=inv_schema.CreditDebitNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_credit_debit_note(
    note_data: inv_schema.CreditDebitNoteCreate,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = cdn_service.CreditDebitNoteService(db)
    try:
        note = service.create_note(note_data, company_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return note


@router.get(
    "/credit-debit-notes/", response_model=List[inv_schema.CreditDebitNoteResponse]
)
def list_credit_debit_notes(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = cdn_service.CreditDebitNoteService(db)
    return service.get_notes(company_id, skip=skip, limit=limit)


@router.get(
    "/credit-debit-notes/{note_id}", response_model=inv_schema.CreditDebitNoteResponse
)
def get_credit_debit_note(
    note_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = cdn_service.CreditDebitNoteService(db)
    note = service.get_note_by_id(note_id, company_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.get(
    "/invoices/{invoice_id}/credit-debit-notes/",
    response_model=List[inv_schema.CreditDebitNoteResponse],
)
def get_notes_by_invoice(
    invoice_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = cdn_service.CreditDebitNoteService(db)
    return service.get_notes_by_invoice(invoice_id, company_id)


@router.post("/credit-debit-notes/{note_id}/generate-xml")
def generate_note_xml(
    note_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = cdn_service.CreditDebitNoteService(db)
    try:
        result = service.generate_xml_and_cufe(note_id, company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result


@router.post("/credit-debit-notes/{note_id}/send-to-dian")
def send_note_to_dian(
    note_id: int,
    company_id: int,
    company_dep: company_model.Company = Depends(verify_company_membership),
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    db_company = (
        db.query(company_model.Company)
        .filter(company_model.Company.id == company_id)
        .first()
    )
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    service = cdn_service.CreditDebitNoteService(db)
    try:
        result = service.send_to_dian(note_id, company_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return result
