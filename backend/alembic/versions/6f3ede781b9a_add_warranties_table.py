"""add_warranties_table

Revision ID: 6f3ede781b9a
Revises: 97d8928869d4
Create Date: 2026-03-31 17:49:36.184706

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6f3ede781b9a"
down_revision: Union[str, None] = "97d8928869d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "warranties",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "repair_order_id",
            sa.Integer(),
            sa.ForeignKey("repair_orders.id"),
            nullable=False,
        ),
        sa.Column(
            "repair_item_id",
            sa.Integer(),
            sa.ForeignKey("repair_items.id"),
            nullable=True,
        ),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column(
            "warranty_type",
            sa.Enum("MANUFACTURER", "SERVICE", "PARTS", name="warranty_types"),
            nullable=False,
            server_default="SERVICE",
        ),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "EXPIRED", "VOID", "CLAIMED", name="warranty_statuses"),
            server_default="ACTIVE",
        ),
        sa.Column("description", sa.String(1000), nullable=True),
        sa.Column("terms_and_conditions", sa.Text(), nullable=True),
        sa.Column("claim_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("claim_description", sa.String(1000), nullable=True),
        sa.Column("claim_resolution", sa.String(1000), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    pass


def downgrade() -> None:
    op.drop_index(op.f("ix_warranties_id"), table_name="warranties")
    op.drop_table("warranties")
    op.execute("DROP TYPE warranty_types")
    op.execute("DROP TYPE warranty_statuses")
