"""add_serial_number_to_invoice_items

Revision ID: d1e2f3a4b5c6
Revises: 782f9987ccc4
Create Date: 2026-05-26 18:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, None] = '782f9987ccc4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Verificamos si la columna ya existe antes de intentar crearla (para evitar errores en produccion)
    conn = op.get_bind()
    res = conn.execute(sa.text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='invoice_items' AND column_name='serial_number'"
    ))
    if not res.first():
        op.add_column('invoice_items', sa.Column('serial_number', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('invoice_items', 'serial_number')
