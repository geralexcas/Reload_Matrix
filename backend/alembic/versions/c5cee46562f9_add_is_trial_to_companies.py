"""add_is_trial_to_companies

Revision ID: c5cee46562f9
Revises: 9f8e7d6c5b4a
Create Date: 2026-07-19 03:21:47.355337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5cee46562f9'
down_revision: Union[str, None] = '9f8e7d6c5b4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('companies', sa.Column('is_trial', sa.Boolean(), nullable=True))
    op.execute("UPDATE companies SET is_trial = false WHERE is_trial IS NULL")
    op.alter_column('companies', 'is_trial', nullable=False, server_default=sa.text('false'))


def downgrade() -> None:
    op.drop_column('companies', 'is_trial')
