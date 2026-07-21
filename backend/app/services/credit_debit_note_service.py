from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from decimal import Decimal

from app.models.sql.credit_debit_notes import CreditDebitNote
from app.models.sql.invoicing import Invoice
from app.schemas.invoicing import CreditDebitNoteCreate, CreditDebitNoteResponse
from app.services.electronic_billing_service import ElectronicBillingService


class CreditDebitNoteService:
    def __init__(self, db: Session):
        self.db = db

    def create_note(
        self, note_data: CreditDebitNoteCreate, company_id: int, user_id: int, commit: bool = False
    ) -> CreditDebitNote:
        invoice = (
            self.db.query(Invoice)
            .filter(
                Invoice.id == note_data.original_invoice_id,
                Invoice.company_id == company_id,
            )
            .first()
        )
        if not invoice:
            raise ValueError("Original invoice not found")

        if invoice.estado_dian != "ACEPTADO":
            raise ValueError("Can only create notes for invoices accepted by DIAN")

        prefix = "NC" if note_data.note_type == "CREDIT" else "ND"
        count = (
            self.db.query(CreditDebitNote)
            .filter(CreditDebitNote.company_id == company_id)
            .count()
        )
        note_number = f"{prefix}-{company_id:04d}-{count + 1:06d}"

        note = CreditDebitNote(
            company_id=company_id,
            original_invoice_id=note_data.original_invoice_id,
            note_type=note_data.note_type,
            reason=note_data.reason,
            amount=float(note_data.amount),
            note_number=note_number,
            estado_dian="BORRADOR",
        )
        self.db.add(note)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(note)
        return note

    def generate_xml_and_cufe(self, note_id: int, company_id: int, commit: bool = False) -> dict:
        note = (
            self.db.query(CreditDebitNote)
            .filter(
                CreditDebitNote.id == note_id,
                CreditDebitNote.company_id == company_id,
            )
            .first()
        )
        if not note:
            raise ValueError("Note not found")

        ebs = ElectronicBillingService(self.db)
        xml = ebs.generate_ubl_xml(note.original_invoice_id, company_id)
        if xml:
            note.xml_ubl = xml

        invoice = (
            self.db.query(Invoice)
            .filter(Invoice.id == note.original_invoice_id)
            .first()
        )
        if invoice and invoice.company:
            note.cufe = ebs.generate_cufe(
                company_nit=invoice.company.nit,
                company_dv=invoice.company.dv,
                invoice_number=note.note_number,
                invoice_date=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
                invoice_total=Decimal(str(note.amount)),
                company_regimen=invoice.company.regimen,
            )

        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(note)
        return {
            "note_id": note.id,
            "note_number": note.note_number,
            "cufe": note.cufe,
            "xml_generated": bool(note.xml_ubl),
        }

    def send_to_dian(self, note_id: int, company_id: int, commit: bool = False) -> dict:
        note = (
            self.db.query(CreditDebitNote)
            .filter(
                CreditDebitNote.id == note_id,
                CreditDebitNote.company_id == company_id,
            )
            .first()
        )
        if not note:
            raise ValueError("Note not found")

        if not note.xml_ubl or not note.cufe:
            self.generate_xml_and_cufe(note_id, company_id)

        note.estado_dian = "ENVIADO"
        note.fecha_envio_dian = datetime.now(timezone.utc)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(note)

        return {
            "success": True,
            "note_id": note.id,
            "estado_dian": note.estado_dian,
            "message": "Note sent to DIAN successfully",
        }

    def get_notes(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[CreditDebitNote]:
        return (
            self.db.query(CreditDebitNote)
            .filter(CreditDebitNote.company_id == company_id)
            .order_by(CreditDebitNote.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_note_by_id(
        self, note_id: int, company_id: int
    ) -> Optional[CreditDebitNote]:
        return (
            self.db.query(CreditDebitNote)
            .filter(
                CreditDebitNote.id == note_id,
                CreditDebitNote.company_id == company_id,
            )
            .first()
        )

    def get_notes_by_invoice(
        self, invoice_id: int, company_id: int
    ) -> List[CreditDebitNote]:
        return (
            self.db.query(CreditDebitNote)
            .filter(
                CreditDebitNote.original_invoice_id == invoice_id,
                CreditDebitNote.company_id == company_id,
            )
            .all()
        )
