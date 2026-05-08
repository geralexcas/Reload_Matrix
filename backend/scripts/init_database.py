#!/usr/bin/env python3
"""
Script para inicializar datos por defecto en la base de datos.
Crea usuario admin, empresa demo y plan de cuentas.
"""

import sys
import os
sys.path.insert(0, '/app')

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.sql.user import User
from app.models.sql.company import Company
from app.models.sql.partners import Partner
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
from sqlalchemy.exc import IntegrityError
from decimal import Decimal

def init_database():
    """Inicializa la base de datos con datos por defecto."""
    
    print("🔧 Inicializando base de datos...")
    
    # Crear todas las tablas
    print("  📋 Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("  ✅ Tablas creadas")
    
    db = SessionLocal()
    
    try:
        # 1. Verificar si ya existe el admin
        existing_admin = db.query(User).filter(User.email == "admin@admin.com").first()
        if existing_admin:
            print("  ℹ️  El usuario admin ya existe")
            admin = existing_admin
        else:
            # Crear usuario admin
            print("  👤 Creando usuario admin...")
            admin = User(
                email="admin@admin.com",
                username="admin",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_superuser=True,
                full_name="Administrador Sistema"
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print("  ✅ Usuario admin creado")
        
        # 2. Verificar si ya existe empresa
        existing_company = db.query(Company).first()
        if existing_company:
            print("  ℹ️  La empresa demo ya existe")
            company = existing_company
        else:
            # Crear empresa demo
            print("  🏢 Creando empresa demo...")
            from datetime import date
            company = Company(
                name="Mi Empresa",
                nit="900123456",
                dv="9",
                legal_representative="Administrador",
                phone="3001234567",
                email="admin@admin.com",
                address="Calle 123 # 45-67, Bogotá",
                regimen="COMUN",
                fecha_inicio_actividades=date(2024, 1, 1),
                is_active=True
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            print("  ✅ Empresa demo creada")
        
        # 3. Crear proveedor demo
        existing_partner = db.query(Partner).filter(Partner.company_id == company.id).first()
        if not existing_partner:
            print("  🤝 Creando proveedor demo...")
            partner = Partner(
                name="Proveedor Demo",
                nit="123456789",
                dv="1",
                phone="3001234567",
                email="proveedor@demo.com",
                address="Calle 123",
                partner_type="SUPPLIER",
                company_id=company.id,
                is_active=True
            )
            db.add(partner)
            db.commit()
            db.refresh(partner)
            print("  ✅ Proveedor demo creado")
        
        # 4. Crear plan de cuentas
        print("  📊 Creando plan de cuentas...")
        
        # Obtener servicio de accounting
        from app.services.accounting_service import AccountingService
        accounting_service = AccountingService(db)
        
        # Crear plan de cuentas por defecto
        accounts = accounting_service.create_default_chart_of_accounts(company.id)
        print(f"  ✅ {len(accounts)} cuentas creadas")
        
        print("\n" + "="*50)
        print("✅ INICIALIZACIÓN COMPLETA")
        print("="*50)
        print("\n📋 DATOS DE ACCESO:")
        print("   📧 Email: admin@admin.com")
        print("   🔑 Password: admin123")
        print("\n🏢 Empresa: Mi Empresa (NIT: 900123456789)")
        print("\n🌐 Accede a: http://localhost:8081")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()