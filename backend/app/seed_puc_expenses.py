try:
    from app.core.database import SessionLocal
    from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
except ImportError:
    from core.database import SessionLocal
    from models.sql.accounting.chart_of_accounts import ChartOfAccounts

def seed_expenses():
    db = SessionLocal()
    company_id = 1
    
    expenses_to_add = [
        # Gastos de Personal
        {"code": "5105", "name": "Gastos de Personal", "account_type": "EXPENSE"},
        {"code": "510506", "name": "Sueldos", "account_type": "EXPENSE"},
        # Arrendamientos
        {"code": "5120", "name": "Arrendamientos", "account_type": "EXPENSE"},
        {"code": "512010", "name": "Construcciones y Edificaciones (Arriendo)", "account_type": "EXPENSE"},
        # Servicios
        {"code": "5135", "name": "Servicios", "account_type": "EXPENSE"},
        {"code": "513525", "name": "Acueducto y Alcantarillado", "account_type": "EXPENSE"},
        {"code": "513530", "name": "Energía Eléctrica", "account_type": "EXPENSE"},
        {"code": "513535", "name": "Teléfono", "account_type": "EXPENSE"},
        # Mantenimiento
        {"code": "5145", "name": "Mantenimiento y Reparaciones", "account_type": "EXPENSE"},
        {"code": "514510", "name": "Construcciones y Edificaciones (Mantenimiento)", "account_type": "EXPENSE"},
        {"code": "514525", "name": "Equipo de Computación y Comunicación", "account_type": "EXPENSE"},
    ]
    
    added_count = 0
    for acc in expenses_to_add:
        # Check if already exists
        existing = db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.code == acc["code"]
        ).first()
        
        if not existing:
            new_acc = ChartOfAccounts(
                code=acc["code"],
                name=acc["name"],
                account_type=acc["account_type"],
                company_id=company_id,
                is_active=True
            )
            db.add(new_acc)
            added_count += 1
            
    db.commit()
    print(f"Se agregaron {added_count} cuentas de gastos exitosamente.")
    db.close()

if __name__ == "__main__":
    seed_expenses()
