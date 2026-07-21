#!/usr/bin/env python3
"""
Script para inicializar la base de datos con el platform-admin.

Crea UNICAMENTE el usuario platform-admin (superuser sin company_id).
Las empresas (tenants) se crean desde el panel de Plataforma en la UI.

Uso:
  docker compose exec backend python scripts/init_database.py
"""

import sys
import os
sys.path.insert(0, '/app')

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash, validate_password_strength
from app.models.sql.user import User
from app.services.permission_service import seed_permissions, assign_role_permissions


PLATFORM_ADMIN_EMAIL = os.getenv("PLATFORM_ADMIN_EMAIL", "admin@reloadmatrix.com")
PLATFORM_ADMIN_USERNAME = os.getenv("PLATFORM_ADMIN_USERNAME", "platform_admin")
PLATFORM_ADMIN_PASSWORD = os.getenv("PLATFORM_ADMIN_PASSWORD", "AdminReload@2026")
PLATFORM_ADMIN_FULL_NAME = os.getenv("PLATFORM_ADMIN_FULL_NAME", "Platform Admin")


def init_database():
    """Crea el platform-admin inicial."""
    print("=" * 60)
    print("  Reload Matrix — Inicializacion de Base de Datos")
    print("=" * 60)

    # Crear todas las tablas
    print("\n  Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("  Tablas creadas")

    db = SessionLocal()

    try:
        # Verificar si ya existe el platform-admin
        existing = (
            db.query(User)
            .filter(User.email == PLATFORM_ADMIN_EMAIL)
            .first()
        )
        if existing:
            print(f"\n  El platform-admin ya existe ({existing.email})")
            print("     Para resetear la contrasena use:")
            print("     python scripts/create_admin.py --reset")
            return

        # Validar fortaleza de contrasena
        is_valid, message = validate_password_strength(PLATFORM_ADMIN_PASSWORD)
        if not is_valid:
            print(f"\n  ERROR: La contrasena no cumple los requisitos: {message}")
            print("     Setee PLATFORM_ADMIN_PASSWORD con una contrasena fuerte")
            print("     (min 8 chars, mayuscula, minuscula, numero, caracter especial)")
            sys.exit(1)

        # Crear platform-admin
        print("\n  Creando platform-admin...")
        admin = User(
            email=PLATFORM_ADMIN_EMAIL,
            username=PLATFORM_ADMIN_USERNAME,
            hashed_password=get_password_hash(PLATFORM_ADMIN_PASSWORD),
            is_active=True,
            is_superuser=True,
            full_name=PLATFORM_ADMIN_FULL_NAME,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        seed_permissions(db)
        assign_role_permissions(db, admin)
        db.commit()

        print("\n  " + "=" * 56)
        print("  INICIALIZACION COMPLETA")
        print("  " + "=" * 56)
        print(f"\n    Email:     {PLATFORM_ADMIN_EMAIL}")
        print(f"    Password:  {PLATFORM_ADMIN_PASSWORD}")
        print(f"    Username:  {PLATFORM_ADMIN_USERNAME}")
        print("\n    Accede a:  http://localhost:8081/login")
        print("\n  IMPORTANTE: Este usuario es PLATFORM-ADMIN:")
        print("    - Gestiona empresas desde el panel 'Plataforma'")
        print("    - Crea tenants con su admin inicial desde la UI")
        print("    - NO opera como tenant (no crea facturas, inventario, etc.)")
        print("\n  CAMBIA LA CONTRASENA INMEDIATAMENTE:")
        print("    python scripts/create_admin.py --reset --password 'TuNuevaClave@123'")

    except Exception as e:
        print(f"\n  Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_database()