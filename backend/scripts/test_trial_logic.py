from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.sql.company import Company
from app.core.scheduler import check_trial_expirations

def verify_trial_logic():
    db = SessionLocal()
    
    # 1. Crear empresa de prueba
    test_company = Company(
        name="Empresa Trial Test",
        nit="900999888",
        dv="1",
        legal_representative="Test",
        fecha_inicio_actividades=datetime.now().date(),
        is_trial=True,
        is_active=True
    )
    db.add(test_company)
    db.commit()
    db.refresh(test_company)
    print(f"Empresa creada: {test_company.id}, is_trial={test_company.is_trial}, is_active={test_company.is_active}")

    # 2. Ajustar fecha de creación (65 días atrás)
    old_date = datetime.now(timezone.utc) - timedelta(days=65)
    test_company.created_at = old_date
    db.commit()
    print(f"Fecha de creación ajustada a: {test_company.created_at}")

    # 3. Ejecutar lógica de expiración
    print("Ejecutando check_trial_expirations()...")
    check_trial_expirations()

    # 4. Verificar resultado
    db.refresh(test_company)
    print(f"Estado tras chequeo: is_active={test_company.is_active}")

    # 5. Limpieza
    db.delete(test_company)
    db.commit()
    print("Empresa de prueba eliminada.")
    db.close()

if __name__ == "__main__":
    verify_trial_logic()
