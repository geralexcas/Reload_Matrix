"""add treasury module bank accounts cash accounts reconciliation

Revision ID: c4d5e6f7a8b9
Revises: b7c8d9e0f1a2
Create Date: 2026-04-03 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4d5e6f7a8b9"
down_revision: Union[str, None] = "b7c8d9e0f1a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enums are created by SQLAlchemy automatically because they have values

    # bank_accounts
    op.create_table(
        "bank_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("bank_name", sa.String(255), nullable=False),
        sa.Column("account_number", sa.String(50), nullable=False),
        sa.Column(
            "account_type",
            sa.Enum("CHECKING", "SAVINGS", "TIME_DEPOSIT", name="bank_account_types"),
            nullable=False,
            server_default="CHECKING",
        ),
        sa.Column("currency", sa.String(3), server_default="COP"),
        sa.Column("initial_balance", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("current_balance", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("branch_office", sa.String(255), nullable=True),
        sa.Column("swift_code", sa.String(20), nullable=True),
        sa.Column("routing_number", sa.String(20), nullable=True),
        sa.Column(
            "linked_account_id",
            sa.Integer(),
            sa.ForeignKey("chart_of_accounts.id"),
            nullable=True,
        ),
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
    op.create_index("ix_bank_accounts_company_id", "bank_accounts", ["company_id"])

    # cash_accounts
    op.create_table(
        "cash_accounts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "account_type",
            sa.Enum("MAIN_CASH", "PETTY_CASH", "REGISTER_CASH", name="cash_account_types"),
            nullable=False,
            server_default="MAIN_CASH",
        ),
        sa.Column("currency", sa.String(3), server_default="COP"),
        sa.Column("initial_balance", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("current_balance", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column(
            "responsible_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
        sa.Column("max_petty_cash_amount", sa.Numeric(15, 2), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column(
            "linked_account_id",
            sa.Integer(),
            sa.ForeignKey("chart_of_accounts.id"),
            nullable=True,
        ),
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
    op.create_index("ix_cash_accounts_company_id", "cash_accounts", ["company_id"])

    # treasury_transactions
    op.create_table(
        "treasury_transactions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column(
            "account_type", sa.Enum("BANK", "CASH", name="treasury_account_types"), nullable=False
        ),
        sa.Column(
            "bank_account_id",
            sa.Integer(),
            sa.ForeignKey("bank_accounts.id"),
            nullable=True,
        ),
        sa.Column(
            "cash_account_id",
            sa.Integer(),
            sa.ForeignKey("cash_accounts.id"),
            nullable=True,
        ),
        sa.Column(
            "transaction_type", sa.Enum("DEPOSIT", "WITHDRAWAL", "TRANSFER_IN", "TRANSFER_OUT", "FEE", "INTEREST", "CHECK_ISSUED", "CHECK_CLEARED", "CHECK_BOUNCED", name="treasury_tx_types"), nullable=False
        ),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="COP"),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("reference", sa.String(100), nullable=True),
        sa.Column("reference_type", sa.String(50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column(
            "journal_entry_id",
            sa.Integer(),
            sa.ForeignKey("journal_entries.id"),
            nullable=True,
        ),
        sa.Column("balance_after", sa.Numeric(15, 2), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_treasury_transactions_company_id", "treasury_transactions", ["company_id"]
    )

    # check_register
    op.create_table(
        "check_register",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column(
            "bank_account_id",
            sa.Integer(),
            sa.ForeignKey("bank_accounts.id"),
            nullable=False,
        ),
        sa.Column("check_number", sa.String(30), nullable=False),
        sa.Column("payee", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("issue_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ISSUED", "DELIVERED", "CLEARED", "BOUNCED", "VOIDED", name="check_status"),
            nullable=False,
            server_default="ISSUED",
        ),
        sa.Column("cleared_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "linked_transaction_id",
            sa.Integer(),
            sa.ForeignKey("treasury_transactions.id"),
            nullable=True,
        ),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("ix_check_register_company_id", "check_register", ["company_id"])

    # bank_reconciliations
    op.create_table(
        "bank_reconciliations",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column(
            "bank_account_id",
            sa.Integer(),
            sa.ForeignKey("bank_accounts.id"),
            nullable=False,
        ),
        sa.Column("statement_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("statement_balance", sa.Numeric(15, 2), nullable=False),
        sa.Column("system_balance", sa.Numeric(15, 2), nullable=False),
        sa.Column("outstanding_deposits", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("outstanding_checks", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("bank_fees_not_recorded", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("interest_not_recorded", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("adjusted_balance", sa.Numeric(15, 2), nullable=True),
        sa.Column("is_balanced", sa.Boolean(), server_default="false"),
        sa.Column(
            "status",
            sa.Enum("IN_PROGRESS", "COMPLETED", name="reconciliation_status"),
            nullable=False,
            server_default="IN_PROGRESS",
        ),
        sa.Column(
            "reconciled_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True
        ),
        sa.Column("reconciled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.String(1000), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_bank_reconciliations_company_id", "bank_reconciliations", ["company_id"]
    )

    # reconciliation_lines
    op.create_table(
        "reconciliation_lines",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "reconciliation_id",
            sa.Integer(),
            sa.ForeignKey("bank_reconciliations.id"),
            nullable=False,
        ),
        sa.Column(
            "treasury_transaction_id",
            sa.Integer(),
            sa.ForeignKey("treasury_transactions.id"),
            nullable=True,
        ),
        sa.Column("is_matched", sa.Boolean(), server_default="false"),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        sa.Column("statement_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("system_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("difference", sa.Numeric(15, 2), server_default="0.00"),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("reconciliation_lines")
    op.drop_table("bank_reconciliations")
    op.drop_table("check_register")
    op.drop_table("treasury_transactions")
    op.drop_table("cash_accounts")
    op.drop_table("bank_accounts")
    op.execute("DROP TYPE reconciliation_status")
    op.execute("DROP TYPE check_status")
    op.execute("DROP TYPE treasury_tx_types")
    op.execute("DROP TYPE treasury_account_types")
    op.execute("DROP TYPE cash_account_types")
    op.execute("DROP TYPE bank_account_types")
