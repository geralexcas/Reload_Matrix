"""enable_row_level_security_tenant_isolation

Revision ID: 9f8e7d6c5b4a
Revises: fb0405b8d677
Create Date: 2026-07-13 00:00:00.000000

Habilita Row-Level Security (RLS) en las tablas tenant-scoped como red de
seguridad debajo del filtro ORM (app/core/tenant_context.py).  Si una query
bypassa el ORM (raw SQL, bulk Query.update/delete, o un modelo nuevo sin
company_id), RLS la filtra igual.

Politica deny-by-default: una fila es visible solo si
  company_id::text = current_setting('app.tenant_id', true)
Cuando app.tenant_id no esta seteado (NULL) → ninguna fila coincide → deny.
La app setea app.tenant_id por request en get_current_user / verify_company_membership
(ver app/core/tenant_context.set_db_tenant_id).

FORCE RLS: el rol de la app (user) tambien es dueno de las tablas, asi que
sin FORCE el dueno bypassearia RLS.  FORCE lo aplica tambien al dueno.

Tablas SIN RLS (aisladas por capa de app, no por RLS):
  - users        (resuelto antes de tener contexto de tenant; en _EXCLUDE_FROM_AUTO_FILTER)
  - companies    (registro de tenants; no tiene company_id)
  - audit_logs   (nullable company_id; admin-only; en _EXCLUDE_FROM_AUTO_FILTER)
  - permissions  (RBAC global; sin company_id)
  - tablas hijas sin company_id (invoice_items, wallet_transactions, repair_items,
    purchase_items, purchase_payments, reconciliation_lines, journal_entry_lines):
    se protegen via FK al padre (que SI tiene RLS) + ban de raw SQL en CI.

Override para scripts de seed/admin (rara vez, fuera del request):
  SET session_replication_role = 'replica';   -- bypassa RLS y triggers
  -- ... inserts ...
  SET session_replication_role = 'origin';
O mejor: usar app.core.tenant_context.set_db_tenant_id(db, company_id) al inicio.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9f8e7d6c5b4a'
down_revision: Union[str, None] = 'fb0405b8d677'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Tablas tenant-scoped con company_id (no incluye users/companies/audit_logs/permissions).
_TENANT_TABLES = [
    "products",
    "product_price_history",
    "inventory_movements",
    "partners",
    "fiscal_periods",
    "invoices",
    "invoice_resolutions",
    "credit_debit_notes",
    "wallets",
    "dian_billing_ranges",
    "repair_orders",
    "warranties",
    "technicians",
    "purchases",
    "chart_of_accounts",
    "journal_entries",
    "treasury_transactions",
    "cash_accounts",
    "bank_accounts",
    "bank_reconciliations",
    "check_register",
]


def upgrade() -> None:
    for table in _TENANT_TABLES:
        op.execute(sa.text(
            f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY"
        ))
        op.execute(sa.text(
            f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY"
        ))
        op.execute(sa.text(
            f"CREATE POLICY tenant_isolation ON {table} "
            f"USING (company_id::text = current_setting('app.tenant_id', true))"
        ))


def downgrade() -> None:
    for table in _TENANT_TABLES:
        op.execute(sa.text(f"DROP POLICY IF EXISTS tenant_isolation ON {table}"))
        op.execute(sa.text(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY"))
        op.execute(sa.text(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY"))
