"""Script de ejemplo para poblar datos contables básicos.

Este script:
- Crea cuentas de tipo REVENUE, COST y EXPENSE (si no existen).
- Genera una factura de venta y una compra para generar asientos contables.
- Deja datos suficientes para que los reportes como "Estado de Resultados" muestren valores distintos de cero.
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from decimal import Decimal
from datetime import datetime, timezone

from app.core.database import SessionLocal, engine
from app.models.sql import company as company_model, user as user_model, chart_of_accounts as coa_model, invoice as inv_model, purchase as purchase_model
from app.services.accounting_service import AccountingService
from app.services.invoicing_service import InvoicingService
from app.services.purchase_service import PurchaseService
from app.services.inventory_service import InventoryService
from app.schemas import invoicing as inv_schema
from app.schemas import purchases as purchase_schema

# ---------------------------------------------------------------------------
# Configuración básica (usa la primera empresa y usuario que existan)
# ---------------------------------------------------------------------------

def get_first_company(db):
    return db.query(company_model.Company).first()

def get_first_user(db):
    return db.query(user_model.User).first()

def ensure_coa(db, company_id):
    """Crea cuentas básicas de ingresos, costos y gastos si no existen."""
    defaults = [
        {"code": "4100", "name": "Ingresos por ventas", "account_type": "REVENUE"},
        {"code": "5100", "name": "Costo de Ventas", "account_type": "COST"},
        {"code": "6200", "name": "Gastos operacionales", "account_type": "EXPENSE"},
    ]
    for acc in defaults:
        existing = (
            db.query(coa_model.ChartOfAccounts)
            .filter(
                coa_model.ChartOfAccounts.company_id == company_id,
                coa_model.ChartOfAccounts.code == acc["code"],
            )
            .first()
        )
        if not existing:
            db.add(
                coa_model.ChartOfAccounts(
                    code=acc["code"],
                    name=acc["name"],
                    account_type=acc["account_type"],
                    company_id=company_id,
                )
            )
    db.commit()

def create_sample_invoice(db, company_id, partner_id, product_id):
    invoicing = InvoicingService(db)
    # Simple invoice con un ítem
    invoice_data = {
        "invoice_number": None,
        "invoice_type": "SALE",
        "partner_id": partner_id,
        "issue_date": datetime.now(timezone.utc),
        "due_date": None,
        "total_amount": Decimal("1000.00"),
        "currency": "COP",
        "status": "ISSUED",
        "cufe": None,
        "xml_ubl": None,
        "estado_dian": "BORRADOR",
        "motivo_rechazo": None,
    }
    inv = invoicing.create_invoice(inv_schema.InvoiceCreate(**invoice_data), company_id)
    # Añadir ítem
    item = inv_model.InvoiceItem(
        invoice_id=inv.id,
        description="Producto de ejemplo",
        quantity=Decimal("1"),
        unit_price=Decimal("1000.00"),
        discount=Decimal("0.00"),
        tax_rate=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        line_total=Decimal("1000.00"),
        product_id=product_id,
        serial_number=None,
    )
    db.add(item)
    db.commit()
    # El método create_invoice ya generó el asiento automático
    return inv

def create_sample_purchase(db, company_id, supplier_id, product_id):
    purchase_srv = PurchaseService(db)
    # Crear compra con un ítem que genera stock
    purchase_data = {
        "purchase_number": f"PUR-{int(datetime.now().timestamp())}",
        "partner_id": supplier_id,
        "subtotal": Decimal("500.00"),
        "tax_amount": Decimal("0.00"),
        "total_amount": Decimal("500.00"),
        "payment_method": "CASH",
        "status": "ISSUED",
        "company_id": company_id,
        "notes": "Compra de muestra",
    }
    purchase = purchase_srv.create_purchase(purchase_schema.PurchaseCreate(**purchase_data), company_id)
    # Añadir ítem de compra
    item = purchase_model.PurchaseItem(
        purchase_id=purchase.id,
        product_id=product_id,
        description="Producto de compra",
        quantity=Decimal("5"),
        unit_price=Decimal("100.00"),
        serial_number=None,
        discount_percent=Decimal("0.00"),
        discount_amount=Decimal("0.00"),
        tax_rate=Decimal("0.00"),
        tax_amount=Decimal("0.00"),
        line_total=Decimal("500.00"),
    )
    db.add(item)
    db.commit()
    # El servicio de compra actualizará inventario y generará el asiento contable
    return purchase

def main():
    db = SessionLocal()
    try:
        company = get_first_company(db)
        user = get_first_user(db)
        if not company or not user:
            print("Necesita al menos una compañía y un usuario creados antes de ejecutar el seed.")
            return
        # ponytail: set tenant ContextVar so the before_cursor_execute event
        # applies app.tenant_id and RLS allows the INSERTs (PG only; SQLite no-op).
        from app.core.tenant_context import current_tenant_id
        current_tenant_id.set(company.id)
        print(f"Usando compañía id={company.id}, nombre={company.name}")
        ensure_coa(db, company.id)
        # Crear proveedor y cliente dummy si no existen
        from app.models.sql.partners import Partner
        partner = db.query(Partner).filter(Partner.company_id == company.id).first()
        if not partner:
            partner = Partner(
                name="Cliente Demo",
                nit="1111111111",
                email="demo@example.com",
                phone="1234567",
                address="Calle 123",
                type="CLIENT",
                company_id=company.id,
            )
            db.add(partner)
            db.commit()
        # Crear producto dummy
        from app.models.sql.inventory import Product
        product = db.query(Product).filter(Product.company_id == company.id).first()
        if not product:
            product = Product(
                sku="SKU001",
                barcode="1234567890123",
                name="Producto Demo",
                description="Producto de prueba",
                category="Demo",
                brand="DemoBrand",
                model="X",
                unit_of_measure="UNIDAD",
                purchase_price=Decimal("100.00"),
                sale_price=Decimal("150.00"),
                stock_level=Decimal("0"),
                min_stock_level=Decimal("0"),
                max_stock_level=Decimal("999999"),
                is_active=True,
                company_id=company.id,
            )
            db.add(product)
            db.commit()
        # Generar datos de ejemplo
        create_sample_invoice(db, company.id, partner.id, product.id)
        create_sample_purchase(db, company.id, partner.id, product.id)
        print("Datos de ejemplo creados correctamente.")
    finally:
        db.close()

if __name__ == "__main__":
    main()
