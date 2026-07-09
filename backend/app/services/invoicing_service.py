from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.sql.invoicing import Invoice, InvoiceItem, InvoiceResolution
from app.models.sql import company as company_model
from app.schemas import invoicing as inv_schema
from decimal import Decimal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.services.inventory_service import InventoryService
from app.services.accounting_service import AccountingService
from app.services.treasury_service import TreasuryService
from app.models.sql.repair import RepairOrder


class InvoicingService:
    def __init__(self, db: Session):
        self.db = db

    def generate_invoice_number(self, company_id: int, invoice_type: str = "SALE") -> str:
        """Generate the next invoice number atomically.

        This method acquires a row‑level lock on the active ``InvoiceResolution`` for the
        given company and ``invoice_type``. If none exists it creates one using an
        ``INSERT`` that may raise ``IntegrityError`` under concurrent load – we catch
        that error, rollback, and fetch the existing resolution instead. This
        eliminates the TOCTOU race where two transactions could create duplicate
        ``InvoiceResolution`` rows.
        """
        # Try to fetch the active resolution with a lock
        resolution = (
            self.db.query(InvoiceResolution)
            .filter(
                InvoiceResolution.company_id == company_id,
                InvoiceResolution.resolution_type == invoice_type,
                InvoiceResolution.is_active == True,
            )
            .with_for_update()
            .first()
        )

        if not resolution:
            # No active resolution – attempt to create the default one
            resolution = InvoiceResolution(
                company_id=company_id,
                resolution_type=invoice_type,
                prefix="INV-",
                start_number=1,
                current_number=1,
                is_active=True,
            )
            self.db.add(resolution)
            try:
                self.db.flush()
            except Exception as e:
                # Likely an IntegrityError from a concurrent INSERT – fetch the existing row
                self.db.rollback()
                resolution = (
                    self.db.query(InvoiceResolution)
                    .filter(
                        InvoiceResolution.company_id == company_id,
                        InvoiceResolution.resolution_type == invoice_type,
                        InvoiceResolution.is_active == True,
                    )
                    .with_for_update()
                    .first()
                )
                if not resolution:
                    # Re‑raise if we still cannot obtain a resolution
                    raise e

        # Ensure we have not exceeded the defined range
        if resolution.end_number is not None and resolution.current_number > resolution.end_number:
            raise ValueError(
                f"Se ha agotado el rango de numeración de facturas ({resolution.current_number} > {resolution.end_number}) "
                f"para la resolución {resolution.prefix}. Configure una nueva resolución de facturación."
            )

        # Allocate the next number
        next_number = resolution.current_number
        formatted_number = f"{resolution.prefix}{next_number:08d}"
        # Increment the counter for the next call
        resolution.current_number += 1
        self.db.flush()
        return formatted_number

    def _calculate_invoice_values(
        self, subtotal: Decimal, company_regimen: str, tax_rate: Decimal = None
    ) -> dict:
        """
        Calculate invoice values based on company's tax regime
        For SIMPLE regime: no tax discrimination
        For COMUN/ESPECIAL regimes: apply tax rate
        """
        if company_regimen in ("SIMPLE", "NO_RESPONSABLE"):
            # Régimen Simple o No Responsable: no se discrimina IVA
            iva = Decimal("0.00")
            valor_total = subtotal
            ley_factura = "Tratamiento especial - Régimen Simple de Tributación" if company_regimen == "SIMPLE" else "No Responsable de IVA"
        else:
            # Régimen Común o Especial: aplicar IVA según tipo
            if tax_rate is None:
                tax_rate = Decimal("0.19")  # Default to 19% IVA
            iva = subtotal * tax_rate
            valor_total = subtotal + iva
            ley_factura = None

        return {
            "subtotal": subtotal,
            "iva": iva,
            "valor_total": valor_total,
            "ley_factura": ley_factura,
        }

    def _create_automatic_journal_entry(
        self, db_invoice: Invoice, company_id: int, is_paid: bool = False, payment_method: Optional[str] = None, wallet_amount_applied: Decimal = Decimal("0.00"),
        commit: bool = True,
    ):
        """
        Create automatic journal entry when invoice is created.
        """
        from app.services.accounting_service import AccountingService
        from app.models.sql.inventory import Product

        accounting_service = AccountingService(self.db)

        # Calculate subtotal and tax from items
        subtotal = Decimal("0.00")
        tax_amount = Decimal("0.00")
        total_cost = Decimal("0.00")

        if hasattr(db_invoice, "items") and db_invoice.items:
            for item in db_invoice.items:
                # Net amount without tax
                net_amount = item.line_total - item.tax_amount
                subtotal += net_amount
                tax_amount += item.tax_amount
                if item.product_id:
                    product = self.db.query(Product).filter(Product.id == item.product_id).first()
                    if product and product.purchase_price:
                        total_cost += Decimal(str(product.purchase_price)) * Decimal(str(item.quantity))
        else:
            # When items are not expanded, assume total_amount already includes tax and subtotal = total_amount (tax will be zeroed later if regime is simple)
            subtotal = db_invoice.total_amount
            tax_amount = Decimal("0.00")

        total_amount = subtotal + tax_amount

        # For SIMPLE regime, no tax discrimination
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if company and company.regimen in ("SIMPLE", "NO_RESPONSABLE"):
            tax_amount = Decimal("0.00")
            total_amount = subtotal

        accounting_service.create_journal_entry_from_invoice(
            invoice_id=db_invoice.id,
            company_id=company_id,
            total_amount=total_amount,
            subtotal=subtotal,
            tax_amount=tax_amount,
            partner_id=db_invoice.partner_id,
            is_warranty=False,
            source_type="INVOICE",
            total_cost=total_cost,
            is_paid=is_paid,
            payment_method=payment_method,
            wallet_amount_applied=wallet_amount_applied,
            commit=commit,
        )

    def create_invoice(
        self, invoice: inv_schema.InvoiceCreate, company_id: int
    ) -> Invoice:
        """Legacy invoice creation – disabled.

        The original implementation created an invoice without deducting
        inventory, leading to data inconsistency. It is now deliberately
        disabled. Use ``create_invoice_with_items`` which performs the full
        workflow (stock deduction, accounting, treasury handling).
        """
        raise ValueError(
            "`create_invoice` is deprecated because it does not handle inventory. "
            "Use `create_invoice_with_items` instead."
        )

    def create_invoice_with_items(
        self, invoice_with_items: inv_schema.InvoiceWithItemsCreate, company_id: int
    ) -> Invoice:
        # Determine invoice number
        inv_num = invoice_with_items.invoice_number
        if not inv_num or inv_num.startswith("INV-17"):
            inv_num = self.generate_invoice_number(company_id, invoice_type=invoice_with_items.invoice_type)

        # Create the invoice
        db_invoice = Invoice(
            invoice_number=inv_num,
            invoice_type=invoice_with_items.invoice_type,
            partner_id=invoice_with_items.partner_id,

            issue_date=invoice_with_items.issue_date,
            due_date=invoice_with_items.due_date,
            total_amount=invoice_with_items.total_amount,
            currency=invoice_with_items.currency,
            status=invoice_with_items.status,
            cufe=invoice_with_items.cufe,
            xml_ubl=invoice_with_items.xml_ubl,
            estado_dian=invoice_with_items.estado_dian
            or ("NO_APLICA" if invoice_with_items.invoice_type == "CUENTA_COBRO" else "BORRADOR"),
            motivo_rechazo=invoice_with_items.motivo_rechazo,
            company_id=company_id,
        )
        
        if invoice_with_items.is_paid:
            db_invoice.status = "PAID"

        self.db.add(db_invoice)
        self.db.flush()

        # Create the invoice items
        for item in invoice_with_items.items:
            db_item = InvoiceItem(
                invoice_id=db_invoice.id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount,
                tax_rate=item.tax_rate,
                tax_amount=item.tax_amount,
                line_total=item.line_total,
                product_id=item.product_id,
                serial_number=item.serial_number,
            )
            self.db.add(db_item)

        # Link to Repair Order if provided
        if invoice_with_items.repair_id:
            repair_order = self.db.query(RepairOrder).filter(RepairOrder.id == invoice_with_items.repair_id).first()
            if repair_order:
                repair_order.invoice_id = db_invoice.id
                repair_order.status = "DELIVERED"

        try:
            # Deduct inventory for invoice items that have products linked
            from app.services.inventory_service import InventoryService

            inventory_service = InventoryService(self.db)

            for item in db_invoice.items:
                if item.product_id:
                    inventory_service.deduct_stock(
                        product_id=item.product_id,
                        quantity=item.quantity,
                        company_id=company_id,
                        commit=False,
                    )

            # Create automatic journal entry (no commit — caller handles it)
            self._create_automatic_journal_entry(
                db_invoice, 
                company_id, 
                is_paid=invoice_with_items.is_paid, 
                payment_method=invoice_with_items.payment_method,
                wallet_amount_applied=invoice_with_items.wallet_amount_applied,
                commit=False,
            )

            self.db.flush()

            # Trigger Treasury Deposit or Wallet Withdrawal if paid
            if invoice_with_items.is_paid:
                remaining_to_pay = invoice_with_items.total_amount
                
                # 1. Apply Wallet Balance first if specified
                if invoice_with_items.wallet_amount_applied > 0:
                    from app.services.wallet_service import WalletService
                    wallet_service = WalletService(self.db)
                    wallet = wallet_service.get_wallet_by_partner(db_invoice.partner_id, company_id)
                    if not wallet:
                        raise ValueError("El socio no tiene un monedero activo para aplicar el saldo.")
                    
                    if wallet.balance < invoice_with_items.wallet_amount_applied:
                        raise ValueError("Saldo insuficiente en el monedero para aplicar el monto especificado.")
                    
                    wallet_service.withdraw(
                        wallet_id=wallet.id,
                        amount=invoice_with_items.wallet_amount_applied,
                        description=f"Aplicación parcial a Factura {db_invoice.invoice_number}",
                        company_id=company_id,
                        commit=False,
                    )
                    remaining_to_pay -= invoice_with_items.wallet_amount_applied

                # 2. Handle the rest with the selected payment method
                if remaining_to_pay > 0:
                    if invoice_with_items.payment_method == "WALLET":
                        from app.services.wallet_service import WalletService
                        wallet_service = WalletService(self.db)
                        wallet = wallet_service.get_wallet_by_partner(db_invoice.partner_id, company_id)
                        
                        wallet_service.withdraw(
                            wallet_id=wallet.id,
                            amount=remaining_to_pay,
                            description=f"Pago de Factura {db_invoice.invoice_number}",
                            company_id=company_id,
                            commit=False,
                        )
                    else:
                        from app.services.treasury_service import TreasuryService
                        treasury_service = TreasuryService(self.db)
                        
                        acct_type = invoice_with_items.payment_account_type
                        acct_id = invoice_with_items.payment_account_id
                        
                        if not acct_type or not acct_id:
                            if invoice_with_items.payment_method == "CASH":
                                cash_accounts = treasury_service.get_cash_accounts(company_id)
                                if cash_accounts:
                                    acct_type = "CASH"
                                    acct_id = cash_accounts[0].id
                            elif invoice_with_items.payment_method in ("BANK_TRANSFER", "CARD", "TRANSFER"):
                                try:
                                    bank_accounts = treasury_service.get_bank_accounts(company_id)
                                    if bank_accounts:
                                        acct_type = "BANK"
                                        acct_id = bank_accounts[0].id
                                except AttributeError:
                                    pass

                        if acct_type and acct_id:
                            treasury_service.deposit(
                                account_type=acct_type,
                                account_id=acct_id,
                                amount=remaining_to_pay,
                                description=f"Pago - Factura {db_invoice.invoice_number}",
                                reference=f"INV-{db_invoice.id:06d}",
                                company_id=company_id,
                                skip_journal_entry=True,
                                commit=False,
                            )

            # Single commit for the entire transaction
            self.db.commit()
            self.db.refresh(db_invoice)
        except Exception:
            self.db.rollback()
            raise

        return db_invoice

    # ---------------------------------------------------------------------------
    # Helper: enrich an Invoice ORM object with denormalized partner data
    # ---------------------------------------------------------------------------
    def _enrich_invoice(self, invoice: Invoice) -> dict:
        """Return a dict representation of the invoice with partner fields included."""
        data = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "invoice_type": invoice.invoice_type,
            "partner_id": invoice.partner_id,
            "issue_date": invoice.issue_date,
            "due_date": invoice.due_date,
            "total_amount": invoice.total_amount,
            "currency": invoice.currency,
            "status": invoice.status,
            "cufe": invoice.cufe,
            "xml_ubl": invoice.xml_ubl,
            "estado_dian": invoice.estado_dian,
            "motivo_rechazo": invoice.motivo_rechazo,
            "company_id": invoice.company_id,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at,
            # Partner info
            "partner_name": invoice.partner.name if invoice.partner else None,
            "partner_nit": invoice.partner.nit if invoice.partner else None,
            "partner_address": invoice.partner.address if invoice.partner else None,
            "partner_phone": invoice.partner.phone if invoice.partner else None,
        }
        # Calculate subtotal and vat_amount from items; also include items list
        subtotal = Decimal("0.00")
        vat_amount = Decimal("0.00")
        items_list = []
        if hasattr(invoice, "items") and invoice.items:
            for item in invoice.items:
                line_sub = (item.quantity * item.unit_price) - item.discount
                subtotal += line_sub
                vat_amount += item.tax_amount
                items_list.append({
                    "id": item.id,
                    "invoice_id": item.invoice_id,
                    "description": item.description,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount": item.discount,
                    "tax_rate": item.tax_rate,
                    "tax_amount": item.tax_amount,
                    "line_total": item.line_total,
                    "product_id": item.product_id,
                    "serial_number": item.serial_number,
                })
        data["subtotal"] = subtotal if subtotal else invoice.total_amount
        data["vat_amount"] = vat_amount
        data["items"] = items_list
        return data

    def get_invoices(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Invoice]:
        invoices = (
            self.db.query(Invoice)
            .filter(Invoice.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._enrich_invoice(inv) for inv in invoices]

    def get_invoice_by_id(self, invoice_id: int, company_id: int) -> Optional[Invoice]:
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.id == invoice_id,
                Invoice.company_id == company_id,
            )
            .first()
        )

    def get_invoice_with_items(
        self, invoice_id: int, company_id: int
    ) -> Optional[dict]:
        invoice = self.get_invoice_by_id(invoice_id, company_id)
        if invoice:
            # Eager load the items
            self.db.refresh(invoice, attribute_names=["items"])
            return self._enrich_invoice(invoice)
        return None

    def update_invoice(
        self, invoice_id: int, invoice: inv_schema.InvoiceCreate, company_id: int
    ) -> Optional[Invoice]:
        db_invoice = self.get_invoice_by_id(invoice_id, company_id)
        if db_invoice:
            invoice_dict = invoice.model_dump()
            # Handle field name changes for DIAN compliance
            if "dian_response" in invoice_dict and "estado_dian" not in invoice_dict:
                invoice_dict["estado_dian"] = invoice_dict.pop("dian_response")
            if "xml_ubl" in invoice_dict:
                invoice_dict["xml_ubl"] = invoice_dict["xml_ubl"]
            if "cufe" in invoice_dict:
                invoice_dict["cufe"] = invoice_dict["cufe"]
            # Set defaults for new fields if not provided
            if "estado_dian" not in invoice_dict:
                invoice_dict["estado_dian"] = "BORRADOR"
            if "motivo_rechazo" not in invoice_dict:
                invoice_dict["motivo_rechazo"] = None

            for key, value in invoice_dict.items():
                setattr(db_invoice, key, value)
            self.db.commit()
            self.db.refresh(db_invoice)
        return db_invoice

    def delete_invoice(self, invoice_id: int, company_id: int) -> bool:
        raise ValueError(
            "La eliminación directa de facturas no está permitida. "
            "Use cancel_invoice() para anular la factura en su lugar."
        )

    def cancel_invoice(self, invoice_id: int, company_id: int) -> Invoice:
        """
        Cancel an invoice and reverse its effects.
        - Reverse inventory stock (add back)
        - Create reversing accounting entry
        - Reverse treasury deposit if it was paid
        - Reverse wallet withdrawals
        """
        db_invoice = self.get_invoice_by_id(invoice_id, company_id)
        if not db_invoice:
            raise ValueError("Invoice not found")

        if db_invoice.status == "CANCELLED":
            return db_invoice

        self.db.refresh(db_invoice, attribute_names=["items"])

        try:
            # 1. Reverse Inventory (Add stock back)
            inventory_service = InventoryService(self.db)
            
            for item in db_invoice.items:
                if item.product_id:
                    inventory_service.add_stock(
                        product_id=item.product_id,
                        quantity=item.quantity,
                        company_id=company_id,
                        reference=f"Cancelación de Factura {db_invoice.invoice_number}",
                        reference_id=db_invoice.id,
                        reference_type="INVOICE_CANCEL",
                        commit=False,
                    )

            # 2. Reverse Accounting
            accounting_service = AccountingService(self.db)
            reference = f"INV-{db_invoice.id:06d}"
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
                    description=f"Anulación de Factura #{db_invoice.invoice_number}",
                    commit=False,
                )

            # 3. Reverse Wallet Withdrawals
            partner_id = db_invoice.partner_id
            if partner_id:
                from app.services.wallet_service import WalletService
                from app.models.sql.wallet import WalletTransaction as WalletTxModel
                wallet_service = WalletService(self.db)
                wallet = wallet_service.get_wallet_by_partner(partner_id, company_id)
                if wallet:
                    wallet_txs = (
                        self.db.query(WalletTxModel)
                        .filter(
                            WalletTxModel.wallet_id == wallet.id,
                            WalletTxModel.transaction_type == "WITHDRAWAL",
                            WalletTxModel.description.like(f"%{db_invoice.invoice_number}%"),
                        )
                        .all()
                    )
                    for wtx in wallet_txs:
                        wallet_service.deposit(
                            wallet_id=wallet.id,
                            amount=wtx.amount,
                            description=f"Reversión por anulación de factura {db_invoice.invoice_number}",
                            company_id=company_id,
                            commit=False,
                        )

            # 4. Reverse Treasury Deposit if PAID
            if db_invoice.status == "PAID":
                treasury_service = TreasuryService(self.db)
                from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
                tx = (
                    self.db.query(TreasuryTransaction)
                    .filter(
                        TreasuryTransaction.reference == f"INV-{db_invoice.id:06d}",
                        TreasuryTransaction.company_id == company_id,
                        TreasuryTransaction.transaction_type == "DEPOSIT"
                    )
                    .first()
                )
                if tx:
                    account_id = tx.bank_account_id or tx.cash_account_id
                    account_type = tx.account_type
                    if account_id:
                        treasury_service.withdraw(
                            account_type=account_type,
                            account_id=account_id,
                            amount=tx.amount,
                            description=f"Reversión por anulación de factura {db_invoice.invoice_number}",
                            reference=f"REV-INV-{db_invoice.id}",
                            company_id=company_id,
                            skip_journal_entry=True,
                            commit=False,
                        )

            # 5. Set status to CANCELLED
            db_invoice.status = "CANCELLED"
            self.db.commit()
            self.db.refresh(db_invoice)
        except Exception:
            self.db.rollback()
            raise
        
        return db_invoice
