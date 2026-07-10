"""prevent_direct_invoice_delete_trigger

Revision ID: a4b5c6d7e8f9
Revises: f123456789ac
Create Date: 2026-07-10 00:00:00.000000

Crea un trigger BEFORE DELETE en la tabla invoices que impide el borrado
directo de facturas por SQL o script, forzando el uso del flujo de
cancelacion (status=CANCELLED). Los asientos contables quedan como
huérfanos cuando se borra una factura por fuera del service layer, y este
trigger lo previene a nivel de base de datos.

Para override deliberado (casos excepcionales de admin):
  SET session_replication_role = 'replica';
  DELETE FROM invoices WHERE id = X;
  SET session_replication_role = 'origin';
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a4b5c6d7e8f9'
down_revision: Union[str, None] = 'f123456789ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION prevent_invoice_delete()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'DELETE directo en invoices prohibido. Use cancel_invoice (status=CANCELLED). Override: SET session_replication_role = replica';
        END;
        $$ LANGUAGE plpgsql
    """))
    op.execute(sa.text("""
        CREATE TRIGGER trg_prevent_invoice_delete
        BEFORE DELETE ON invoices
        FOR EACH ROW
        EXECUTE FUNCTION prevent_invoice_delete()
    """))


def downgrade() -> None:
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_prevent_invoice_delete ON invoices"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS prevent_invoice_delete()"))