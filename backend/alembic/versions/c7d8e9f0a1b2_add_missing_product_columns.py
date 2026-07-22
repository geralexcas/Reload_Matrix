"""add missing product columns

Revision ID: c7d8e9f0a1b2
Revises: 9a8b7c6d5e4f
Create Date: 2026-07-22 10:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c7d8e9f0a1b2"
down_revision: Union[str, None] = "9a8b7c6d5e4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c["name"] for c in inspector.get_columns("products")}

    if "brand" not in existing_cols:
        op.add_column("products", sa.Column("brand", sa.String(100), nullable=True))
    if "model" not in existing_cols:
        op.add_column("products", sa.Column("model", sa.String(100), nullable=True))
    if "payment_method" not in existing_cols:
        op.add_column(
            "products",
            sa.Column("payment_method", sa.String(50), server_default="CASH"),
        )
    if "supplier_id" not in existing_cols:
        op.add_column(
            "products",
            sa.Column(
                "supplier_id",
                sa.Integer(),
                sa.ForeignKey("partners.id"),
                nullable=True,
            ),
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c["name"] for c in inspector.get_columns("products")}

    if "supplier_id" in existing_cols:
        op.drop_constraint("products_supplier_id_fkey", "products", type_="foreignkey")
        op.drop_column("products", "supplier_id")
    if "payment_method" in existing_cols:
        op.drop_column("products", "payment_method")
    if "model" in existing_cols:
        op.drop_column("products", "model")
    if "brand" in existing_cols:
        op.drop_column("products", "brand")
