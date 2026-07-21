#!/usr/bin/env python3
"""
Script para crear usuario administrador en Reload Matrix.

Dos tipos de admin:
  - PLATFORM-ADMIN: superuser SIN company_id. Gestiona todas las empresas
    desde el panel Plataforma. No opera como tenant.
  - TENANT-ADMIN: superuser CON company_id. Administra una empresa especifica.

Uso:
  # Crear platform-admin (gestiona tenants, no opera como tenant):
  docker compose exec backend python scripts/create_admin.py

  # Crear tenant-admin de una empresa especifica:
  docker compose exec backend python scripts/create_admin.py --company-id 3

  # Parametros personalizados:
  python scripts/create_admin.py --email admin@empresa.com --username admin --password "Admin@123456"

  # Resetear contrasena de un admin existente:
  python scripts/create_admin.py --reset --password "NuevaClave@123"
"""

import sys
import os
import argparse

# Agregar el directorio backend al path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)


def get_db_session():
    """Obtener sesión de base de datos (PostgreSQL)"""
    from app.core.database import SessionLocal, engine, Base
    
    # Asegurar que las tablas existan
    Base.metadata.create_all(bind=engine)
    
    return SessionLocal()


def create_admin_user(db, email, username, password, full_name, company_id=None, reset=False):
    from app.core.security import get_password_hash, validate_password_strength
    from app.models.sql.user import User

    existing = (
        db.query(User)
        .filter((User.email == email) | (User.username == username))
        .first()
    )
    if existing:
        if not reset:
            print(
                f"ERROR: Usuario ya existe (id={existing.id}, username={existing.username}). Use --reset para actualizar contraseña."
            )
            return None
        is_valid, message = validate_password_strength(password)
        if not is_valid:
            print(f"ERROR: {message}")
            return None
        existing.hashed_password = get_password_hash(password)
        db.commit()
        db.refresh(existing)
        print("✅ Contraseña actualizada exitosamente:")
        print(f"  ID: {existing.id}")
        print(f"  Username: {existing.username}")
        print(f"  Email: {existing.email}")
        return existing

    is_valid, message = validate_password_strength(password)
    if not is_valid:
        print(f"ERROR: {message}")
        return None

    hashed_password = get_password_hash(password)
    user = User(
        email=email,
        username=username,
        hashed_password=hashed_password,
        full_name=full_name,
        is_active=True,
        is_superuser=True,
        role="ADMINISTRADOR",
        company_id=company_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    from app.services.permission_service import seed_permissions, assign_role_permissions
    seed_permissions(db)
    assign_role_permissions(db, user)
    db.commit()

    print("✅ Usuario admin creado exitosamente:")
    print(f"   ID:        {user.id}")
    print(f"   Email:     {user.email}")
    print(f"   Username:  {user.username}")
    print(f"   Nombre:    {user.full_name}")
    print(f"   Role:      {user.role}")
    print(f"   Activo:    {user.is_active}")
    print(f"   Superuser: {user.is_superuser}")
    print(f"   Company:   {user.company_id or 'Sin empresa'}")
    return user


def test_login(db, username, password):
    from app.core.security import verify_password
    from app.models.sql.user import User

    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"ERROR: No se encontró usuario {username}")
        return False

    if verify_password(password, user.hashed_password):
        print("✅ Login verificado correctamente")
        return True
    else:
        print("ERROR: La contraseña no coincide")
        return False


def main():
    parser = argparse.ArgumentParser(description="Crear usuario administrador")
    parser.add_argument("--email", default="admin@reloadmatrix.com")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="Admin@123456")
    parser.add_argument("--full-name", default="Administrador Sistema")
    parser.add_argument("--company-id", type=int, default=None)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--reset", action="store_true", help="Actualizar contraseña si el usuario ya existe")

    args = parser.parse_args()
    db = get_db_session()

    try:
        user = create_admin_user(
            db=db,
            email=args.email,
            username=args.username,
            password=args.password,
            full_name=args.full_name,
            company_id=args.company_id,
            reset=args.reset,
        )
        if user and args.verify:
            test_login(db, args.username, args.password)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
