"""add_cost_to_account_types_enum

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-06-01 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e2f3a4b5c6d7'
down_revision: Union[str, None] = 'd1e2f3a4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE account_types ADD VALUE IF NOT EXISTS 'COST'")


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "UPDATE chart_of_accounts SET account_type = 'EXPENSE' WHERE account_type = 'COST'"
    ))
    conn.execute(sa.text("COMMIT"))
    op.execute(
        "ALTER TYPE account_types RENAME TO account_types_old"
    )
    op.execute(
        "CREATE TYPE account_types AS ENUM ('ASSET', 'LIABILITY', 'EQUITY', 'REVENUE', 'EXPENSE')"
    )
    op.execute(
        "ALTER TABLE chart_of_accounts ALTER COLUMN account_type TYPE account_types "
        "USING account_type::text::account_types"
    )
    op.execute("DROP TYPE account_types_old")
