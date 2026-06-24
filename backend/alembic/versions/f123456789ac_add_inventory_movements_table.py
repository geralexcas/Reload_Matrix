"""add inventory_movements table

Revision ID: f123456789ac
Revises: e2f3a4b5c6d7
Create Date: 2026-06-23 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "f123456789ac"
down_revision: Union[str, None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Verificar si la tabla ya existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'inventory_movements' not in inspector.get_table_names():
        op.create_table(
            "inventory_movements",
            sa.Column("id", sa.Integer(), primary_key=True, index=True),
            sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
            sa.Column("company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False),
            sa.Column(
                "movement_type",
                sa.Enum("ADD", "DEDUCT", "ADJUST", name="inventory_movement_type"),
                nullable=False,
            ),
            sa.Column("quantity", sa.Numeric(15, 2), nullable=False),
            sa.Column("reference", sa.String(length=255), nullable=True),
            sa.Column("reference_id", sa.Integer(), nullable=True),
            sa.Column("reference_type", sa.String(length=50), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )
        op.create_index(
            op.f('ix_inventory_movements_id'), 
            'inventory_movements', 
            ['id'], 
            unique=False
        )


def downgrade() -> None:
    # Verificar si el índice existe antes de eliminarlo
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    
    if 'inventory_movements' in inspector.get_table_names():
        indexes = [idx['name'] for idx in inspector.get_indexes('inventory_movements')]
        if 'ix_inventory_movements_id' in indexes:
            op.drop_index(
                op.f('ix_inventory_movements_id'), 
                table_name='inventory_movements'
            )
        op.drop_table('inventory_movements')
