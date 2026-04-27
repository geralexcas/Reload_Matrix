#!/usr/bin/env python3
"""
Script para crear usuario administrador en reload_Matrix.

Uso:
  # Con PostgreSQL (desde host, requiere Docker levantado):
  cd /home/geralexcas/reload_Matrix
  docker compose up -d db
  cd backend && python scripts/create_admin.py

  # Con SQLite (desarrollo local sin Docker):
  cd backend && python scripts/create_admin.py --sqlite

  # Con parámetros personalizados:
  python scripts/create_admin.py --email admin@empresa.com --username admin --password "Admin@123456"

  # Asociar a una empresa:
  python scripts/create_admin.py --company-id 1
"""

import sys
import os
import argparse

# Agregar el directorio backend al path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)


def get_db_session(use_sqlite=False):
    """Obtener sesión de base de datos (SQLite o PostgreSQL)"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base

    if use_sqlite:
        sqlite_path = os.path.join(backend_dir, "business.db")
        engine = create_engine(
            f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL desde host
        db_url = os.getenv(
            "DATABASE_URL", "postgresql://user:password@localhost:5434/business_db"
        )
        # Reemplazar hostname Docker por localhost
        db_url = db_url.replace("@db:", "@localhost:")
        db_url = db_url.replace(":5432", ":5434")
        engine = create_engine(db_url)

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def create_admin_user(db, email, username, password, full_name, company_id=None):
    from app.core.security import get_password_hash, validate_password_strength
    from app.models.sql.user import User

    is_valid, message = validate_password_strength(password)
    if not is_valid:
        print(f"ERROR: {message}")
        return None

    existing = (
        db.query(User)
        .filter((User.email == email) | (User.username == username))
        .first()
    )
    if existing:
        print(
            f"ERROR: Usuario ya existe (id={existing.id}, username={existing.username})"
        )
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
    parser.add_argument("--sqlite", action="store_true")
    parser.add_argument("--verify", action="store_true")

    args = parser.parse_args()
    db = get_db_session(use_sqlite=args.sqlite)

    try:
        user = create_admin_user(
            db=db,
            email=args.email,
            username=args.username,
            password=args.password,
            full_name=args.full_name,
            company_id=args.company_id,
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
