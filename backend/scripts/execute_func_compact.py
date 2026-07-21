import sys
from decimal import Decimal
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.tenant_context import current_tenant_id
from app.services import inventory_service
from app.schemas import inventory as inv_schema
from app.models.sql import user as user_model
from app.models.sql import company as company_model
from app.models.sql.inventory import Product
from app.core.security import get_password_hash

# Setup
db = SessionLocal()

# Encontrar empresa Evocomputo (asumiré ID 25 basada en listado previo)
company = db.query(company_model.Company).filter(company_model.Company.name == "evocomputo").first()
if not company:
    company = db.query(company_model.Company).filter(company_model.Company.id == 1).first()

COMPANY_ID = company.id
current_tenant_id.set(COMPANY_ID)
print(f"--- Empresa seleccionada: {company.name} (ID: {COMPANY_ID}) ---")

# 2. Agregar producto (si no existe)
inv_service = inventory_service.InventoryService(db)
existing_product = db.query(Product).filter(Product.sku == "COMP-001", Product.company_id == COMPANY_ID).first()
if not existing_product:
    try:
        product_data = inv_schema.ProductCreate(
            name="Componente Reparación",
            sku="COMP-001",
            purchase_price=Decimal("10000.00"),
            sale_price=Decimal("50000.00"),
            company_id=COMPANY_ID
        )
        product = inv_service.create_product(product_data, COMPANY_ID, commit=True)
        print(f"Producto creado: {product.id}")
    except Exception as e:
        print(f"Error creando producto: {e}")
else:
    print("Producto ya existe (omitido).")

db.close()
