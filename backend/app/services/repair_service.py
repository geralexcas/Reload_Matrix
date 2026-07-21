from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from app.models.sql.repair import RepairOrder, RepairItem, Technician, Warranty
from app.models.sql.invoicing import Invoice, InvoiceItem
from app.models.sql import company as company_model
from app.models.sql import partners as partner_model
from app.schemas import repair as rep_schema
from app.schemas import invoicing as inv_schema
from app.schemas.payment import POSPayment  # Se asume que existe o crearé un base model
from decimal import Decimal
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RepairService:
    def __init__(self, db: Session):
        self.db = db

    def generate_repair_number(self, company_id: int) -> str:
        """
        Generates the next repair order number using the InvoiceResolution table with row-level locking.
        Uses resolution_type='REPAIR'.
        """
        from app.models.sql.invoicing import InvoiceResolution
        
        # Find the active resolution for repairs, locking it for update
        resolution = (
            self.db.query(InvoiceResolution)
            .filter(
                InvoiceResolution.company_id == company_id,
                InvoiceResolution.resolution_type == "REPAIR",
                InvoiceResolution.is_active == True
            )
            .with_for_update()
            .first()
        )

        if not resolution:
            # Create a default resolution "REP-"
            resolution = InvoiceResolution(
                company_id=company_id,
                resolution_type="REPAIR",
                prefix="REP-",
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

    # Technician methods
    def create_technician(
        self, technician: rep_schema.TechnicianCreate, company_id: int, commit: bool = False
    ) -> Technician:
        db_tech = Technician(**technician.model_dump(), company_id=company_id)
        self.db.add(db_tech)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(db_tech)
        return db_tech

    def get_technicians(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        from app.models.sql.user import User
        
        logger.debug("Getting technicians for company_id=%s", company_id)
        
        users = (
            self.db.query(User)
            .filter(User.company_id == company_id, User.role == "TECNICO")
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        logger.debug("Found %d users with role TECNICO", len(users))
        
        # Format for TechnicianResponse schema
        technician_list = []
        for u in users:
            name_parts = (u.full_name or u.username).split(" ")
            first_name = name_parts[0]
            last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            # Use basic ISO format for dates to avoid serialization issues
            technician_list.append({
                "id": u.id,
                "first_name": first_name,
                "last_name": last_name,
                "employee_id": u.username,
                "specialty": "Técnico General",
                "is_active": u.is_active,
                "company_id": u.company_id,
                "created_at": u.created_at,
                "updated_at": u.updated_at
            })
        logger.debug("Returning %d formatted technicians", len(technician_list))
        return technician_list

    def get_technician_by_id(
        self, technician_id: int, company_id: int
    ) -> Optional[Technician]:
        return (
            self.db.query(Technician)
            .filter(
                Technician.id == technician_id,
                Technician.company_id == company_id,
            )
            .first()
        )

    def update_technician(
        self,
        technician_id: int,
        technician: rep_schema.TechnicianCreate,
        company_id: int,
        commit: bool = False,
    ) -> Optional[Technician]:
        db_tech = self.get_technician_by_id(technician_id, company_id)
        if db_tech:
            for key, value in technician.model_dump().items():
                setattr(db_tech, key, value)
            self.db.flush()
            if commit:
                self.db.commit()
            self.db.refresh(db_tech)
        return db_tech

    def delete_technician(self, technician_id: int, company_id: int, commit: bool = False) -> bool:
        db_tech = self.get_technician_by_id(technician_id, company_id)
        if db_tech:
            self.db.delete(db_tech)
            if commit:
                self.db.commit()
            return True
        return False

    # Repair Order methods
    def create_repair_order(
        self, repair_order: rep_schema.RepairOrderCreate, company_id: int, commit: bool = False
    ) -> RepairOrder:
        ro_data = repair_order.model_dump()
        if not ro_data.get("order_number") or ro_data["order_number"].startswith("REP-17"):
            ro_data["order_number"] = self.generate_repair_number(company_id)
            
        db_ro = RepairOrder(**ro_data, company_id=company_id)
        self.db.add(db_ro)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(db_ro)
        return db_ro

    def create_repair_order_simple(
        self, repair_order: rep_schema.RepairOrderSimpleCreate, company_id: int, commit: bool = False
    ) -> RepairOrder:
        order_number = repair_order.order_number
        if not order_number or order_number.startswith("REP-17"):
            order_number = self.generate_repair_number(company_id)
            
        db_ro = RepairOrder(
            order_number=order_number,
            partner_id=repair_order.partner_id,
            technician_id=repair_order.technician_id,
            issue_date=repair_order.issue_date,
            expected_delivery_date=repair_order.expected_delivery_date,
            actual_delivery_date=repair_order.actual_delivery_date,
            problem_description=repair_order.problem_description,
            diagnosis=repair_order.diagnosis,
            service_notes=repair_order.service_notes,
            status=repair_order.status,
            warranty_applied=repair_order.warranty_applied,
            total_labor_cost=repair_order.total_labor_cost,
            total_parts_cost=repair_order.total_parts_cost,
            total_amount=repair_order.total_amount,
            company_id=company_id,
        )
        self.db.add(db_ro)
        self.db.flush()

        # Create primary repair item if device details are provided
        if repair_order.device_type or repair_order.brand or repair_order.model or repair_order.serial_number:
            db_ri = RepairItem(
                repair_order_id=db_ro.id,
                description=repair_order.device_type or "Dispositivo",
                brand=repair_order.brand,
                model=repair_order.model,
                serial_number=repair_order.serial_number,
                issue_reported=repair_order.problem_description,
                quantity=1,
                unit_cost=Decimal("0.00"),
                line_total=Decimal("0.00"),
                warranty_status="IN_WARRANTY" if repair_order.warranty_applied else "NO_WARRANTY"
            )
            self.db.add(db_ri)

        if commit:
            self.db.commit()
        self.db.refresh(db_ro)
        return db_ro

    def create_repair_order_with_items(
        self,
        repair_order_with_items: rep_schema.RepairOrderWithItemsCreate,
        company_id: int,
        commit: bool = False,
    ) -> RepairOrder:
        order_number = repair_order_with_items.order_number
        if not order_number or order_number.startswith("REP-17"):
            order_number = self.generate_repair_number(company_id)
            
        # Create the repair order
        db_ro = RepairOrder(
            order_number=order_number,
            partner_id=repair_order_with_items.partner_id,
            technician_id=repair_order_with_items.technician_id,
            issue_date=repair_order_with_items.issue_date,
            expected_delivery_date=repair_order_with_items.expected_delivery_date,
            actual_delivery_date=repair_order_with_items.actual_delivery_date,
            problem_description=repair_order_with_items.problem_description,
            diagnosis=repair_order_with_items.diagnosis,
            service_notes=repair_order_with_items.service_notes,
            status=repair_order_with_items.status,
            warranty_applied=repair_order_with_items.warranty_applied,
            total_labor_cost=Decimal("0.00"),  # Will be calculated from items
            total_parts_cost=Decimal("0.00"),  # Will be calculated from items
            total_amount=repair_order_with_items.total_amount,
            cufe=repair_order_with_items.cufe,
            xml_ubl=repair_order_with_items.xml_ubl,
            estado_dian=repair_order_with_items.estado_dian,
            motivo_rechazo=repair_order_with_items.motivo_rechazo,
            company_id=company_id,
        )
        self.db.add(db_ro)
        self.db.flush()  # To get the ID without committing

        # Create the repair order items
        total_labor_cost = Decimal("0.00")
        total_parts_cost = Decimal("0.00")

        for item in repair_order_with_items.items:
            db_ri = RepairItem(
                repair_order_id=db_ro.id,
                description=item.description,
                serial_number=item.serial_number,
                model=item.model,
                brand=item.brand,
                issue_reported=item.issue_reported,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                discount=item.discount,
                tax_rate=item.tax_rate,
                tax_amount=item.tax_amount,
                line_total=item.line_total,
                product_id=item.product_id,
                warranty_status=item.warranty_status,
                warranty_days=item.warranty_days,
            )
            self.db.add(db_ri)

            # Calculate costs based on warranty status
            if item.warranty_status == "NO_WARRANTY":
                total_parts_cost += item.quantity * item.unit_price
            # For warranty items, we track costs but don't charge customer
            # Labor costs would need to be determined separately

        # Update totals
        db_ro.total_labor_cost = (
            total_labor_cost  # This would need more detailed tracking
        )
        db_ro.total_parts_cost = total_parts_cost
        db_ro.total_amount = total_parts_cost  # Simplified for now

        if commit:
            self.db.commit()
        self.db.refresh(db_ro)
        return db_ro

    def get_repair_orders(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[RepairOrder]:
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(RepairOrder)
            .options(joinedload(RepairOrder.partner))
            .filter(RepairOrder.company_id == company_id)
            .order_by(RepairOrder.created_at.desc())  # Most recent orders first
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_repair_order_by_id(
        self, repair_order_id: int, company_id: int
    ) -> Optional[RepairOrder]:
        return (
            self.db.query(RepairOrder)
            .filter(
                RepairOrder.id == repair_order_id,
                RepairOrder.company_id == company_id,
            )
            .first()
        )

    def get_repair_order_with_items(
        self, repair_order_id: int, company_id: int
    ) -> Optional[RepairOrder]:
        from sqlalchemy.orm import joinedload

        ro = (
            self.db.query(RepairOrder)
            .options(
                joinedload(RepairOrder.partner),
                joinedload(RepairOrder.technician),
            )
            .filter(
                RepairOrder.id == repair_order_id,
                RepairOrder.company_id == company_id,
            )
            .first()
        )
        return ro

    def update_repair_order(
        self,
        repair_order_id: int,
        repair_order: rep_schema.RepairOrderUpdate,
        company_id: int,
        commit: bool = False,
    ) -> Optional[RepairOrder]:
        db_ro = self.get_repair_order_by_id(repair_order_id, company_id)
        if db_ro:
            update_data = repair_order.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if value is not None:
                    setattr(db_ro, key, value)
            self.db.flush()
            if commit:
                self.db.commit()
            self.db.refresh(db_ro)
        return db_ro

    def delete_repair_order(self, repair_order_id: int, company_id: int, commit: bool = False) -> bool:
        db_ro = self.get_repair_order_by_id(repair_order_id, company_id)
        if db_ro:
            self.db.delete(db_ro)
            if commit:
                self.db.commit()
            return True
        return False

    def cancel_repair_order(self, repair_order_id: int, company_id: int, commit: bool = False) -> RepairOrder:
        """
        Cancel a repair order and reverse all effects (inventory, invoice)
        """
        db_ro = self.get_repair_order_with_items(repair_order_id, company_id)
        if not db_ro:
            raise ValueError("Repair order not found")

        if db_ro.status == "CANCELLED":
            return db_ro

        try:
            # 1. Revertir inventario ANTES de cancelar la factura
            if db_ro.invoice_id and db_ro.items:
                from app.services.inventory_service import InventoryService
                inventory_service = InventoryService(self.db)
                
                for repair_item in db_ro.items:
                    if repair_item.product_id:
                        # Devolver al inventario
                        inventory_service.add_stock(
                            product_id=repair_item.product_id,
                            quantity=repair_item.quantity,
                            company_id=company_id,
                            reference=f"Cancel Repair {db_ro.order_number}",
                            reference_id=db_ro.id,
                            reference_type="REPAIR_CANCEL",
                            commit=False,
                        )

            # 2. Cancelar factura si existe
            if db_ro.invoice_id:
                from app.services.invoicing_service import InvoicingService
                inv_service = InvoicingService(self.db)
                try:
                    if hasattr(inv_service, 'cancel_invoice'):
                        inv_service.cancel_invoice(db_ro.invoice_id, company_id)
                    else:
                        from app.models.sql.invoicing import Invoice
                        invoice = self.db.query(Invoice).filter(
                            Invoice.id == db_ro.invoice_id
                        ).first()
                        if invoice:
                            invoice.status = "CANCELLED"
                except Exception as e:
                    logger.warning("Associated invoice %s could not be cancelled: %s", db_ro.invoice_id, e)

            # 3. Marcar como cancelada
            db_ro.status = "CANCELLED"
            self.db.flush()
            if commit:
                self.db.commit()
            self.db.refresh(db_ro)
            
            return db_ro
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al cancelar orden de reparación: {str(e)}")

    # Repair Item methods
    def create_repair_item(
        self,
        repair_item: rep_schema.RepairItemCreate,
        repair_order_id: int,
        company_id: int,
        commit: bool = False,
    ) -> RepairItem:
        # Verify repair order exists
        db_ro = self.get_repair_order_by_id(repair_order_id, company_id)
        if not db_ro:
            raise ValueError("Repair order not found")

        # Create the item
        db_ri = RepairItem(
            repair_order_id=repair_order_id,
            description=repair_item.description,
            serial_number=repair_item.serial_number,
            model=repair_item.model,
            brand=repair_item.brand,
            issue_reported=repair_item.issue_reported,
            quantity=repair_item.quantity,
            unit_cost=repair_item.unit_cost,
            discount=repair_item.discount,
            tax_rate=repair_item.tax_rate,
            tax_amount=repair_item.tax_amount,
            line_total=repair_item.line_total,
            product_id=repair_item.product_id,
            warranty_status=repair_item.warranty_status,
            warranty_days=repair_item.warranty_days,
        )
        self.db.add(db_ri)
        self.db.flush()

        # Update totals
        if repair_item.warranty_status == "NO_WARRANTY":
            if repair_item.product_id:
                db_ro.total_parts_cost += repair_item.line_total
            else:
                db_ro.total_labor_cost += repair_item.line_total
            db_ro.total_amount += repair_item.line_total

        if commit:
            self.db.commit()
        self.db.refresh(db_ri)
        return db_ri

    def delete_repair_item(
        self, item_id: int, repair_order_id: int, company_id: int, commit: bool = False
    ) -> bool:
        from app.models.sql.repair import RepairItem

        item = (
            self.db.query(RepairItem)
            .filter(
                RepairItem.id == item_id, RepairItem.repair_order_id == repair_order_id
            )
            .first()
        )
        if not item:
            return False

        # Get the repair order
        db_ro = self.get_repair_order_by_id(repair_order_id, company_id)
        if db_ro:
            # Update totals
            if item.warranty_status == "NO_WARRANTY":
                if item.product_id:
                    db_ro.total_parts_cost -= item.line_total
                else:
                    db_ro.total_labor_cost -= item.line_total
                db_ro.total_amount -= item.line_total

        self.db.delete(item)
        if commit:
            self.db.commit()
        return True

    def apply_warranty(
        self, repair_order_id: int, company_id: int, commit: bool = False
    ) -> Optional[RepairOrder]:
        """
        Apply warranty to a repair order - marks it as warranty work
        and prevents charging the customer for parts/labor
        """
        db_ro = self.get_repair_order_by_id(repair_order_id, company_id)
        if db_ro:
            db_ro.warranty_applied = True
            # When warranty is applied, the customer doesn't pay
            # but we still track costs internally
            db_ro.total_amount = Decimal("0.00")
            self.db.flush()
            if commit:
                self.db.commit()
            self.db.refresh(db_ro)
        return db_ro

    def create_invoice_from_repair(
        self, repair_order_id: int, company_id: int, payment_data: Optional[POSPayment] = None, commit: bool = False
    ) -> Optional[Invoice]:
        """
        Automatically generate an invoice from a completed repair order
        """
        db_ro = self.get_repair_order_by_id(repair_order_id, company_id)
        if not db_ro:
            return None

        # Check if repair is cancelled
        if db_ro.status == "CANCELLED":
            raise ValueError(
                "Cannot generate invoice for a cancelled repair order"
            )
            
        if not db_ro.items:
            raise ValueError(
                "Repair order must have at least one service or part to generate an invoice"
            )

        # Check if invoice already exists
        if db_ro.invoice_id:
            existing_invoice = (
                self.db.query(Invoice).filter(Invoice.id == db_ro.invoice_id).first()
            )
            if existing_invoice:
                return existing_invoice

        # Get partner (customer) info
        partner = (
            self.db.query(partner_model.Partner)
            .filter(partner_model.Partner.id == db_ro.partner_id)
            .first()
        )
        if not partner:
            raise ValueError("Partner not found")

        # Calculate totals from repair items
        total_labor_cost = Decimal("0.00")
        total_parts_cost = Decimal("0.00")

        for item in db_ro.items:
            # For simplicity, we're treating all items as parts cost
            # In a real system, you'd distinguish between labor and parts
            item_total = item.quantity * item.unit_cost
            total_parts_cost += item_total

        # If warranty was applied, customer pays nothing
        if db_ro.warranty_applied:
            total_amount = Decimal("0.00")
        else:
            total_amount = (
                total_parts_cost  # Simplified - would include labor in real system
            )

        # Generate sequence invoice number
        from app.services.invoicing_service import InvoicingService
        invoice_number = InvoicingService(self.db).generate_invoice_number(company_id, "SALE")

        invoice_status = "DRAFT"
        if payment_data and payment_data.is_paid:
            invoice_status = "PAID"
        
        # Create invoice
        invoice_data = inv_schema.InvoiceCreate(
            invoice_number=invoice_number,
            invoice_type="SALE",
            partner_id=db_ro.partner_id,
            issue_date=db_ro.issue_date,
            due_date=None,  # Could set based on company policy
            total_amount=total_amount,
            currency=db_ro.currency,
            status=invoice_status,
            estado_dian="BORRADOR",
            motivo_rechazo=None,
        )

        db_invoice = Invoice(**invoice_data.model_dump(), company_id=company_id)
        self.db.add(db_invoice)
        self.db.flush()  # Get ID without committing

        # Create invoice items from repair items
        for repair_item in db_ro.items:
            invoice_item_data = inv_schema.InvoiceItemCreate(
                description=repair_item.description,
                quantity=repair_item.quantity,
                unit_price=repair_item.unit_cost,
                discount=Decimal("0.00"),
                tax_rate=Decimal(
                    "0.00"
                ),  # Simplified - would calculate based on tax rules
                tax_amount=Decimal("0.00"),
                line_total=repair_item.quantity * repair_item.unit_cost,
                product_id=repair_item.product_id,
            )

            db_invoice_item = InvoiceItem(
                invoice_id=db_invoice.id, **invoice_item_data.model_dump()
            )
            self.db.add(db_invoice_item)

        # Link invoice to repair order
        db_ro.invoice_id = db_invoice.id

        # Deduct inventory for repair items that have products linked
        from app.services.inventory_service import InventoryService

        inventory_service = InventoryService(self.db)

        deducted_products = []
        for repair_item in db_ro.items:
            if repair_item.product_id:
                product = inventory_service.deduct_stock(
                    product_id=repair_item.product_id,
                    quantity=repair_item.quantity,
                    company_id=company_id,
                )
                deducted_products.append(
                    {
                        "product_id": repair_item.product_id,
                        "product_name": product.name,
                        "quantity_deducted": repair_item.quantity,
                        "remaining_stock": product.stock_level,
                    }
                )

        # Create automatic journal entry
        from app.services.accounting_service import AccountingService

        accounting_service = AccountingService(self.db)

        if db_ro.warranty_applied:
            # Warranty: record costs without revenue
            accounting_service._create_warranty_journal_entry(
                invoice_id=db_invoice.id,
                company_id=company_id,
                parts_cost=total_parts_cost,
                labor_cost=total_labor_cost,
            )
        else:
            # Normal invoice: create revenue journal entry
            tax_amount = Decimal("0.00")
            for item in db_ro.items:
                tax_amount += item.tax_amount

            accounting_service.create_journal_entry_from_invoice(
                invoice_id=db_invoice.id,
                company_id=company_id,
                total_amount=total_amount,
                subtotal=total_parts_cost,
                tax_amount=tax_amount,
                partner_id=db_ro.partner_id,
                is_warranty=False,
                source_type="REPAIR",
                is_paid=payment_data.is_paid if payment_data else False,
                payment_method=payment_data.payment_method if payment_data else "CREDIT",
                payment_account_id=payment_data.payment_account_id if payment_data else None,
            )
            
        # Register payment if provided
        if payment_data and payment_data.is_paid and payment_data.payment_account_type and payment_data.payment_account_id:
            from app.services.treasury_service import TreasuryService
            treasury_service = TreasuryService(self.db)
            
            treasury_service.deposit(
                account_type=payment_data.payment_account_type,
                account_id=payment_data.payment_account_id,
                amount=payment_data.amount_paid or total_amount,
                description=f"Cobro reparación {invoice_number}",
                reference=payment_data.reference or f"Pago Fra. {invoice_number}",
                company_id=company_id,
                skip_journal_entry=True
            )

        if commit:
            self.db.commit()
        self.db.refresh(db_invoice)
        return db_invoice

    # Warranty methods
    def create_warranty(
        self, warranty: rep_schema.WarrantyCreate, company_id: int, commit: bool = False
    ) -> Warranty:
        if warranty.start_date >= warranty.end_date:
            raise ValueError("End date must be after start date")

        db_ro = (
            self.db.query(RepairOrder)
            .filter(
                RepairOrder.id == warranty.repair_order_id,
                RepairOrder.company_id == company_id,
            )
            .first()
        )
        if not db_ro:
            raise ValueError("Repair order not found")

        if warranty.repair_item_id:
            db_ri = (
                self.db.query(RepairItem)
                .filter(
                    RepairItem.id == warranty.repair_item_id,
                    RepairItem.repair_order_id == warranty.repair_order_id,
                )
                .first()
            )
            if not db_ri:
                raise ValueError("Repair item not found in this repair order")

        db_warranty = Warranty(
            repair_order_id=warranty.repair_order_id,
            repair_item_id=warranty.repair_item_id,
            company_id=company_id,
            warranty_type=warranty.warranty_type,
            start_date=warranty.start_date,
            end_date=warranty.end_date,
            description=warranty.description,
            terms_and_conditions=warranty.terms_and_conditions,
            status="ACTIVE",
        )
        self.db.add(db_warranty)
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(db_warranty)
        return db_warranty

    def get_warranties(
        self,
        company_id: int,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[str] = None,
    ) -> List[Warranty]:
        query = self.db.query(Warranty).filter(Warranty.company_id == company_id)
        if status_filter:
            query = query.filter(Warranty.status == status_filter)
        return query.offset(skip).limit(limit).all()

    def get_warranty_by_id(
        self, warranty_id: int, company_id: int
    ) -> Optional[Warranty]:
        return (
            self.db.query(Warranty)
            .filter(
                Warranty.id == warranty_id,
                Warranty.company_id == company_id,
            )
            .first()
        )

    def get_warranties_by_repair_order(
        self, repair_order_id: int, company_id: int
    ) -> List[Warranty]:
        return (
            self.db.query(Warranty)
            .filter(
                Warranty.repair_order_id == repair_order_id,
                Warranty.company_id == company_id,
            )
            .all()
        )

    def update_warranty_status(
        self, warranty_id: int, company_id: int, status: str, commit: bool = False
    ) -> Optional[Warranty]:
        allowed = ["ACTIVE", "EXPIRED", "VOID", "CLAIMED"]
        if status not in allowed:
            raise ValueError(f"Status must be one of {allowed}")

        db_warranty = self.get_warranty_by_id(warranty_id, company_id)
        if db_warranty:
            db_warranty.status = status
            self.db.flush()
            if commit:
                self.db.commit()
            self.db.refresh(db_warranty)
        return db_warranty

    def file_warranty_claim(
        self,
        warranty_id: int,
        company_id: int,
        claim: rep_schema.WarrantyClaim,
        commit: bool = False,
    ) -> Optional[Warranty]:
        db_warranty = self.get_warranty_by_id(warranty_id, company_id)
        if not db_warranty:
            raise ValueError("Warranty not found")

        if db_warranty.status != "ACTIVE":
            raise ValueError("Warranty must be active to file a claim")

        if db_warranty.end_date < datetime.now(timezone.utc):
            db_warranty.status = "EXPIRED"
            if commit:
                self.db.commit()
            raise ValueError("Warranty has expired")

        db_warranty.status = "CLAIMED"
        db_warranty.claim_date = datetime.now(timezone.utc)
        db_warranty.claim_description = claim.claim_description
        db_warranty.claim_resolution = claim.claim_resolution
        self.db.flush()
        if commit:
            self.db.commit()
        self.db.refresh(db_warranty)
        return db_warranty

    def check_expired_warranties(self, company_id: int, commit: bool = False) -> List[Warranty]:
        now = datetime.now(timezone.utc)
        expired = (
            self.db.query(Warranty)
            .filter(
                Warranty.company_id == company_id,
                Warranty.status == "ACTIVE",
                Warranty.end_date < now,
            )
            .all()
        )
        for w in expired:
            w.status = "EXPIRED"
        if expired and commit:
            self.db.commit()
        return expired

    def delete_warranty(self, warranty_id: int, company_id: int, commit: bool = False) -> bool:
        db_warranty = self.get_warranty_by_id(warranty_id, company_id)
        if db_warranty:
            self.db.delete(db_warranty)
            if commit:
                self.db.commit()
            return True
        return False
