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


class InvoicingService:
    def __init__(self, db: Session):
        self.db = db

    def generate_invoice_number(self, company_id: int, invoice_type: str = "SALE") -> str:
        """
        Generates the next invoice number using the InvoiceResolution table with row-level locking.
        """
        # Find the active resolution for this company and type, locking it for update
        resolution = (
            self.db.query(InvoiceResolution)
            .filter(
                InvoiceResolution.company_id == company_id,
                InvoiceResolution.resolution_type == invoice_type,
                InvoiceResolution.is_active == True
            )
            .with_for_update()
            .first()
        )

        if not resolution:
            # Create a default resolution "INV-"
            resolution = InvoiceResolution(
                company_id=company_id,
                resolution_type=invoice_type,
                prefix="INV-",
                start_number=1,
                current_number=1,
                is_active=True
            )
            self.db.add(resolution)
            self.db.flush()

        # Generate the next number
        next_number = resolution.current_number
        formatted_number = f"{resolution.prefix}{next_number:08d}"
        
        # Increment the sequence
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
        self, db_invoice: Invoice, company_id: int, is_paid: bool = False, payment_method: Optional[str] = None
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
                subtotal += item.line_total
                tax_amount += item.tax_amount
                if item.product_id:
                    product = self.db.query(Product).filter(Product.id == item.product_id).first()
                    if product and product.purchase_price:
                        total_cost += Decimal(str(product.purchase_price)) * Decimal(str(item.quantity))
        else:
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
        )

    def create_invoice(
        self, invoice: inv_schema.InvoiceCreate, company_id: int
    ) -> Invoice:
        # Get company to determine regime
        db_company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not db_company:
            raise ValueError("Company not found")

        # Prepare invoice data
        invoice_data = invoice.model_dump()

        # Generate sequenced invoice number if missing or includes Date.now timestamp indicator
        if not invoice_data.get("invoice_number") or invoice_data["invoice_number"].startswith("INV-17"):
            invoice_data["invoice_number"] = self.generate_invoice_number(
                company_id, invoice_type=invoice_data.get("invoice_type", "SALE")
            )

        # If tax calculation is needed based on items, we would do it here
        # For now, we assume the client sends pre-calculated values
        # But we ensure DIAN compliance fields are set
        if "estado_dian" not in invoice_data or not invoice_data["estado_dian"]:
            if db_company.regimen == "NO_RESPONSABLE" or invoice_data.get("invoice_type") == "CUENTA_COBRO":
                invoice_data["estado_dian"] = "NO_APLICA"
            else:
                invoice_data["estado_dian"] = "BORRADOR"
        if "motivo_rechazo" not in invoice_data:
            invoice_data["motivo_rechazo"] = None

        db_invoice = Invoice(**invoice_data, company_id=company_id)
        self.db.add(db_invoice)
        self.db.commit()
        self.db.refresh(db_invoice)

        # Create automatic journal entry
        self._create_automatic_journal_entry(db_invoice, company_id)
        self.db.commit()
        self.db.refresh(db_invoice)

        return db_invoice

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
            or ("NO_APLICA" if invoice_with_items.invoice_type == "CUENTA_COBRO" else "BORRADOR"),  # Default to BORRADOR or NO_APLICA
            motivo_rechazo=invoice_with_items.motivo_rechazo,
            company_id=company_id,
        )
        
        if invoice_with_items.is_paid:
            db_invoice.status = "PAID"

        self.db.add(db_invoice)
        self.db.flush()  # To get the ID without committing

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
            )
            self.db.add(db_item)

        self.db.commit()
        self.db.refresh(db_invoice)

        # Deduct inventory for invoice items that have products linked
        from app.services.inventory_service import InventoryService

        inventory_service = InventoryService(self.db)

        for item in db_invoice.items:
            if item.product_id:
                inventory_service.deduct_stock(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    company_id=company_id,
                )

        # Create automatic journal entry
        self._create_automatic_journal_entry(
            db_invoice, 
            company_id, 
            is_paid=invoice_with_items.is_paid, 
            payment_method=invoice_with_items.payment_method
        )
        self.db.commit()
        self.db.refresh(db_invoice)

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
                    company_id=company_id
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
                        company_id=company_id
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
                                pass # In case get_bank_accounts isn't available

                    if acct_type and acct_id:
                        treasury_service.deposit(
                            account_type=acct_type,
                            account_id=acct_id,
                            amount=remaining_to_pay,
                            description=f"Pago - Factura {db_invoice.invoice_number}",
                            reference=f"INV-{db_invoice.id}",
                            company_id=company_id,
                            skip_journal_entry=True
                        )

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
        db_invoice = self.get_invoice_by_id(invoice_id, company_id)
        if db_invoice:
            self.db.delete(db_invoice)
            self.db.commit()
            return True
        return False

    def cancel_invoice(self, invoice_id: int, company_id: int) -> Invoice:
        """
        Cancel an invoice and reverse its effects.
        - Reverse inventory stock (add back)
        - Create reversing accounting entry
        - Reverse treasury deposit if it was paid
        """
        db_invoice = self.get_invoice_by_id(invoice_id, company_id)
        if not db_invoice:
            raise ValueError("Invoice not found")

        if db_invoice.status == "CANCELLED":
            return db_invoice

        # 1. Reverse Inventory (Add stock back)
        inventory_service = InventoryService(self.db)
        # We need the items to reverse stock
        # If db_invoice was fetched via get_invoice_by_id, we might need to refresh items
        self.db.refresh(db_invoice, attribute_names=["items"])
        
        for item in db_invoice.items:
            if item.product_id:
                inventory_service.add_stock(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    company_id=company_id,
                    reference=f"Cancelación de Factura {db_invoice.invoice_number}",
                    reference_id=db_invoice.id,
                    reference_type="INVOICE_CANCEL"
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
                description=f"Anulación de Factura #{db_invoice.invoice_number}"
            )

        # 3. Reverse Treasury Deposit if PAID
        if db_invoice.status == "PAID":
            treasury_service = TreasuryService(self.db)
            # Find the deposit transaction
            # Usually reference matches INV-{id}
            from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
            tx = (
                self.db.query(TreasuryTransaction)
                .filter(
                    TreasuryTransaction.reference == f"INV-{db_invoice.id}",
                    TreasuryTransaction.company_id == company_id,
                    TreasuryTransaction.transaction_type == "DEPOSIT"
                )
                .first()
            )
            if tx:
                # We "withdraw" what was "deposited"
                account_id = tx.bank_account_id or tx.cash_account_id
                account_type = tx.account_type
                if account_id:
                    treasury_service.withdraw(
                        account_type=account_type,
                        account_id=account_id,
                        amount=tx.amount,
                        description=f"Reversión por anulación de factura {db_invoice.invoice_number}",
                        reference=f"REV-INV-{db_invoice.id}",
                        company_id=company_id
                    )

        # 4. Set status to CANCELLED
        db_invoice.status = "CANCELLED"
        self.db.commit()
        self.db.refresh(db_invoice)
        
        return db_invoice
