import os
import sys

# Ensure backend directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.sql.audit import Permission
from app.core.database import SessionLocal

def init_permissions():
    db = SessionLocal()
    
    # Lista de permisos básicos
    permissions = [
        {"name": "view_company", "module": "company", "action": "view"},
        {"name": "manage_clients", "module": "partners", "action": "manage"},
        {"name": "manage_suppliers", "module": "partners", "action": "manage"},
        {"name": "manage_products", "module": "inventory", "action": "manage"},
        {"name": "manage_repairs", "module": "repair", "action": "manage"},
        {"name": "manage_invoices", "module": "invoicing", "action": "manage"},
        {"name": "manage_purchases", "module": "purchases", "action": "manage"},
        {"name": "view_accounting", "module": "accounting", "action": "view"},
    ]
    
    added_count = 0
    for perm_data in permissions:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            perm = Permission(**perm_data)
            db.add(perm)
            added_count += 1
    
    if added_count > 0:
        db.commit()
        print(f"✅ Se inicializaron {added_count} permisos correctamente.")
    else:
        print("ℹ️ Todos los permisos básicos ya estaban registrados.")

if __name__ == "__main__":
    init_permissions()
