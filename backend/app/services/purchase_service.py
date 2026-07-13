from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict
from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, InvalidOperation
from app.models.sql.purchases import Purchase, PurchaseItem, PurchasePayment
from app.models.sql import company as company_model
from app.models.sql.partners import Partner
from app.schemas import purchase as purchase_schema
from app.services.inventory_service import InventoryService
from app.services.accounting_service import AccountingService
from app.models.sql.accounting.journal_entry import JournalEntry
import fitz
from google import genai
from google.genai import types
import json
from app.core.config import settings



class PurchaseService:
    def __init__(self, db: Session):
        self.db = db

    def _calculate_item_values(
        self, item: purchase_schema.PurchaseItemCreate, company_regimen: str
    ) -> dict:
        """Calculate item values including discounts and taxes"""
        try:
            quantity = Decimal(str(item.quantity)) if item.quantity is not None else Decimal("0.00")
            unit_price = Decimal(str(item.unit_price)) if item.unit_price is not None else Decimal("0.00")
            discount_percent = Decimal(str(item.discount_percent)) if item.discount_percent is not None else Decimal("0.00")
        except (ValueError, TypeError, InvalidOperation) as e:
            import logging
            logging.error(f"Error convirtiendo valores de ítem a Decimal: {e} - Item: {item}")
            raise ValueError(f"Valor numérico inválido en el ítem: {e}")

        subtotal = quantity * unit_price
        discount_amount = subtotal * (discount_percent / 100)
        subtotal_after_discount = subtotal - discount_amount

        tax_rate = Decimal(str(item.tax_rate))
        tax_amount = subtotal_after_discount * (tax_rate / 100)

        line_total = subtotal_after_discount + tax_amount

        return {
            "subtotal": subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "line_total": line_total,
        }

    def _get_company_regimen(self, company_id: int) -> str:
        """Get company's tax regimen"""
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        return company.regimen if company else "COMUN"

    def create_purchase(
        self,
        purchase_data: purchase_schema.PurchaseWithItemsCreate,
        company_id: int,
        user_id: int = None,
    ) -> Purchase:
        """Create a new purchase invoice with items"""
        # Verify purchase number doesn't already exist to prevent duplicates
        existing = self.db.query(Purchase).filter(
            Purchase.purchase_number == purchase_data.purchase_number,
            Purchase.company_id == company_id
        ).first()
        if existing:
            raise ValueError(f"Ya existe una compra con el número {purchase_data.purchase_number}. Use otro número o edite la compra existente.")

        # Verify company exists
        db_company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not db_company:
            raise ValueError("Company not found")

        # Verify partner exists
        db_partner = (
            self.db.query(Partner)
            .filter(Partner.id == purchase_data.partner_id)
            .first()
        )
        if not db_partner:
            raise ValueError("Supplier not found")

        # Get company regimen for tax calculation
        company_regimen = self._get_company_regimen(company_id)

        # Calculate totals from items
        total_subtotal = Decimal("0.00")
        total_tax = Decimal("0.00")
        total_discount = Decimal("0.00")

        calculated_items = []
        for item in purchase_data.items:
            values = self._calculate_item_values(item, company_regimen)
            total_subtotal += values["subtotal"] - values["discount_amount"]
            total_tax += values["tax_amount"]
            total_discount += values["discount_amount"]
            calculated_items.append((item, values))

        total_amount = total_subtotal + total_tax - purchase_data.discount_amount

        # Helper to parse date string to datetime
        def parse_date(date_val):
            if date_val is None:
                return None
            if isinstance(date_val, datetime):
                return date_val
            if isinstance(date_val, str) and date_val.strip():
                try:
                    return datetime.fromisoformat(date_val.replace("Z", "+00:00"))
                except:
                    try:
                        return datetime.strptime(date_val, "%Y-%m-%d")
                    except:
                        return None
            return None

        # Create purchase record
        db_purchase = Purchase(
            purchase_number=purchase_data.purchase_number,
            partner_id=purchase_data.partner_id,
            purchase_date=parse_date(purchase_data.purchase_date) or datetime.now(timezone.utc),
            due_date=parse_date(purchase_data.due_date),
            subtotal=total_subtotal,
            tax_amount=total_tax,
            discount_amount=purchase_data.discount_amount,
            total_amount=total_amount,
            currency=purchase_data.currency,
            payment_method=str(purchase_data.payment_method.value) if hasattr(purchase_data.payment_method, "value") else str(purchase_data.payment_method),
            status=str(purchase_data.status.value) if purchase_data.status and hasattr(purchase_data.status, "value") else (str(purchase_data.status) if purchase_data.status else purchase_schema.PurchaseStatusEnum.DRAFT.value),
            notes=purchase_data.notes,
            company_id=company_id,
            created_by=user_id,
        )

        self.db.add(db_purchase)
        
        from sqlalchemy.exc import IntegrityError
        try:
            self.db.flush()
        except IntegrityError as e:
            self.db.rollback()
            if 'uq_purchase_number_company' in str(e):
                raise ValueError(
                    f"Ya existe una compra con el número {purchase_data.purchase_number}. "
                    f"Si está intentando reintentar una operación fallida, use otro número."
                )
            raise

        # Create purchase items
        for item, values in calculated_items:
            db_item = PurchaseItem(
                purchase_id=db_purchase.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                serial_number=item.serial_number,
                discount_percent=item.discount_percent,
                discount_amount=values["discount_amount"],
                tax_rate=item.tax_rate,
                tax_amount=values["tax_amount"],
                line_total=values["line_total"],
            )
            self.db.add(db_item)

        self.db.flush()

        # Update inventory and create payment if purchase is issued
        if db_purchase.status in ["ISSUED", "PAID", "PARTIAL"]:
            self._update_inventory(db_purchase, company_id)
            self._create_accounting_entry(db_purchase, company_id)

            # Create automatic payment if payment method is not credit AND no payment exists yet
            if db_purchase.status in [
                "ISSUED",
                "PAID",
            ] and db_purchase.payment_method not in ["CREDIT", "PARTIAL_CREDIT"]:
                # Check if payment already exists to prevent duplicates
                existing_payment = (
                    self.db.query(PurchasePayment)
                    .filter(PurchasePayment.purchase_id == db_purchase.id)
                    .first()
                )
                if not existing_payment:
                    db_payment = PurchasePayment(
                        purchase_id=db_purchase.id,
                        payment_method=db_purchase.payment_method,
                        amount=db_purchase.total_amount,
                        payment_date=db_purchase.purchase_date,
                        reference=f"Auto-{db_purchase.purchase_number}",
                        created_by=user_id,
                    )
                    self.db.add(db_payment)
                    self.db.flush()

                    # Auto update status to PAID since payment covers total amount
                    db_purchase.status = "PAID"

                    # Create treasury transaction to decrease bank/cash balance
                    self._create_treasury_transaction(db_purchase, db_payment, company_id)

        try:
            self.db.commit()
            self.db.refresh(db_purchase)
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al guardar la compra: {str(e)}")

        return db_purchase

    def _update_inventory(self, purchase: Purchase, company_id: int):
        """Update inventory from purchase items"""
        import logging

        try:
            inventory_service = InventoryService(self.db)

            for item in purchase.items:
                if item.product_id:
                    inventory_service.add_stock(
                        product_id=item.product_id,
                        quantity=item.quantity,
                        company_id=company_id,
                        reference=f"Purchase {purchase.purchase_number}",
                        reference_id=purchase.id,
                        reference_type="PURCHASE",
                        unit_price=item.unit_price,
                    )
        except Exception as e:
            logging.warning(
                f"Error updating inventory for purchase {purchase.purchase_number}: {e}"
            )

    def _create_accounting_entry(self, purchase: Purchase, company_id: int):
        """Create automatic accounting entry for purchase"""
        import logging

        try:
            accounting_service = AccountingService(self.db)

            accounting_service.create_journal_entry_from_purchase(
                purchase_id=purchase.id,
                company_id=company_id,
                total_amount=purchase.total_amount,
                subtotal=purchase.subtotal,
                tax_amount=purchase.tax_amount,
                partner_id=purchase.partner_id,
                payment_method=purchase.payment_method,
            )
        except Exception as e:
            logging.warning(
                f"Error creating accounting entry for purchase {purchase.purchase_number}: {e}"
            )

    def get_purchases(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
        partner_id: int = None,
    ) -> List[Purchase]:
        """Get purchases with optional filters"""
        query = (
            self.db.query(Purchase)
            .options(joinedload(Purchase.partner))
            .filter(Purchase.company_id == company_id)
        )

        if status:
            query = query.filter(Purchase.status == status)
        if partner_id:
            query = query.filter(Purchase.partner_id == partner_id)

        return (
            query.order_by(Purchase.purchase_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_accounts_payable(
        self,
        company_id: int,
        days_ahead: int = 7,
    ) -> Dict:
        """
        Get accounts payable summary including overdue and upcoming due invoices.
        
        Args:
            company_id: Company ID
            days_ahead: Number of days to consider as 'upcoming' (default 7)
            
        Returns:
            Dictionary with:
            - overdue_invoices: List of invoices past due date
            - upcoming_invoices: List of invoices due within days_ahead
            - pending_invoices: All unpaid invoices
            - summary: Total amounts
        """
        now = datetime.now(timezone.utc)
        upcoming_cutoff = now + timedelta(days=days_ahead)
        
        # Get all non-paid purchases for the company
        pending_purchases = (
            self.db.query(Purchase)
            .options(joinedload(Purchase.partner), joinedload(Purchase.payments))
            .filter(
                Purchase.company_id == company_id,
                Purchase.status.in_(["ISSUED", "PARTIAL", "OVERDUE"]),
            )
            .order_by(Purchase.due_date.asc().nullslast())
            .all()
        )
        
        overdue_invoices = []
        upcoming_invoices = []
        pending_invoices = []
        
        total_pending = Decimal("0.00")
        total_overdue = Decimal("0.00")
        total_upcoming = Decimal("0.00")
        
        for purchase in pending_purchases:
            balance_due = self.calculate_balance_due(purchase.id)
            if balance_due <= 0:
                continue
                
            # Calculate days until due
            days_until_due = None
            if purchase.due_date:
                days_until_due = (purchase.due_date - now).days
            
            # Determine status
            is_overdue = purchase.due_date and purchase.due_date < now
            is_upcoming = purchase.due_date and now <= purchase.due_date <= upcoming_cutoff
            
            invoice_data = {
                "id": purchase.id,
                "purchase_number": purchase.purchase_number,
                "partner_id": purchase.partner_id,
                "partner_name": purchase.partner.name if purchase.partner else "Sin proveedor",
                "purchase_date": purchase.purchase_date,
                "due_date": purchase.due_date,
                "total_amount": purchase.total_amount,
                "balance_due": balance_due,
                "payment_method": purchase.payment_method,
                "status": purchase.status,
                "days_until_due": days_until_due,
                "is_overdue": is_overdue,
                "is_upcoming": is_upcoming,
            }
            
            if is_overdue:
                overdue_invoices.append(invoice_data)
                total_overdue += balance_due
            elif is_upcoming:
                upcoming_invoices.append(invoice_data)
                total_upcoming += balance_due
            else:
                pending_invoices.append(invoice_data)
            
            total_pending += balance_due
        
        return {
            "overdue_invoices": overdue_invoices,
            "upcoming_invoices": upcoming_invoices,
            "pending_invoices": pending_invoices,
            "summary": {
                "total_pending": total_pending,
                "total_overdue": total_overdue,
                "total_upcoming": total_upcoming,
                "overdue_count": len(overdue_invoices),
                "upcoming_count": len(upcoming_invoices),
                "pending_count": len(pending_invoices),
            },
        }

    def get_purchase_by_id(
        self, purchase_id: int, company_id: int
    ) -> Optional[Purchase]:
        """Get a single purchase by ID"""
        return (
            self.db.query(Purchase)
            .options(joinedload(Purchase.partner))
            .filter(Purchase.id == purchase_id, Purchase.company_id == company_id)
            .first()
        )

    def update_purchase(
        self,
        purchase_id: int,
        purchase_data: purchase_schema.PurchaseUpdate,
        company_id: int,
    ) -> Optional[Purchase]:
        """Update a purchase"""
        db_purchase = self.get_purchase_by_id(purchase_id, company_id)
        if not db_purchase:
            return None

        # Only allow updates for DRAFT or ISSUED status
        if db_purchase.status not in ["DRAFT", "ISSUED"]:
            raise ValueError("Cannot update purchase in current status")

        # Check if purchase number already exists (excluding current purchase)
        new_purchase_number = purchase_data.purchase_number
        if new_purchase_number and new_purchase_number != db_purchase.purchase_number:
            existing = self.db.query(Purchase).filter(
                Purchase.purchase_number == new_purchase_number,
                Purchase.company_id == company_id,
                Purchase.id != purchase_id
            ).first()
            if existing:
                raise ValueError(f"Ya existe otra compra con el número {new_purchase_number}. Use un número diferente.")

        # Store original status to detect changes
        original_status = db_purchase.status
        original_payment_method = db_purchase.payment_method

        update_data = purchase_data.model_dump(exclude_unset=True)

        # Handle enum conversion
        if "payment_method" in update_data:
            update_data["payment_method"] = update_data["payment_method"].value
        if "status" in update_data:
            update_data["status"] = update_data["status"].value

        for key, value in update_data.items():
            setattr(db_purchase, key, value)

        self.db.commit()
        self.db.refresh(db_purchase)

        # Only update inventory/accounting when status CHANGES to ISSUED (not on every save)
        status_changed_to_issued = original_status != "ISSUED" and db_purchase.status == "ISSUED"

        if status_changed_to_issued:
            self._update_inventory(db_purchase, company_id)
            self._create_accounting_entry(db_purchase, company_id)

            # Create automatic payment if not credit AND no payment exists yet
            if db_purchase.payment_method not in ["CREDIT", "PARTIAL_CREDIT"]:
                existing_payment = (
                    self.db.query(PurchasePayment)
                    .filter(PurchasePayment.purchase_id == db_purchase.id)
                    .first()
                )
                if not existing_payment:
                    user_id = None  # Will be None for updates, no user tracking
                    db_payment = PurchasePayment(
                        purchase_id=db_purchase.id,
                        payment_method=db_purchase.payment_method,
                        amount=db_purchase.total_amount,
                        payment_date=db_purchase.purchase_date,
                        reference=f"Auto-{db_purchase.purchase_number}",
                        created_by=user_id,
                    )
                    self.db.add(db_payment)
                    db_purchase.status = "PAID"
                    self.db.commit()
                    self._create_treasury_transaction(db_purchase, db_payment, company_id)
                else:
                    self.db.commit()

        return db_purchase
        if not db_purchase:
            return False

        if db_purchase.status != "DRAFT":
            raise ValueError("Only DRAFT purchases can be deleted")

        self.db.delete(db_purchase)
        self.db.commit()
        return True

    def cancel_purchase(self, purchase_id: int, company_id: int) -> Purchase:
        """
        Cancel a purchase and reverse its effects.
        - Reverse inventory stock
        - Create reversing accounting entry
        - Reverse treasury transactions if payments exist
        """
        db_purchase = self.get_purchase_by_id(purchase_id, company_id)
        if not db_purchase:
            raise ValueError("Purchase not found")

        if db_purchase.status == "CANCELLED":
            return db_purchase

        # 1. Reverse Inventory
        if db_purchase.status in ["ISSUED", "PAID", "PARTIAL"]:
            inventory_service = InventoryService(self.db)
            for item in db_purchase.items:
                if item.product_id:
                    inventory_service.deduct_stock(
                        product_id=item.product_id,
                        quantity=item.quantity,
                        company_id=company_id,
                    )

        # 2. Reverse Accounting
        if db_purchase.status in ["ISSUED", "PAID", "PARTIAL"]:
            accounting_service = AccountingService(self.db)
            # Find the original journal entry by reference
            reference = f"CP-{db_purchase.id:06d}"
            original_je = (
                self.db.query(JournalEntry)
                .filter(
                    JournalEntry.reference == reference,
                    JournalEntry.company_id == company_id
                )
                .first()
            )
            if original_je:
                accounting_service.reverse_journal_entry(
                    je_id=original_je.id,
                    company_id=company_id,
                    description=f"Anulación de compra #{db_purchase.purchase_number}"
                )

        # 3. Reverse Payments in Treasury
        from app.services.treasury_service import TreasuryService
        treasury_service = TreasuryService(self.db)
        for payment in db_purchase.payments:
            # We "deposit" back what was "withdrawn"
            # We need to find the correct account. 
            # In our system, payments usually affect bank or cash based on payment_method.
            account_type = "CASH" if payment.payment_method == "CASH" else "BANK"
            
            # Find an active account of that type for the company
            if account_type == "CASH":
                accounts = treasury_service.get_cash_accounts(company_id)
            else:
                accounts = treasury_service.get_bank_accounts(company_id)
            
            if accounts:
                treasury_service.deposit(
                    account_type=account_type,
                    account_id=accounts[0].id,
                    amount=payment.amount,
                    description=f"Reversión de pago por anulación - Factura {db_purchase.purchase_number}",
                    reference=f"REV-PAY-{payment.id}",
                    company_id=company_id
                )

        # 4. Set status to CANCELLED
        db_purchase.status = "CANCELLED"
        self.db.commit()
        self.db.refresh(db_purchase)
        
        return db_purchase

    def register_payment(
        self,
        purchase_id: int,
        payment_data: purchase_schema.PurchasePaymentCreate,
        company_id: int,
        user_id: int = None,
    ) -> PurchasePayment:
        """Register a payment for a purchase"""
        db_purchase = self.get_purchase_by_id(purchase_id, company_id)
        if not db_purchase:
            raise ValueError("Purchase not found")

        if db_purchase.status == "CANCELLED":
            raise ValueError("Cannot make payment to cancelled purchase")

        # Calculate paid amount
        total_paid = sum(p.amount for p in db_purchase.payments)
        remaining = db_purchase.total_amount - total_paid

        # Use a small epsilon to prevent floating-point/decimal conversion false positives
        if payment_data.amount > remaining + Decimal("0.02"):
            raise ValueError(f"Payment amount exceeds remaining balance of {remaining}")

        # Create payment record
        db_payment = PurchasePayment(
            purchase_id=purchase_id,
            payment_method=payment_data.payment_method.value,
            amount=payment_data.amount,
            payment_date=payment_data.payment_date or datetime.now(timezone.utc),
            reference=payment_data.reference,
            notes=payment_data.notes,
            created_by=user_id,
        )

        self.db.add(db_payment)

        # Update purchase status
        total_paid_after = total_paid + payment_data.amount
        if total_paid_after >= db_purchase.total_amount:
            db_purchase.status = "PAID"
        else:
            db_purchase.status = "PARTIAL"

        self.db.commit()
        self.db.refresh(db_payment)

        # Create treasury transaction if payment is not credit
        if payment_data.payment_method not in ["CREDIT", "PARTIAL_CREDIT"]:
            self._create_treasury_transaction(db_purchase, db_payment, company_id)

        return db_payment

    def _create_treasury_transaction(
        self, purchase: Purchase, payment: PurchasePayment, company_id: int
    ):
        """Create treasury transaction for the payment"""
        from app.services.treasury_service import TreasuryService

        treasury_service = TreasuryService(self.db)

        # Determine account type based on payment method
        if payment.payment_method in ["CASH"]:
            account_type = "CASH"
            # Get first cash account
            cash_accounts = treasury_service.get_cash_accounts(company_id)
            if not cash_accounts:
                return  # No cash account configured
            account_id = cash_accounts[0].id
        else:
            account_type = "BANK"
            # Get first bank account
            bank_accounts = treasury_service.get_bank_accounts(company_id)
            if not bank_accounts:
                return  # No bank account configured
            account_id = bank_accounts[0].id

        try:
            treasury_service.withdraw(
                account_type=account_type,
                account_id=account_id,
                amount=payment.amount,
                description=f"Pago a proveedor - Factura {purchase.purchase_number}",
                reference=payment.reference,
                company_id=company_id,
                skip_journal_entry=True,
            )
        except Exception as e:
            # Log error but don't fail the payment
            import logging

            logging.warning(f"Error creating treasury transaction: {e}")

    def get_statistics(
        self, company_id: int, start_date: date = None, end_date: date = None
    ) -> purchase_schema.PurchaseStatistics:
        """Get purchase statistics"""
        query = (
            self.db.query(Purchase)
            .options(joinedload(Purchase.payments), joinedload(Purchase.partner))
            .filter(Purchase.company_id == company_id)
        )

        if start_date:
            query = query.filter(Purchase.purchase_date >= start_date)
        if end_date:
            query = query.filter(Purchase.purchase_date <= end_date)

        purchases = query.all()

        total_purchases = len(purchases)
        total_amount = sum(p.total_amount for p in purchases)

        paid_amount = Decimal("0.00")
        pending_amount = Decimal("0.00")
        overdue_count = 0

        by_payment_method = {}
        by_month = {}

        from datetime import timezone
        now = datetime.now(timezone.utc)

        for p in purchases:
            paid = sum(pm.amount for pm in p.payments)

            if p.status == "PAID":
                paid_amount += p.total_amount
            else:
                pending_amount += p.total_amount - paid

            if p.status == "OVERDUE" or (
                p.due_date and p.due_date < now and p.status != "PAID"
            ):
                overdue_count += 1

            # By payment method
            pm = p.payment_method
            if pm not in by_payment_method:
                by_payment_method[pm] = {"count": 0, "total": Decimal("0.00")}
            by_payment_method[pm]["count"] += 1
            by_payment_method[pm]["total"] += p.total_amount

            # By month
            month_key = p.purchase_date.strftime("%Y-%m") if p.purchase_date else "N/A"
            if month_key not in by_month:
                by_month[month_key] = {
                    "month": month_key,
                    "count": 0,
                    "total": Decimal("0.00"),
                }
            by_month[month_key]["count"] += 1
            by_month[month_key]["total"] += p.total_amount

        # Convertir by_month a lista
        by_month_list = [
            {"month": k, "count": v["count"], "total": v["total"]}
            for k, v in by_month.items()
        ]

        return purchase_schema.PurchaseStatistics(
            total_purchases=total_purchases,
            total_amount=total_amount,
            paid_amount=paid_amount,
            pending_amount=pending_amount,
            overdue_count=overdue_count,
            by_payment_method=by_payment_method,
            by_month=by_month_list,
        )

    def calculate_balance_due(self, purchase_id: int, company_id: int = None) -> Decimal:
        """Calculate remaining balance for a purchase"""
        query = self.db.query(Purchase).filter(Purchase.id == purchase_id)
        if company_id is not None:
            query = query.filter(Purchase.company_id == company_id)
        purchase = query.first()
        if not purchase:
            return Decimal("0.00")

        paid = sum(p.amount for p in purchase.payments)
        return purchase.total_amount - paid

    def extract_from_pdf(self, file_content: bytes, company_id: int) -> dict:
        """Extract partner and items from a purchase invoice PDF using Gemini"""
        # 1. Extract text using PyMuPDF (solo para PDFs nativos, no escaneados)
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()

        is_scanned = not text.strip()

        # 2. Call Gemini API
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "tu_clave_de_gemini_aqui":
            raise ValueError("GEMINI_API_KEY no es válida. Obtén una clave real en Google AI Studio.")

        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        if is_scanned:
            text_context = "Este es un PDF escaneado (imagen), no tiene texto embebido. Lee el contenido directamente de la imagen del documento."
        else:
            text_context = f"Texto extraído como respaldo:\n{text}"

        prompt = f"""
A continuación tienes una factura de compra (archivo PDF). {text_context}
Tu tarea es extraer la información del proveedor y los productos comprados.
IMPORTANTE: Para la descripción del producto, extrae EXACTAMENTE el texto original que ves en la factura, no resumas ni recortes la descripción. Si incluye referencias como DDR4 4GB 3200MHZ, inclúyelas tal cual.

Responde ÚNICAMENTE con un objeto JSON con la siguiente estructura (sin formato Markdown, sin texto adicional):
{{
  "purchase_number": "Número de la factura (solo el número o código, ej: ATPE 24468)",
  "partner_data": {{
    "nit": "Número de NIT o documento (solo números o guiones)",
    "name": "Nombre completo del proveedor",
    "email": "Email del proveedor si existe, o null",
    "phone": "Teléfono si existe, o null",
    "address": "Dirección si existe, o null"
  }},
  "items": [
    {{
      "description": "Copia EXACTA del nombre y características del producto (sin resumir)",
      "quantity": cantidad en número,
      "unit_price": precio unitario en número sin símbolos,
      "tax_rate": porcentaje de IVA (ej. 19) o 0,
      "serial_number": "El número de serie del producto (suele empezar por SN:, SN::, o S/N). Debes extraerlo sí o sí si aparece bajo la descripción. Ej: BWA43100001578. Si no hay, null"
    }}
  ]
}}
"""
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(data=file_content, mime_type='application/pdf'),
                    prompt
                ],
            )
            response_text = response.text.strip()
        except Exception as e:
            raise ValueError(f"Error de comunicación con Gemini: {str(e)}")
        
        # Clean up markdown if Gemini returned it despite the instruction
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        try:
            extracted_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parseando la respuesta de Gemini: {e}")
            
        partner_data = extracted_data.get("partner_data", {})
        nit = partner_data.get("nit", "")
        
        partner_exists = False
        partner_id = None
        
        # Clean NIT for search (remove dashes and letters)
        clean_nit = ''.join(filter(str.isdigit, str(nit))) if nit else ""
        
        if clean_nit:
            # Look for partner
            db_partner = self.db.query(Partner).filter(
                Partner.company_id == company_id,
                Partner.nit.like(f"%{clean_nit}%")
            ).first()
            
            if db_partner:
                partner_exists = True
                partner_id = db_partner.id
                # Overwrite extracted data with real DB data to be safe
                partner_data = {
                    "id": db_partner.id,
                    "nit": db_partner.nit,
                    "name": db_partner.name
                }
                
        return {
            "partner_exists": partner_exists,
            "partner_data": partner_data,
            "items": extracted_data.get("items", []),
            "purchase_number": extracted_data.get("purchase_number", "")
        }
