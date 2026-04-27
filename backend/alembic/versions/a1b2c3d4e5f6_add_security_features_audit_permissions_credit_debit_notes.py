"""add security features audit permissions credit debit notes

Revision ID: a1b2c3d4e5f6
Revises: 6f3ede781b9a
Create Date: 2026-04-01 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "6f3ede781b9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add hashed_refresh_token to users
    op.add_column("users", sa.Column("hashed_refresh_token", sa.Text(), nullable=True))

    # 2. Create permissions table
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("module", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
    )

    # 3. Create audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=True
        ),
        sa.Column(
            "action",
            sa.Enum(
                "CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", name="audit_actions"
            ),
            nullable=False,
        ),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("old_values", sa.Text(), nullable=True),
        sa.Column("new_values", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now()
        ),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_company_id", "audit_logs", ["company_id"])

    # 4. Create credit_debit_notes table
    op.create_table(
        "credit_debit_notes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column(
            "company_id", sa.Integer(), sa.ForeignKey("companies.id"), nullable=False
        ),
        sa.Column(
            "original_invoice_id",
            sa.Integer(),
            sa.ForeignKey("invoices.id"),
            nullable=False,
        ),
        sa.Column(
            "note_type", sa.Enum("CREDIT", "DEBIT", name="note_types"), nullable=False
        ),
        sa.Column("reason", sa.String(500), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("note_number", sa.String(50), nullable=False, unique=True),
        sa.Column("cufe", sa.String(128), nullable=True),
        sa.Column("xml_ubl", sa.Text(), nullable=True),
        sa.Column(
            "estado_dian",
            sa.Enum(
                "BORRADOR", "ENVIADO", "ACEPTADO", "RECHAZADO", name="note_dian_status"
            ),
            server_default="BORRADOR",
        ),
        sa.Column("fecha_envio_dian", sa.DateTime(timezone=True), nullable=True),
        sa.Column("motivo_rechazo", sa.Text(), nullable=True),
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
        "ix_credit_debit_notes_company_id", "credit_debit_notes", ["company_id"]
    )
    op.create_index(
        "ix_credit_debit_notes_original_invoice_id",
        "credit_debit_notes",
        ["original_invoice_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_credit_debit_notes_original_invoice_id", table_name="credit_debit_notes"
    )
    op.drop_index("ix_credit_debit_notes_company_id", table_name="credit_debit_notes")
    op.drop_table("credit_debit_notes")
    op.drop_index("ix_audit_logs_company_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_table("permissions")
    op.drop_column("users", "hashed_refresh_token")
