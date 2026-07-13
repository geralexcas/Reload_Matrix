#!/usr/bin/env python3
"""
Script para crear 3 productos de prueba:
- 2 con proveedor (supplier_id asignado)
- 1 sin proveedor (supplier_id = NULL)

Uso:
    docker compose exec backend python scripts/create_test_products.py
"""

import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_dir)


def get_db_session():
    from app.core.database import SessionLocal, engine, Base
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def create_test_products():
    from app.models.sql.partners import Partner
    from app.models.sql.inventory import Product

    db = get_db_session()
    try:
        company_id = 1
        # ponytail: set tenant ContextVar so the before_cursor_execute event
        # applies app.tenant_id and RLS allows the INSERTs (PG only; SQLite no-op).
        from app.core.tenant_context import current_tenant_id
        current_tenant_id.set(company_id)

        # --- Crear 2 proveedores de prueba si no existen ---
        suppliers_data = [
            {"nit": "900123456", "name": "Proveedor A", "partner_type": "SUPPLIER"},
            {"nit": "900789012", "name": "Proveedor B", "partner_type": "SUPPLIER"},
        ]
        suppliers = []
        for sdata in suppliers_data:
            partner = (
                db.query(Partner)
                .filter(Partner.nit == sdata["nit"], Partner.company_id == company_id)
                .first()
            )
            if not partner:
                partner = Partner(
                    nit=sdata["nit"],
                    name=sdata["name"],
                    partner_type=sdata["partner_type"],
                    company_id=company_id,
                    is_active=True,
                )
                db.add(partner)
                db.flush()
            suppliers.append(partner)

        # --- Crear 3 productos ---
        products_data = [
            {
                "sku": "TEST001",
                "barcode": "7701001000011",
                "name": "Teclado Mecánico RGB",
                "description": "Teclado mecánico retroiluminado RGB, switches Cherry MX",
                "category": "PERIFERICOS",
                "brand": "TechBrand",
                "purchase_price": 85000,
                "sale_price": 145000,
                "stock_level": 50,
                "min_stock_level": 5,
                "max_stock_level": 200,
                "company_id": company_id,
                "supplier_id": suppliers[0].id,
            },
            {
                "sku": "TEST002",
                "barcode": "7701001000028",
                "name": "Mouse Inalámbrico",
                "description": "Mouse ergonómico inalámbrico con sensor óptico de 4000 DPI",
                "category": "PERIFERICOS",
                "brand": "TechBrand",
                "purchase_price": 45000,
                "sale_price": 78000,
                "stock_level": 30,
                "min_stock_level": 5,
                "max_stock_level": 150,
                "company_id": company_id,
                "supplier_id": suppliers[1].id,
            },
            {
                "sku": "TEST003",
                "barcode": "7701001000035",
                "name": "Cable USB-C 2m",
                "description": "Cable USB-C a USB-C de 2 metros, carga rápida",
                "category": "ACCESORIOS",
                "brand": None,
                "purchase_price": 12000,
                "sale_price": 25000,
                "stock_level": 100,
                "min_stock_level": 10,
                "max_stock_level": 500,
                "company_id": company_id,
                "supplier_id": None,  # Sin proveedor
            },
        ]

        created = 0
        for pdata in products_data:
            exists = (
                db.query(Product)
                .filter(Product.sku == pdata["sku"], Product.company_id == company_id)
                .first()
            )
            if exists:
                print(f"  → Ya existe: {pdata['sku']} - {pdata['name']}")
                continue

            product = Product(**pdata)
            db.add(product)
            created += 1

        db.commit()
        print(f"✅ {created} producto(s) creado(s) exitosamente.")
        print()

        # Mostrar resumen
        print("Productos en BD:")
        productos = (
            db.query(Product)
            .filter(Product.company_id == company_id)
            .order_by(Product.sku)
            .all()
        )
        for p in productos:
            prov = f"Proveedor: {p.supplier.name}" if p.supplier else "Sin proveedor"
            print(f"  [{p.sku}] {p.name} — ${p.sale_price:,.0f} — {prov}")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    create_test_products()
