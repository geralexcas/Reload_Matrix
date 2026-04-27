"""add backlog features credit limit dian ranges uvt

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-04-01 18:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add credit_limit to partners
    op.add_column("partners", sa.Column("credit_limit", sa.Float(), nullable=True))

    # 2. Create dian_billing_ranges table
    op.create_table(
        "dian_billing_ranges",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column("resolution", sa.String(100), nullable=False),
        sa.Column("prefix", sa.String(10), nullable=False),
        sa.Column("from_number", sa.Integer(), nullable=False),
        sa.Column("to_number", sa.Integer(), nullable=False),
        sa.Column("next_number", sa.Integer(), nullable=False),
        sa.Column("approval_date", sa.Date(), nullable=False),
        sa.Column("expiration_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
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
    op.create_index(
        "ix_dian_billing_ranges_company_id", "dian_billing_ranges", ["company_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_dian_billing_ranges_company_id", table_name="dian_billing_ranges")
    op.drop_table("dian_billing_ranges")
    op.drop_column("partners", "credit_limit")
