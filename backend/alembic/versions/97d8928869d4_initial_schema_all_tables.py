"""initial_schema_all_tables

Revision ID: 97d8928869d4
Revises:
Create Date: 2026-03-31 16:32:57.542809

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "97d8928869d4"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("nit", sa.String(length=20), nullable=False),
        sa.Column("dv", sa.String(length=1), nullable=False),
        sa.Column("legal_representative", sa.String(length=255), nullable=False),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=500), nullable=True),
        sa.Column(
            "regimen",
            sa.Enum("COMUN", "SIMPLE", "ESPECIAL", "NO_RESPONSABLE", name="regimen_types"),
            nullable=True,
        ),
        sa.Column("fecha_inicio_actividades", sa.Date(), nullable=False),
        sa.Column("resolucion_facturacion", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=False)
    op.create_index(op.f("ix_companies_nit"), "companies", ["nit"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            sa.Enum(
                "ADMINISTRADOR",
                "CONTADOR",
                "TECNICO",
                "VENDEDOR",
                "BODEGUERO",
                name="user_roles",
            ),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_superuser", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "chart_of_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "account_type",
            sa.Enum(
                "ASSET",
                "LIABILITY",
                "EQUITY",
                "REVENUE",
                "EXPENSE",
                name="account_types",
            ),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["chart_of_accounts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_chart_of_accounts_code"), "chart_of_accounts", ["code"], unique=True
    )
    op.create_index(
        op.f("ix_chart_of_accounts_id"), "chart_of_accounts", ["id"], unique=False
    )

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "entry_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("is_posted", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_journal_entries_id"), "journal_entries", ["id"], unique=False
    )

    op.create_table(
        "journal_entry_lines",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("journal_entry_id", sa.Integer(), nullable=True),
        sa.Column("account_id", sa.Integer(), nullable=True),
        sa.Column("debit_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("credit_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["chart_of_accounts.id"],
        ),
        sa.ForeignKeyConstraint(
            ["journal_entry_id"],
            ["journal_entries.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_journal_entry_lines_id"), "journal_entry_lines", ["id"], unique=False
    )

    op.create_table(
        "partners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nit", sa.String(length=20), nullable=False),
        sa.Column("dv", sa.String(length=1), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "partner_type",
            sa.Enum("SUPPLIER", "CUSTOMER", "BOTH", name="partner_types"),
            nullable=False,
        ),
        sa.Column(
            "responsibility_fiscal",
            sa.Enum(
                "RESPONSABLE IVA",
                "NO RESPONSABLE",
                "AGENTE RETENEDOR",
                name="responsibility_fiscal_types",
            ),
            nullable=False,
        ),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("contact_person", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_partners_id"), "partners", ["id"], unique=False)
    op.create_index(op.f("ix_partners_nit"), "partners", ["nit"], unique=True)

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=50), nullable=False),
        sa.Column("barcode", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("unit_of_measure", sa.String(length=50), nullable=True),
        sa.Column("purchase_price", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("sale_price", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("stock_level", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("min_stock_level", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("max_stock_level", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_barcode"), "products", ["barcode"], unique=True)
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
    op.create_index(op.f("ix_products_sku"), "products", ["sku"], unique=True)

    op.create_table(
        "technicians",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.String(length=50), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("specialty", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_technicians_employee_id"), "technicians", ["employee_id"], unique=True
    )
    op.create_index(op.f("ix_technicians_id"), "technicians", ["id"], unique=False)

    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invoice_number", sa.String(length=50), nullable=False),
        sa.Column(
            "invoice_type",
            sa.Enum("SALE", "PURCHASE", "CUENTA_COBRO", name="invoice_types"),
            nullable=False,
        ),
        sa.Column("partner_id", sa.Integer(), nullable=True),
        sa.Column(
            "issue_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "ISSUED", "PAID", "CANCELLED", name="invoice_status"),
            nullable=True,
        ),
        sa.Column("cufe", sa.String(length=100), nullable=True),
        sa.Column("xml_ubl", sa.String(), nullable=True),
        sa.Column(
            "estado_dian",
            sa.Enum(
                "BORRADOR",
                "ENVIADO",
                "ACEPTADO",
                "RECHAZADO",
                "NO_APLICA",
                name="invoice_dian_state",
            ),
            nullable=True,
        ),
        sa.Column("motivo_rechazo", sa.String(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["partner_id"],
            ["partners.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoices_cufe"), "invoices", ["cufe"], unique=True)
    op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)
    op.create_index(
        op.f("ix_invoices_invoice_number"), "invoices", ["invoice_number"], unique=True
    )

    op.create_table(
        "invoice_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("discount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("tax_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("line_total", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["invoices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_invoice_items_id"), "invoice_items", ["id"], unique=False)

    op.create_table(
        "wallets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("partner_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("balance", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["partner_id"],
            ["partners.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wallets_id"), "wallets", ["id"], unique=False)

    op.create_table(
        "wallet_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("wallet_id", sa.Integer(), nullable=True),
        sa.Column(
            "transaction_type",
            sa.Enum(
                "DEPOSIT",
                "WITHDRAWAL",
                "TRANSFER_IN",
                "TRANSFER_OUT",
                name="wallet_tx_types",
            ),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("reference_type", sa.String(length=50), nullable=True),
        sa.Column("reference_id", sa.Integer(), nullable=True),
        sa.Column("balance_after", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["wallet_id"],
            ["wallets.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_wallet_transactions_id"), "wallet_transactions", ["id"], unique=False
    )

    op.create_table(
        "repair_orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("partner_id", sa.Integer(), nullable=True),
        sa.Column("technician_id", sa.Integer(), nullable=True),
        sa.Column(
            "issue_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expected_delivery_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_delivery_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("problem_description", sa.String(length=1000), nullable=True),
        sa.Column("diagnosis", sa.String(length=1000), nullable=True),
        sa.Column("service_notes", sa.String(length=2000), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "RECEIVED",
                "DIAGNOSIS",
                "APPROVED",
                "IN_REPAIR",
                "WAITING_PARTS",
                "READY",
                "DELIVERED",
                "CANCELLED",
                name="repair_order_status",
            ),
            nullable=True,
        ),
        sa.Column("warranty_applied", sa.Boolean(), nullable=True),
        sa.Column("total_labor_cost", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("total_parts_cost", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("total_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.Column("cufe", sa.String(length=100), nullable=True),
        sa.Column("xml_ubl", sa.String(), nullable=True),
        sa.Column(
            "estado_dian",
            sa.Enum(
                "BORRADOR",
                "ENVIADO",
                "ACEPTADO",
                "RECHAZADO",
                "NO_APLICA",
                name="invoice_dian_state",
            ),
            nullable=True,
        ),
        sa.Column("motivo_rechazo", sa.String(), nullable=True),
        sa.Column("invoice_id", sa.Integer(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invoice_id"],
            ["invoices.id"],
        ),
        sa.ForeignKeyConstraint(
            ["partner_id"],
            ["partners.id"],
        ),
        sa.ForeignKeyConstraint(
            ["technician_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_repair_orders_cufe"), "repair_orders", ["cufe"], unique=True
    )
    op.create_index(op.f("ix_repair_orders_id"), "repair_orders", ["id"], unique=False)
    op.create_index(
        op.f("ix_repair_orders_order_number"),
        "repair_orders",
        ["order_number"],
        unique=True,
    )

    op.create_table(
        "repair_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("repair_order_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("serial_number", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("issue_reported", sa.String(length=500), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("unit_cost", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("discount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("tax_amount", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column("line_total", sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column(
            "warranty_status",
            sa.Enum(
                "NO_WARRANTY",
                "IN_WARRANTY",
                "WARRANTY_VOID",
                name="warranty_status_types",
            ),
            nullable=True,
        ),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["repair_order_id"],
            ["repair_orders.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_repair_items_id"), "repair_items", ["id"], unique=False)

    # 1. fiscal_periods
    op.create_table(
        "fiscal_periods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_fiscal_periods_id"), "fiscal_periods", ["id"], unique=False)
    op.create_index(op.f("ix_fiscal_periods_company_id"), "fiscal_periods", ["company_id"], unique=False)

    # 2. product_price_history
    op.create_table(
        "product_price_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("effective_date", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_price_history_id"), "product_price_history", ["id"], unique=False)
    op.create_index(op.f("ix_product_price_history_product_id"), "product_price_history", ["product_id"], unique=False)
    op.create_index(op.f("ix_product_price_history_company_id"), "product_price_history", ["company_id"], unique=False)

    # 3. purchases
    op.create_table(
        "purchases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purchase_number", sa.String(length=50), nullable=False),
        sa.Column("partner_id", sa.Integer(), nullable=False),
        sa.Column("purchase_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("subtotal", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(precision=15, scale=2), server_default="0.00"),
        sa.Column("total_amount", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0.00"),
        sa.Column("discount_amount", sa.Numeric(precision=15, scale=2), server_default="0.00"),
        sa.Column("currency", sa.String(length=3), server_default="COP"),
        sa.Column(
            "payment_method",
            sa.Enum("CASH", "BANK_TRANSFER", "CHECK", "CREDIT_CARD", "CREDIT", "PARTIAL_CREDIT", name="payment_methods"),
            nullable=False,
            server_default="CREDIT",
        ),
        sa.Column(
            "status",
            sa.Enum("DRAFT", "ISSUED", "PAID", "PARTIAL", "OVERDUE", "CANCELLED", name="purchase_status"),
            server_default="DRAFT",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"]),
        sa.ForeignKeyConstraint(["partner_id"], ["partners.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("purchase_number", "company_id", name="uq_purchase_number_company"),
    )
    op.create_index(op.f("ix_purchases_id"), "purchases", ["id"], unique=False)
    op.create_index(op.f("ix_purchases_purchase_number"), "purchases", ["purchase_number"], unique=False)

    # 4. purchase_items
    op.create_table(
        "purchase_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purchase_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("unit_price", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("serial_number", sa.String(length=255), nullable=True),
        sa.Column("discount_percent", sa.Numeric(precision=5, scale=2), server_default="0.00"),
        sa.Column("discount_amount", sa.Numeric(precision=15, scale=2), server_default="0.00"),
        sa.Column("tax_rate", sa.Numeric(precision=5, scale=2), server_default="0.00"),
        sa.Column("tax_amount", sa.Numeric(precision=15, scale=2), server_default="0.00"),
        sa.Column("line_total", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_purchase_items_id"), "purchase_items", ["id"], unique=False)

    # 5. purchase_payments
    op.create_table(
        "purchase_payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purchase_id", sa.Integer(), nullable=False),
        sa.Column(
            "payment_method",
            sa.Enum("CASH", "BANK_TRANSFER", "CHECK", "CREDIT_CARD", name="payment_methods"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("payment_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["purchase_id"], ["purchases.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_purchase_payments_id"), "purchase_payments", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_purchase_payments_id"), table_name="purchase_payments")
    op.drop_table("purchase_payments")
    op.drop_index(op.f("ix_purchase_items_id"), table_name="purchase_items")
    op.drop_table("purchase_items")
    op.drop_index(op.f("ix_purchases_purchase_number"), table_name="purchases")
    op.drop_index(op.f("ix_purchases_id"), table_name="purchases")
    op.drop_table("purchases")
    op.drop_index(op.f("ix_product_price_history_company_id"), table_name="product_price_history")
    op.drop_index(op.f("ix_product_price_history_product_id"), table_name="product_price_history")
    op.drop_index(op.f("ix_product_price_history_id"), table_name="product_price_history")
    op.drop_table("product_price_history")
    op.drop_index(op.f("ix_fiscal_periods_company_id"), table_name="fiscal_periods")
    op.drop_index(op.f("ix_fiscal_periods_id"), table_name="fiscal_periods")
    op.drop_table("fiscal_periods")
    op.drop_index(op.f("ix_repair_items_id"), table_name="repair_items")
    op.drop_table("repair_items")
    op.drop_index(op.f("ix_repair_orders_order_number"), table_name="repair_orders")
    op.drop_index(op.f("ix_repair_orders_id"), table_name="repair_orders")
    op.drop_index(op.f("ix_repair_orders_cufe"), table_name="repair_orders")
    op.drop_table("repair_orders")
    op.drop_index(op.f("ix_wallet_transactions_id"), table_name="wallet_transactions")
    op.drop_table("wallet_transactions")
    op.drop_index(op.f("ix_wallets_id"), table_name="wallets")
    op.drop_table("wallets")
    op.drop_index(op.f("ix_invoice_items_id"), table_name="invoice_items")
    op.drop_table("invoice_items")
    op.drop_index(op.f("ix_invoices_invoice_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_cufe"), table_name="invoices")
    op.drop_table("invoices")
    op.drop_index(op.f("ix_technicians_employee_id"), table_name="technicians")
    op.drop_index(op.f("ix_technicians_id"), table_name="technicians")
    op.drop_table("technicians")
    op.drop_index(op.f("ix_products_sku"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_index(op.f("ix_products_barcode"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_partners_nit"), table_name="partners")
    op.drop_index(op.f("ix_partners_id"), table_name="partners")
    op.drop_table("partners")
    op.drop_index(op.f("ix_journal_entry_lines_id"), table_name="journal_entry_lines")
    op.drop_table("journal_entry_lines")
    op.drop_index(op.f("ix_journal_entries_id"), table_name="journal_entries")
    op.drop_table("journal_entries")
    op.drop_index(op.f("ix_chart_of_accounts_code"), table_name="chart_of_accounts")
    op.drop_index(op.f("ix_chart_of_accounts_id"), table_name="chart_of_accounts")
    op.drop_table("chart_of_accounts")
    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")
    op.drop_index(op.f("ix_companies_nit"), table_name="companies")
    op.drop_index(op.f("ix_companies_id"), table_name="companies")
    op.drop_table("companies")
