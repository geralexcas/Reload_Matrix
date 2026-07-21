import sys
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.tenant_context import current_tenant_id
from app.services import repair_service, invoicing_service, purchase_service, accounting_service, partner_service, inventory_service
from app.models.sql import user as user_model
from app.core.security import get_password_hash

# Setup
COMPANY_ID = 25
db = SessionLocal()
current_tenant_id.set(COMPANY_ID)

print(f"--- 1. Preparando entorno para empresa {COMPANY_ID} ---")

# Create user
user_data = user_model.User(
    email="technician_evo@example.com",
    username="tec_evo",
    hashed_password=get_password_hash("Password123!"),
    full_name="Tecnico Evo",
    is_active=True,
    is_superuser=False,
    role="TECNICO",
    company_id=COMPANY_ID
)
db.add(user_data)
db.commit()
print("Usuario creado.")

# Create product
inv_service = inventory_service.InventoryService(db)
product = inv_service.create_product({"name": "Componente Reparación", "sku": "COMP-001", "price": 50000, "company_id": COMPANY_ID})
print(f"Producto creado: {product.id}")

print("--- 2. Crear recepción y servicio ---")
# Need to import schemas, too much boilerplate. I will do it simpler.
# Actually, I will just implement the steps as requested.
