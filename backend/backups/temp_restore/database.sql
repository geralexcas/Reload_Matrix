--
-- PostgreSQL database dump
--

\restrict FA2Wj0urvbWfyB8oAA1Fe3e8CiPAaGcl8XD6nphPzV8b8LiWuU49QDtqSAo6pRN

-- Dumped from database version 15.17 (Debian 15.17-1.pgdg13+1)
-- Dumped by pg_dump version 17.10 (Debian 17.10-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.warranties DROP CONSTRAINT IF EXISTS warranties_repair_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public.warranties DROP CONSTRAINT IF EXISTS warranties_repair_item_id_fkey;
ALTER TABLE IF EXISTS ONLY public.warranties DROP CONSTRAINT IF EXISTS warranties_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.wallets DROP CONSTRAINT IF EXISTS wallets_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.wallets DROP CONSTRAINT IF EXISTS wallets_partner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.wallets DROP CONSTRAINT IF EXISTS wallets_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.wallet_transactions DROP CONSTRAINT IF EXISTS wallet_transactions_wallet_id_fkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_permissions DROP CONSTRAINT IF EXISTS user_permissions_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.user_permissions DROP CONSTRAINT IF EXISTS user_permissions_permission_id_fkey;
ALTER TABLE IF EXISTS ONLY public.treasury_transactions DROP CONSTRAINT IF EXISTS treasury_transactions_journal_entry_id_fkey;
ALTER TABLE IF EXISTS ONLY public.treasury_transactions DROP CONSTRAINT IF EXISTS treasury_transactions_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.treasury_transactions DROP CONSTRAINT IF EXISTS treasury_transactions_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.treasury_transactions DROP CONSTRAINT IF EXISTS treasury_transactions_cash_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.treasury_transactions DROP CONSTRAINT IF EXISTS treasury_transactions_bank_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.technicians DROP CONSTRAINT IF EXISTS technicians_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.repair_orders DROP CONSTRAINT IF EXISTS repair_orders_technician_id_fkey;
ALTER TABLE IF EXISTS ONLY public.repair_orders DROP CONSTRAINT IF EXISTS repair_orders_partner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.repair_orders DROP CONSTRAINT IF EXISTS repair_orders_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.repair_orders DROP CONSTRAINT IF EXISTS repair_orders_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.repair_items DROP CONSTRAINT IF EXISTS repair_items_repair_order_id_fkey;
ALTER TABLE IF EXISTS ONLY public.repair_items DROP CONSTRAINT IF EXISTS repair_items_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reconciliation_lines DROP CONSTRAINT IF EXISTS reconciliation_lines_treasury_transaction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.reconciliation_lines DROP CONSTRAINT IF EXISTS reconciliation_lines_reconciliation_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchases DROP CONSTRAINT IF EXISTS purchases_partner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchases DROP CONSTRAINT IF EXISTS purchases_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.purchases DROP CONSTRAINT IF EXISTS purchases_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_payments DROP CONSTRAINT IF EXISTS purchase_payments_purchase_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_payments DROP CONSTRAINT IF EXISTS purchase_payments_created_by_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_items DROP CONSTRAINT IF EXISTS purchase_items_purchase_id_fkey;
ALTER TABLE IF EXISTS ONLY public.purchase_items DROP CONSTRAINT IF EXISTS purchase_items_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_supplier_id_fkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.product_price_history DROP CONSTRAINT IF EXISTS product_price_history_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.product_price_history DROP CONSTRAINT IF EXISTS product_price_history_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.partners DROP CONSTRAINT IF EXISTS partners_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.journal_entry_lines DROP CONSTRAINT IF EXISTS journal_entry_lines_journal_entry_id_fkey;
ALTER TABLE IF EXISTS ONLY public.journal_entry_lines DROP CONSTRAINT IF EXISTS journal_entry_lines_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.journal_entries DROP CONSTRAINT IF EXISTS journal_entries_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_partner_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_resolutions DROP CONSTRAINT IF EXISTS invoice_resolutions_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.inventory_movements DROP CONSTRAINT IF EXISTS inventory_movements_product_id_fkey;
ALTER TABLE IF EXISTS ONLY public.inventory_movements DROP CONSTRAINT IF EXISTS inventory_movements_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.fiscal_periods DROP CONSTRAINT IF EXISTS fiscal_periods_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.dian_billing_ranges DROP CONSTRAINT IF EXISTS dian_billing_ranges_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.credit_debit_notes DROP CONSTRAINT IF EXISTS credit_debit_notes_original_invoice_id_fkey;
ALTER TABLE IF EXISTS ONLY public.credit_debit_notes DROP CONSTRAINT IF EXISTS credit_debit_notes_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.check_register DROP CONSTRAINT IF EXISTS check_register_linked_transaction_id_fkey;
ALTER TABLE IF EXISTS ONLY public.check_register DROP CONSTRAINT IF EXISTS check_register_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.check_register DROP CONSTRAINT IF EXISTS check_register_bank_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.chart_of_accounts DROP CONSTRAINT IF EXISTS chart_of_accounts_parent_id_fkey;
ALTER TABLE IF EXISTS ONLY public.chart_of_accounts DROP CONSTRAINT IF EXISTS chart_of_accounts_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cash_accounts DROP CONSTRAINT IF EXISTS cash_accounts_responsible_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cash_accounts DROP CONSTRAINT IF EXISTS cash_accounts_linked_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.cash_accounts DROP CONSTRAINT IF EXISTS cash_accounts_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_reconciliations DROP CONSTRAINT IF EXISTS bank_reconciliations_reconciled_by_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_reconciliations DROP CONSTRAINT IF EXISTS bank_reconciliations_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_reconciliations DROP CONSTRAINT IF EXISTS bank_reconciliations_bank_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_linked_account_id_fkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_company_id_fkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_user_id_fkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_company_id_fkey;
DROP INDEX IF EXISTS public.ix_warranties_id;
DROP INDEX IF EXISTS public.ix_wallets_id;
DROP INDEX IF EXISTS public.ix_wallet_transactions_id;
DROP INDEX IF EXISTS public.ix_users_username;
DROP INDEX IF EXISTS public.ix_users_id;
DROP INDEX IF EXISTS public.ix_users_email;
DROP INDEX IF EXISTS public.ix_treasury_transactions_id;
DROP INDEX IF EXISTS public.ix_treasury_transactions_company_id;
DROP INDEX IF EXISTS public.ix_technicians_id;
DROP INDEX IF EXISTS public.ix_technicians_employee_id;
DROP INDEX IF EXISTS public.ix_repair_orders_order_number;
DROP INDEX IF EXISTS public.ix_repair_orders_id;
DROP INDEX IF EXISTS public.ix_repair_orders_cufe;
DROP INDEX IF EXISTS public.ix_repair_items_id;
DROP INDEX IF EXISTS public.ix_reconciliation_lines_id;
DROP INDEX IF EXISTS public.ix_purchases_purchase_number;
DROP INDEX IF EXISTS public.ix_purchases_id;
DROP INDEX IF EXISTS public.ix_purchase_payments_id;
DROP INDEX IF EXISTS public.ix_purchase_items_id;
DROP INDEX IF EXISTS public.ix_products_sku;
DROP INDEX IF EXISTS public.ix_products_id;
DROP INDEX IF EXISTS public.ix_products_barcode;
DROP INDEX IF EXISTS public.ix_product_price_history_product_id;
DROP INDEX IF EXISTS public.ix_product_price_history_id;
DROP INDEX IF EXISTS public.ix_product_price_history_company_id;
DROP INDEX IF EXISTS public.ix_permissions_id;
DROP INDEX IF EXISTS public.ix_partners_nit;
DROP INDEX IF EXISTS public.ix_partners_id;
DROP INDEX IF EXISTS public.ix_journal_entry_lines_id;
DROP INDEX IF EXISTS public.ix_journal_entries_id;
DROP INDEX IF EXISTS public.ix_invoices_invoice_number;
DROP INDEX IF EXISTS public.ix_invoices_id;
DROP INDEX IF EXISTS public.ix_invoices_cufe;
DROP INDEX IF EXISTS public.ix_invoice_resolutions_id;
DROP INDEX IF EXISTS public.ix_invoice_items_id;
DROP INDEX IF EXISTS public.ix_inventory_movements_product_id;
DROP INDEX IF EXISTS public.ix_inventory_movements_id;
DROP INDEX IF EXISTS public.ix_inventory_movements_company_id;
DROP INDEX IF EXISTS public.ix_fiscal_periods_id;
DROP INDEX IF EXISTS public.ix_fiscal_periods_company_id;
DROP INDEX IF EXISTS public.ix_dian_billing_ranges_id;
DROP INDEX IF EXISTS public.ix_credit_debit_notes_id;
DROP INDEX IF EXISTS public.ix_companies_nit;
DROP INDEX IF EXISTS public.ix_companies_id;
DROP INDEX IF EXISTS public.ix_check_register_id;
DROP INDEX IF EXISTS public.ix_check_register_company_id;
DROP INDEX IF EXISTS public.ix_chart_of_accounts_id;
DROP INDEX IF EXISTS public.ix_chart_of_accounts_code;
DROP INDEX IF EXISTS public.ix_cash_accounts_id;
DROP INDEX IF EXISTS public.ix_cash_accounts_company_id;
DROP INDEX IF EXISTS public.ix_bank_reconciliations_id;
DROP INDEX IF EXISTS public.ix_bank_reconciliations_company_id;
DROP INDEX IF EXISTS public.ix_bank_accounts_id;
DROP INDEX IF EXISTS public.ix_bank_accounts_company_id;
DROP INDEX IF EXISTS public.ix_audit_logs_id;
ALTER TABLE IF EXISTS ONLY public.warranties DROP CONSTRAINT IF EXISTS warranties_pkey;
ALTER TABLE IF EXISTS ONLY public.wallets DROP CONSTRAINT IF EXISTS wallets_pkey;
ALTER TABLE IF EXISTS ONLY public.wallet_transactions DROP CONSTRAINT IF EXISTS wallet_transactions_pkey;
ALTER TABLE IF EXISTS ONLY public.users DROP CONSTRAINT IF EXISTS users_pkey;
ALTER TABLE IF EXISTS ONLY public.user_permissions DROP CONSTRAINT IF EXISTS user_permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS uq_product_sku_company;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS uq_product_barcode_company;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS uq_invoice_number_per_company;
ALTER TABLE IF EXISTS ONLY public.chart_of_accounts DROP CONSTRAINT IF EXISTS uq_chart_code_company;
ALTER TABLE IF EXISTS ONLY public.invoice_resolutions DROP CONSTRAINT IF EXISTS uq_active_resolution_per_company_type;
ALTER TABLE IF EXISTS ONLY public.treasury_transactions DROP CONSTRAINT IF EXISTS treasury_transactions_pkey;
ALTER TABLE IF EXISTS ONLY public.technicians DROP CONSTRAINT IF EXISTS technicians_pkey;
ALTER TABLE IF EXISTS ONLY public.repair_orders DROP CONSTRAINT IF EXISTS repair_orders_pkey;
ALTER TABLE IF EXISTS ONLY public.repair_items DROP CONSTRAINT IF EXISTS repair_items_pkey;
ALTER TABLE IF EXISTS ONLY public.reconciliation_lines DROP CONSTRAINT IF EXISTS reconciliation_lines_pkey;
ALTER TABLE IF EXISTS ONLY public.purchases DROP CONSTRAINT IF EXISTS purchases_pkey;
ALTER TABLE IF EXISTS ONLY public.purchase_payments DROP CONSTRAINT IF EXISTS purchase_payments_pkey;
ALTER TABLE IF EXISTS ONLY public.purchase_items DROP CONSTRAINT IF EXISTS purchase_items_pkey;
ALTER TABLE IF EXISTS ONLY public.products DROP CONSTRAINT IF EXISTS products_pkey;
ALTER TABLE IF EXISTS ONLY public.product_price_history DROP CONSTRAINT IF EXISTS product_price_history_pkey;
ALTER TABLE IF EXISTS ONLY public.permissions DROP CONSTRAINT IF EXISTS permissions_pkey;
ALTER TABLE IF EXISTS ONLY public.permissions DROP CONSTRAINT IF EXISTS permissions_name_key;
ALTER TABLE IF EXISTS ONLY public.partners DROP CONSTRAINT IF EXISTS partners_pkey;
ALTER TABLE IF EXISTS ONLY public.journal_entry_lines DROP CONSTRAINT IF EXISTS journal_entry_lines_pkey;
ALTER TABLE IF EXISTS ONLY public.journal_entries DROP CONSTRAINT IF EXISTS journal_entries_pkey;
ALTER TABLE IF EXISTS ONLY public.invoices DROP CONSTRAINT IF EXISTS invoices_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_resolutions DROP CONSTRAINT IF EXISTS invoice_resolutions_pkey;
ALTER TABLE IF EXISTS ONLY public.invoice_items DROP CONSTRAINT IF EXISTS invoice_items_pkey;
ALTER TABLE IF EXISTS ONLY public.inventory_movements DROP CONSTRAINT IF EXISTS inventory_movements_pkey;
ALTER TABLE IF EXISTS ONLY public.fiscal_periods DROP CONSTRAINT IF EXISTS fiscal_periods_pkey;
ALTER TABLE IF EXISTS ONLY public.dian_billing_ranges DROP CONSTRAINT IF EXISTS dian_billing_ranges_pkey;
ALTER TABLE IF EXISTS ONLY public.credit_debit_notes DROP CONSTRAINT IF EXISTS credit_debit_notes_pkey;
ALTER TABLE IF EXISTS ONLY public.credit_debit_notes DROP CONSTRAINT IF EXISTS credit_debit_notes_note_number_key;
ALTER TABLE IF EXISTS ONLY public.companies DROP CONSTRAINT IF EXISTS companies_pkey;
ALTER TABLE IF EXISTS ONLY public.check_register DROP CONSTRAINT IF EXISTS check_register_pkey;
ALTER TABLE IF EXISTS ONLY public.chart_of_accounts DROP CONSTRAINT IF EXISTS chart_of_accounts_pkey;
ALTER TABLE IF EXISTS ONLY public.cash_accounts DROP CONSTRAINT IF EXISTS cash_accounts_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_reconciliations DROP CONSTRAINT IF EXISTS bank_reconciliations_pkey;
ALTER TABLE IF EXISTS ONLY public.bank_accounts DROP CONSTRAINT IF EXISTS bank_accounts_pkey;
ALTER TABLE IF EXISTS ONLY public.audit_logs DROP CONSTRAINT IF EXISTS audit_logs_pkey;
ALTER TABLE IF EXISTS ONLY public.alembic_version DROP CONSTRAINT IF EXISTS alembic_version_pkc;
ALTER TABLE IF EXISTS public.warranties ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.wallets ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.wallet_transactions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.users ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.treasury_transactions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.technicians ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.repair_orders ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.repair_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.reconciliation_lines ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.purchases ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.purchase_payments ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.purchase_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.products ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.product_price_history ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.permissions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.partners ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.journal_entry_lines ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.journal_entries ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoices ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice_resolutions ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.invoice_items ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.inventory_movements ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.fiscal_periods ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.dian_billing_ranges ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.credit_debit_notes ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.companies ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.check_register ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.chart_of_accounts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.cash_accounts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bank_reconciliations ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.bank_accounts ALTER COLUMN id DROP DEFAULT;
ALTER TABLE IF EXISTS public.audit_logs ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS public.warranties_id_seq;
DROP TABLE IF EXISTS public.warranties;
DROP SEQUENCE IF EXISTS public.wallets_id_seq;
DROP TABLE IF EXISTS public.wallets;
DROP SEQUENCE IF EXISTS public.wallet_transactions_id_seq;
DROP TABLE IF EXISTS public.wallet_transactions;
DROP SEQUENCE IF EXISTS public.users_id_seq;
DROP TABLE IF EXISTS public.users;
DROP TABLE IF EXISTS public.user_permissions;
DROP SEQUENCE IF EXISTS public.treasury_transactions_id_seq;
DROP TABLE IF EXISTS public.treasury_transactions;
DROP SEQUENCE IF EXISTS public.technicians_id_seq;
DROP TABLE IF EXISTS public.technicians;
DROP SEQUENCE IF EXISTS public.repair_orders_id_seq;
DROP TABLE IF EXISTS public.repair_orders;
DROP SEQUENCE IF EXISTS public.repair_items_id_seq;
DROP TABLE IF EXISTS public.repair_items;
DROP SEQUENCE IF EXISTS public.reconciliation_lines_id_seq;
DROP TABLE IF EXISTS public.reconciliation_lines;
DROP SEQUENCE IF EXISTS public.purchases_id_seq;
DROP TABLE IF EXISTS public.purchases;
DROP SEQUENCE IF EXISTS public.purchase_payments_id_seq;
DROP TABLE IF EXISTS public.purchase_payments;
DROP SEQUENCE IF EXISTS public.purchase_items_id_seq;
DROP TABLE IF EXISTS public.purchase_items;
DROP SEQUENCE IF EXISTS public.products_id_seq;
DROP TABLE IF EXISTS public.products;
DROP SEQUENCE IF EXISTS public.product_price_history_id_seq;
DROP TABLE IF EXISTS public.product_price_history;
DROP SEQUENCE IF EXISTS public.permissions_id_seq;
DROP TABLE IF EXISTS public.permissions;
DROP SEQUENCE IF EXISTS public.partners_id_seq;
DROP TABLE IF EXISTS public.partners;
DROP SEQUENCE IF EXISTS public.journal_entry_lines_id_seq;
DROP TABLE IF EXISTS public.journal_entry_lines;
DROP SEQUENCE IF EXISTS public.journal_entries_id_seq;
DROP TABLE IF EXISTS public.journal_entries;
DROP SEQUENCE IF EXISTS public.invoices_id_seq;
DROP TABLE IF EXISTS public.invoices;
DROP SEQUENCE IF EXISTS public.invoice_resolutions_id_seq;
DROP TABLE IF EXISTS public.invoice_resolutions;
DROP SEQUENCE IF EXISTS public.invoice_items_id_seq;
DROP TABLE IF EXISTS public.invoice_items;
DROP SEQUENCE IF EXISTS public.inventory_movements_id_seq;
DROP TABLE IF EXISTS public.inventory_movements;
DROP SEQUENCE IF EXISTS public.fiscal_periods_id_seq;
DROP TABLE IF EXISTS public.fiscal_periods;
DROP SEQUENCE IF EXISTS public.dian_billing_ranges_id_seq;
DROP TABLE IF EXISTS public.dian_billing_ranges;
DROP SEQUENCE IF EXISTS public.credit_debit_notes_id_seq;
DROP TABLE IF EXISTS public.credit_debit_notes;
DROP SEQUENCE IF EXISTS public.companies_id_seq;
DROP TABLE IF EXISTS public.companies;
DROP SEQUENCE IF EXISTS public.check_register_id_seq;
DROP TABLE IF EXISTS public.check_register;
DROP SEQUENCE IF EXISTS public.chart_of_accounts_id_seq;
DROP TABLE IF EXISTS public.chart_of_accounts;
DROP SEQUENCE IF EXISTS public.cash_accounts_id_seq;
DROP TABLE IF EXISTS public.cash_accounts;
DROP SEQUENCE IF EXISTS public.bank_reconciliations_id_seq;
DROP TABLE IF EXISTS public.bank_reconciliations;
DROP SEQUENCE IF EXISTS public.bank_accounts_id_seq;
DROP TABLE IF EXISTS public.bank_accounts;
DROP SEQUENCE IF EXISTS public.audit_logs_id_seq;
DROP TABLE IF EXISTS public.audit_logs;
DROP TABLE IF EXISTS public.alembic_version;
DROP TYPE IF EXISTS public.warranty_types;
DROP TYPE IF EXISTS public.warranty_statuses;
DROP TYPE IF EXISTS public.warranty_status_types;
DROP TYPE IF EXISTS public.wallet_tx_types;
DROP TYPE IF EXISTS public.user_roles;
DROP TYPE IF EXISTS public.treasury_tx_types;
DROP TYPE IF EXISTS public.treasury_account_types;
DROP TYPE IF EXISTS public.responsibility_fiscal_types;
DROP TYPE IF EXISTS public.repair_order_status;
DROP TYPE IF EXISTS public.regimen_types;
DROP TYPE IF EXISTS public.reconciliation_status;
DROP TYPE IF EXISTS public.purchase_status;
DROP TYPE IF EXISTS public.payment_methods;
DROP TYPE IF EXISTS public.partner_types;
DROP TYPE IF EXISTS public.note_types;
DROP TYPE IF EXISTS public.note_dian_status;
DROP TYPE IF EXISTS public.invoice_types;
DROP TYPE IF EXISTS public.invoice_status;
DROP TYPE IF EXISTS public.invoice_dian_state;
DROP TYPE IF EXISTS public.inventorymovementtype;
DROP TYPE IF EXISTS public.check_status;
DROP TYPE IF EXISTS public.cash_account_types;
DROP TYPE IF EXISTS public.bank_account_types;
DROP TYPE IF EXISTS public.audit_actions;
DROP TYPE IF EXISTS public.account_types;
--
-- Name: account_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.account_types AS ENUM (
    'ASSET',
    'LIABILITY',
    'EQUITY',
    'REVENUE',
    'EXPENSE',
    'COST'
);


ALTER TYPE public.account_types OWNER TO "user";

--
-- Name: audit_actions; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.audit_actions AS ENUM (
    'CREATE',
    'UPDATE',
    'DELETE',
    'LOGIN',
    'LOGOUT'
);


ALTER TYPE public.audit_actions OWNER TO "user";

--
-- Name: bank_account_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.bank_account_types AS ENUM (
    'CHECKING',
    'SAVINGS',
    'TIME_DEPOSIT'
);


ALTER TYPE public.bank_account_types OWNER TO "user";

--
-- Name: cash_account_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.cash_account_types AS ENUM (
    'MAIN_CASH',
    'PETTY_CASH',
    'REGISTER_CASH'
);


ALTER TYPE public.cash_account_types OWNER TO "user";

--
-- Name: check_status; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.check_status AS ENUM (
    'ISSUED',
    'DELIVERED',
    'CLEARED',
    'BOUNCED',
    'VOIDED'
);


ALTER TYPE public.check_status OWNER TO "user";

--
-- Name: inventorymovementtype; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.inventorymovementtype AS ENUM (
    'ADD',
    'DEDUCT',
    'ADJUST'
);


ALTER TYPE public.inventorymovementtype OWNER TO "user";

--
-- Name: invoice_dian_state; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.invoice_dian_state AS ENUM (
    'BORRADOR',
    'ENVIADO',
    'ACEPTADO',
    'RECHAZADO',
    'NO_APLICA'
);


ALTER TYPE public.invoice_dian_state OWNER TO "user";

--
-- Name: invoice_status; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.invoice_status AS ENUM (
    'DRAFT',
    'ISSUED',
    'PAID',
    'CANCELLED'
);


ALTER TYPE public.invoice_status OWNER TO "user";

--
-- Name: invoice_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.invoice_types AS ENUM (
    'SALE',
    'PURCHASE',
    'CUENTA_COBRO'
);


ALTER TYPE public.invoice_types OWNER TO "user";

--
-- Name: note_dian_status; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.note_dian_status AS ENUM (
    'BORRADOR',
    'ENVIADO',
    'ACEPTADO',
    'RECHAZADO'
);


ALTER TYPE public.note_dian_status OWNER TO "user";

--
-- Name: note_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.note_types AS ENUM (
    'CREDIT',
    'DEBIT'
);


ALTER TYPE public.note_types OWNER TO "user";

--
-- Name: partner_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.partner_types AS ENUM (
    'SUPPLIER',
    'CUSTOMER',
    'BOTH'
);


ALTER TYPE public.partner_types OWNER TO "user";

--
-- Name: payment_methods; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.payment_methods AS ENUM (
    'CASH',
    'BANK_TRANSFER',
    'CHECK',
    'CREDIT_CARD',
    'CREDIT',
    'PARTIAL_CREDIT'
);


ALTER TYPE public.payment_methods OWNER TO "user";

--
-- Name: purchase_status; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.purchase_status AS ENUM (
    'DRAFT',
    'ISSUED',
    'PAID',
    'PARTIAL',
    'OVERDUE',
    'CANCELLED'
);


ALTER TYPE public.purchase_status OWNER TO "user";

--
-- Name: reconciliation_status; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.reconciliation_status AS ENUM (
    'IN_PROGRESS',
    'COMPLETED'
);


ALTER TYPE public.reconciliation_status OWNER TO "user";

--
-- Name: regimen_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.regimen_types AS ENUM (
    'COMUN',
    'SIMPLE',
    'ESPECIAL',
    'NO_RESPONSABLE'
);


ALTER TYPE public.regimen_types OWNER TO "user";

--
-- Name: repair_order_status; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.repair_order_status AS ENUM (
    'RECEIVED',
    'DIAGNOSIS',
    'APPROVED',
    'IN_REPAIR',
    'WAITING_PARTS',
    'READY',
    'DELIVERED',
    'CANCELLED'
);


ALTER TYPE public.repair_order_status OWNER TO "user";

--
-- Name: responsibility_fiscal_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.responsibility_fiscal_types AS ENUM (
    'RESPONSABLE IVA',
    'NO RESPONSABLE',
    'AGENTE RETENEDOR'
);


ALTER TYPE public.responsibility_fiscal_types OWNER TO "user";

--
-- Name: treasury_account_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.treasury_account_types AS ENUM (
    'BANK',
    'CASH'
);


ALTER TYPE public.treasury_account_types OWNER TO "user";

--
-- Name: treasury_tx_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.treasury_tx_types AS ENUM (
    'DEPOSIT',
    'WITHDRAWAL',
    'TRANSFER_IN',
    'TRANSFER_OUT',
    'FEE',
    'INTEREST',
    'CHECK_ISSUED',
    'CHECK_CLEARED',
    'CHECK_BOUNCED'
);


ALTER TYPE public.treasury_tx_types OWNER TO "user";

--
-- Name: user_roles; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.user_roles AS ENUM (
    'ADMINISTRADOR',
    'CONTADOR',
    'TECNICO',
    'VENDEDOR',
    'BODEGUERO'
);


ALTER TYPE public.user_roles OWNER TO "user";

--
-- Name: wallet_tx_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.wallet_tx_types AS ENUM (
    'DEPOSIT',
    'WITHDRAWAL',
    'TRANSFER_IN',
    'TRANSFER_OUT',
    'LOYALTY_EARN',
    'LOYALTY_REDEEM'
);


ALTER TYPE public.wallet_tx_types OWNER TO "user";

--
-- Name: warranty_status_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.warranty_status_types AS ENUM (
    'NO_WARRANTY',
    'IN_WARRANTY',
    'WARRANTY_VOID'
);


ALTER TYPE public.warranty_status_types OWNER TO "user";

--
-- Name: warranty_statuses; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.warranty_statuses AS ENUM (
    'ACTIVE',
    'EXPIRED',
    'VOID',
    'CLAIMED'
);


ALTER TYPE public.warranty_statuses OWNER TO "user";

--
-- Name: warranty_types; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.warranty_types AS ENUM (
    'MANUFACTURER',
    'SERVICE',
    'PARTS'
);


ALTER TYPE public.warranty_types OWNER TO "user";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO "user";

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    company_id integer,
    action public.audit_actions NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id integer,
    old_values text,
    new_values text,
    ip_address character varying(45),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.audit_logs OWNER TO "user";

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO "user";

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: bank_accounts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.bank_accounts (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(255) NOT NULL,
    bank_name character varying(255) NOT NULL,
    account_number character varying(50) NOT NULL,
    account_type public.bank_account_types NOT NULL,
    currency character varying(3),
    initial_balance numeric(15,2),
    current_balance numeric(15,2),
    is_active boolean,
    branch_office character varying(255),
    swift_code character varying(20),
    routing_number character varying(20),
    linked_account_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.bank_accounts OWNER TO "user";

--
-- Name: bank_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.bank_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_accounts_id_seq OWNER TO "user";

--
-- Name: bank_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.bank_accounts_id_seq OWNED BY public.bank_accounts.id;


--
-- Name: bank_reconciliations; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.bank_reconciliations (
    id integer NOT NULL,
    company_id integer NOT NULL,
    bank_account_id integer NOT NULL,
    statement_date timestamp with time zone NOT NULL,
    statement_balance numeric(15,2) NOT NULL,
    system_balance numeric(15,2) NOT NULL,
    outstanding_deposits numeric(15,2),
    outstanding_checks numeric(15,2),
    bank_fees_not_recorded numeric(15,2),
    interest_not_recorded numeric(15,2),
    adjusted_balance numeric(15,2),
    is_balanced boolean,
    status public.reconciliation_status NOT NULL,
    reconciled_by integer,
    reconciled_at timestamp with time zone,
    notes character varying(1000),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.bank_reconciliations OWNER TO "user";

--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.bank_reconciliations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.bank_reconciliations_id_seq OWNER TO "user";

--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.bank_reconciliations_id_seq OWNED BY public.bank_reconciliations.id;


--
-- Name: cash_accounts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.cash_accounts (
    id integer NOT NULL,
    company_id integer NOT NULL,
    name character varying(255) NOT NULL,
    account_type public.cash_account_types NOT NULL,
    currency character varying(3),
    initial_balance numeric(15,2),
    current_balance numeric(15,2),
    responsible_user_id integer,
    max_petty_cash_amount numeric(15,2),
    is_active boolean,
    linked_account_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.cash_accounts OWNER TO "user";

--
-- Name: cash_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.cash_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cash_accounts_id_seq OWNER TO "user";

--
-- Name: cash_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.cash_accounts_id_seq OWNED BY public.cash_accounts.id;


--
-- Name: chart_of_accounts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.chart_of_accounts (
    id integer NOT NULL,
    code character varying(20) NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(500),
    account_type public.account_types NOT NULL,
    is_active boolean,
    parent_id integer,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.chart_of_accounts OWNER TO "user";

--
-- Name: chart_of_accounts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.chart_of_accounts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chart_of_accounts_id_seq OWNER TO "user";

--
-- Name: chart_of_accounts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.chart_of_accounts_id_seq OWNED BY public.chart_of_accounts.id;


--
-- Name: check_register; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.check_register (
    id integer NOT NULL,
    company_id integer NOT NULL,
    bank_account_id integer NOT NULL,
    check_number character varying(30) NOT NULL,
    payee character varying(255) NOT NULL,
    amount numeric(15,2) NOT NULL,
    issue_date timestamp with time zone NOT NULL,
    status public.check_status NOT NULL,
    cleared_date timestamp with time zone,
    linked_transaction_id integer,
    notes character varying(500),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.check_register OWNER TO "user";

--
-- Name: check_register_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.check_register_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.check_register_id_seq OWNER TO "user";

--
-- Name: check_register_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.check_register_id_seq OWNED BY public.check_register.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    nit character varying(20) NOT NULL,
    dv character varying(1) NOT NULL,
    legal_representative character varying(255) NOT NULL,
    address character varying(500),
    phone character varying(50),
    email character varying(255),
    logo_url character varying(500),
    regimen public.regimen_types,
    fecha_inicio_actividades date NOT NULL,
    resolucion_facturacion character varying(100),
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.companies OWNER TO "user";

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO "user";

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: credit_debit_notes; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.credit_debit_notes (
    id integer NOT NULL,
    company_id integer NOT NULL,
    original_invoice_id integer NOT NULL,
    note_type public.note_types NOT NULL,
    reason character varying(500) NOT NULL,
    amount double precision NOT NULL,
    note_number character varying(50) NOT NULL,
    cufe character varying(128),
    xml_ubl text,
    estado_dian public.note_dian_status,
    fecha_envio_dian timestamp with time zone,
    motivo_rechazo text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.credit_debit_notes OWNER TO "user";

--
-- Name: credit_debit_notes_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.credit_debit_notes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.credit_debit_notes_id_seq OWNER TO "user";

--
-- Name: credit_debit_notes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.credit_debit_notes_id_seq OWNED BY public.credit_debit_notes.id;


--
-- Name: dian_billing_ranges; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.dian_billing_ranges (
    id integer NOT NULL,
    company_id integer NOT NULL,
    resolution character varying(100) NOT NULL,
    prefix character varying(10) NOT NULL,
    from_number integer NOT NULL,
    to_number integer NOT NULL,
    next_number integer NOT NULL,
    approval_date date NOT NULL,
    expiration_date date NOT NULL,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.dian_billing_ranges OWNER TO "user";

--
-- Name: dian_billing_ranges_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.dian_billing_ranges_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.dian_billing_ranges_id_seq OWNER TO "user";

--
-- Name: dian_billing_ranges_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.dian_billing_ranges_id_seq OWNED BY public.dian_billing_ranges.id;


--
-- Name: fiscal_periods; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.fiscal_periods (
    id integer NOT NULL,
    company_id integer NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    is_closed boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.fiscal_periods OWNER TO "user";

--
-- Name: fiscal_periods_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.fiscal_periods_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.fiscal_periods_id_seq OWNER TO "user";

--
-- Name: fiscal_periods_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.fiscal_periods_id_seq OWNED BY public.fiscal_periods.id;


--
-- Name: inventory_movements; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.inventory_movements (
    id integer NOT NULL,
    product_id integer NOT NULL,
    company_id integer NOT NULL,
    movement_type public.inventorymovementtype NOT NULL,
    quantity numeric(15,2) NOT NULL,
    reference character varying(255),
    reference_id integer,
    reference_type character varying(50),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.inventory_movements OWNER TO "user";

--
-- Name: inventory_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.inventory_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_movements_id_seq OWNER TO "user";

--
-- Name: inventory_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.inventory_movements_id_seq OWNED BY public.inventory_movements.id;


--
-- Name: invoice_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.invoice_items (
    id integer NOT NULL,
    invoice_id integer,
    description character varying(255) NOT NULL,
    quantity numeric(10,2) NOT NULL,
    unit_price numeric(15,2) NOT NULL,
    discount numeric(15,2),
    tax_rate numeric(5,2),
    tax_amount numeric(15,2),
    line_total numeric(15,2) NOT NULL,
    product_id integer,
    assembly_group_id character varying(50),
    serial_number character varying(255)
);


ALTER TABLE public.invoice_items OWNER TO "user";

--
-- Name: invoice_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.invoice_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_items_id_seq OWNER TO "user";

--
-- Name: invoice_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.invoice_items_id_seq OWNED BY public.invoice_items.id;


--
-- Name: invoice_resolutions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.invoice_resolutions (
    id integer NOT NULL,
    company_id integer NOT NULL,
    resolution_type character varying(50) NOT NULL,
    resolution_number character varying(100),
    prefix character varying(20) NOT NULL,
    start_number integer NOT NULL,
    end_number integer,
    current_number integer NOT NULL,
    start_date timestamp with time zone,
    end_date timestamp with time zone,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.invoice_resolutions OWNER TO "user";

--
-- Name: invoice_resolutions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.invoice_resolutions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoice_resolutions_id_seq OWNER TO "user";

--
-- Name: invoice_resolutions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.invoice_resolutions_id_seq OWNED BY public.invoice_resolutions.id;


--
-- Name: invoices; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.invoices (
    id integer NOT NULL,
    invoice_number character varying(50) NOT NULL,
    invoice_type public.invoice_types NOT NULL,
    partner_id integer,
    issue_date timestamp with time zone DEFAULT now() NOT NULL,
    due_date timestamp with time zone,
    total_amount numeric(15,2) NOT NULL,
    currency character varying(3),
    status public.invoice_status,
    cufe character varying(100),
    xml_ubl character varying,
    estado_dian public.invoice_dian_state,
    motivo_rechazo character varying,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.invoices OWNER TO "user";

--
-- Name: invoices_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.invoices_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.invoices_id_seq OWNER TO "user";

--
-- Name: invoices_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.invoices_id_seq OWNED BY public.invoices.id;


--
-- Name: journal_entries; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.journal_entries (
    id integer NOT NULL,
    entry_date timestamp with time zone DEFAULT now() NOT NULL,
    description character varying(500),
    reference character varying(100),
    is_posted boolean,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.journal_entries OWNER TO "user";

--
-- Name: journal_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.journal_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.journal_entries_id_seq OWNER TO "user";

--
-- Name: journal_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.journal_entries_id_seq OWNED BY public.journal_entries.id;


--
-- Name: journal_entry_lines; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.journal_entry_lines (
    id integer NOT NULL,
    journal_entry_id integer,
    account_id integer,
    debit_amount numeric(15,2),
    credit_amount numeric(15,2),
    description character varying(255),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.journal_entry_lines OWNER TO "user";

--
-- Name: journal_entry_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.journal_entry_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.journal_entry_lines_id_seq OWNER TO "user";

--
-- Name: journal_entry_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.journal_entry_lines_id_seq OWNED BY public.journal_entry_lines.id;


--
-- Name: partners; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.partners (
    id integer NOT NULL,
    nit character varying(20),
    dv character varying(1),
    name character varying(255) NOT NULL,
    partner_type public.partner_types NOT NULL,
    responsibility_fiscal public.responsibility_fiscal_types,
    address character varying(500),
    phone character varying(50),
    email character varying(255),
    contact_person character varying(255),
    credit_limit double precision,
    is_active boolean,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.partners OWNER TO "user";

--
-- Name: partners_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.partners_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.partners_id_seq OWNER TO "user";

--
-- Name: partners_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.partners_id_seq OWNED BY public.partners.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.permissions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    module character varying(50) NOT NULL,
    action character varying(50) NOT NULL
);


ALTER TABLE public.permissions OWNER TO "user";

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.permissions_id_seq OWNER TO "user";

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: product_price_history; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.product_price_history (
    id integer NOT NULL,
    product_id integer NOT NULL,
    company_id integer NOT NULL,
    price numeric(15,2) NOT NULL,
    effective_date timestamp with time zone DEFAULT now()
);


ALTER TABLE public.product_price_history OWNER TO "user";

--
-- Name: product_price_history_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.product_price_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_price_history_id_seq OWNER TO "user";

--
-- Name: product_price_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.product_price_history_id_seq OWNED BY public.product_price_history.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.products (
    id integer NOT NULL,
    sku character varying(50) NOT NULL,
    barcode character varying(100),
    name character varying(255) NOT NULL,
    description character varying(500),
    category character varying(100),
    brand character varying(100),
    model character varying(100),
    unit_of_measure character varying(50),
    purchase_price numeric(15,2) NOT NULL,
    sale_price numeric(15,2) NOT NULL,
    stock_level numeric(15,2),
    min_stock_level numeric(15,2),
    max_stock_level numeric(15,2),
    is_active boolean,
    company_id integer,
    supplier_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    payment_method character varying(50) DEFAULT 'CASH'::character varying
);


ALTER TABLE public.products OWNER TO "user";

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO "user";

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: purchase_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchase_items (
    id integer NOT NULL,
    purchase_id integer NOT NULL,
    product_id integer,
    description character varying(255) NOT NULL,
    quantity numeric(10,2) NOT NULL,
    unit_price numeric(15,2) NOT NULL,
    discount_percent numeric(5,2),
    discount_amount numeric(15,2),
    tax_rate numeric(5,2),
    tax_amount numeric(15,2),
    line_total numeric(15,2) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    serial_number character varying(255)
);


ALTER TABLE public.purchase_items OWNER TO "user";

--
-- Name: purchase_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchase_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchase_items_id_seq OWNER TO "user";

--
-- Name: purchase_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchase_items_id_seq OWNED BY public.purchase_items.id;


--
-- Name: purchase_payments; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchase_payments (
    id integer NOT NULL,
    purchase_id integer NOT NULL,
    payment_method public.payment_methods NOT NULL,
    amount numeric(15,2) NOT NULL,
    payment_date timestamp with time zone DEFAULT now() NOT NULL,
    reference character varying(100),
    notes text,
    created_by integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.purchase_payments OWNER TO "user";

--
-- Name: purchase_payments_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchase_payments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchase_payments_id_seq OWNER TO "user";

--
-- Name: purchase_payments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchase_payments_id_seq OWNED BY public.purchase_payments.id;


--
-- Name: purchases; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.purchases (
    id integer NOT NULL,
    purchase_number character varying(50) NOT NULL,
    partner_id integer NOT NULL,
    purchase_date timestamp with time zone DEFAULT now() NOT NULL,
    due_date timestamp with time zone,
    subtotal numeric(15,2) NOT NULL,
    tax_amount numeric(15,2),
    total_amount numeric(15,2) NOT NULL,
    discount_amount numeric(15,2),
    currency character varying(3),
    payment_method public.payment_methods NOT NULL,
    status public.purchase_status,
    notes text,
    company_id integer NOT NULL,
    created_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.purchases OWNER TO "user";

--
-- Name: purchases_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.purchases_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.purchases_id_seq OWNER TO "user";

--
-- Name: purchases_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.purchases_id_seq OWNED BY public.purchases.id;


--
-- Name: reconciliation_lines; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.reconciliation_lines (
    id integer NOT NULL,
    reconciliation_id integer NOT NULL,
    treasury_transaction_id integer,
    is_matched boolean,
    amount numeric(15,2) NOT NULL,
    description character varying(500),
    statement_date timestamp with time zone,
    system_date timestamp with time zone,
    difference numeric(15,2),
    notes character varying(500),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.reconciliation_lines OWNER TO "user";

--
-- Name: reconciliation_lines_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.reconciliation_lines_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.reconciliation_lines_id_seq OWNER TO "user";

--
-- Name: reconciliation_lines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.reconciliation_lines_id_seq OWNED BY public.reconciliation_lines.id;


--
-- Name: repair_items; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.repair_items (
    id integer NOT NULL,
    repair_order_id integer,
    description character varying(255) NOT NULL,
    serial_number character varying(100),
    model character varying(100),
    brand character varying(100),
    issue_reported character varying(500),
    quantity integer,
    unit_cost numeric(15,2),
    discount numeric(15,2),
    tax_rate numeric(5,2),
    tax_amount numeric(15,2),
    line_total numeric(15,2),
    warranty_status public.warranty_status_types,
    warranty_days integer,
    product_id integer
);


ALTER TABLE public.repair_items OWNER TO "user";

--
-- Name: repair_items_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.repair_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.repair_items_id_seq OWNER TO "user";

--
-- Name: repair_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.repair_items_id_seq OWNED BY public.repair_items.id;


--
-- Name: repair_orders; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.repair_orders (
    id integer NOT NULL,
    order_number character varying(50) NOT NULL,
    partner_id integer,
    technician_id integer,
    issue_date timestamp with time zone DEFAULT now() NOT NULL,
    expected_delivery_date timestamp with time zone,
    actual_delivery_date timestamp with time zone,
    problem_description character varying(1000),
    diagnosis character varying(1000),
    service_notes character varying(2000),
    status public.repair_order_status,
    warranty_applied boolean,
    total_labor_cost numeric(15,2),
    total_parts_cost numeric(15,2),
    total_amount numeric(15,2),
    currency character varying(3),
    cufe character varying(100),
    xml_ubl character varying,
    estado_dian public.invoice_dian_state,
    motivo_rechazo character varying,
    invoice_id integer,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.repair_orders OWNER TO "user";

--
-- Name: repair_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.repair_orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.repair_orders_id_seq OWNER TO "user";

--
-- Name: repair_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.repair_orders_id_seq OWNED BY public.repair_orders.id;


--
-- Name: technicians; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.technicians (
    id integer NOT NULL,
    employee_id character varying(50) NOT NULL,
    first_name character varying(100) NOT NULL,
    last_name character varying(100) NOT NULL,
    specialty character varying(200),
    is_active boolean,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.technicians OWNER TO "user";

--
-- Name: technicians_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.technicians_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.technicians_id_seq OWNER TO "user";

--
-- Name: technicians_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.technicians_id_seq OWNED BY public.technicians.id;


--
-- Name: treasury_transactions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.treasury_transactions (
    id integer NOT NULL,
    company_id integer NOT NULL,
    account_type public.treasury_account_types NOT NULL,
    bank_account_id integer,
    cash_account_id integer,
    transaction_type public.treasury_tx_types NOT NULL,
    amount numeric(15,2) NOT NULL,
    currency character varying(3),
    description character varying(500),
    reference character varying(100),
    reference_type character varying(50),
    reference_id integer,
    journal_entry_id integer,
    balance_after numeric(15,2),
    created_by integer,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.treasury_transactions OWNER TO "user";

--
-- Name: treasury_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.treasury_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.treasury_transactions_id_seq OWNER TO "user";

--
-- Name: treasury_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.treasury_transactions_id_seq OWNED BY public.treasury_transactions.id;


--
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.user_permissions (
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.user_permissions OWNER TO "user";

--
-- Name: users; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying(255) NOT NULL,
    username character varying(100) NOT NULL,
    hashed_password character varying(255) NOT NULL,
    full_name character varying(255),
    role public.user_roles,
    is_active boolean,
    is_superuser boolean,
    company_id integer,
    hashed_refresh_token text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.users OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: wallet_transactions; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.wallet_transactions (
    id integer NOT NULL,
    wallet_id integer,
    transaction_type public.wallet_tx_types NOT NULL,
    amount numeric(15,2) NOT NULL,
    description character varying(500),
    reference_type character varying(50),
    reference_id integer,
    balance_after numeric(15,2),
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.wallet_transactions OWNER TO "user";

--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.wallet_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.wallet_transactions_id_seq OWNER TO "user";

--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.wallet_transactions_id_seq OWNED BY public.wallet_transactions.id;


--
-- Name: wallets; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.wallets (
    id integer NOT NULL,
    partner_id integer,
    user_id integer,
    balance numeric(15,2),
    loyalty_points numeric(15,2),
    currency character varying(3),
    is_active boolean,
    company_id integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.wallets OWNER TO "user";

--
-- Name: wallets_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.wallets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.wallets_id_seq OWNER TO "user";

--
-- Name: wallets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.wallets_id_seq OWNED BY public.wallets.id;


--
-- Name: warranties; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.warranties (
    id integer NOT NULL,
    repair_order_id integer NOT NULL,
    repair_item_id integer,
    company_id integer NOT NULL,
    warranty_type public.warranty_types NOT NULL,
    start_date timestamp with time zone NOT NULL,
    end_date timestamp with time zone NOT NULL,
    status public.warranty_statuses,
    description character varying(1000),
    terms_and_conditions text,
    claim_date timestamp with time zone,
    claim_description character varying(1000),
    claim_resolution character varying(1000),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.warranties OWNER TO "user";

--
-- Name: warranties_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.warranties_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.warranties_id_seq OWNER TO "user";

--
-- Name: warranties_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.warranties_id_seq OWNED BY public.warranties.id;


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: bank_accounts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_accounts ALTER COLUMN id SET DEFAULT nextval('public.bank_accounts_id_seq'::regclass);


--
-- Name: bank_reconciliations id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_reconciliations ALTER COLUMN id SET DEFAULT nextval('public.bank_reconciliations_id_seq'::regclass);


--
-- Name: cash_accounts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_accounts ALTER COLUMN id SET DEFAULT nextval('public.cash_accounts_id_seq'::regclass);


--
-- Name: chart_of_accounts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts ALTER COLUMN id SET DEFAULT nextval('public.chart_of_accounts_id_seq'::regclass);


--
-- Name: check_register id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.check_register ALTER COLUMN id SET DEFAULT nextval('public.check_register_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: credit_debit_notes id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.credit_debit_notes ALTER COLUMN id SET DEFAULT nextval('public.credit_debit_notes_id_seq'::regclass);


--
-- Name: dian_billing_ranges id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.dian_billing_ranges ALTER COLUMN id SET DEFAULT nextval('public.dian_billing_ranges_id_seq'::regclass);


--
-- Name: fiscal_periods id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.fiscal_periods ALTER COLUMN id SET DEFAULT nextval('public.fiscal_periods_id_seq'::regclass);


--
-- Name: inventory_movements id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_movements ALTER COLUMN id SET DEFAULT nextval('public.inventory_movements_id_seq'::regclass);


--
-- Name: invoice_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_items ALTER COLUMN id SET DEFAULT nextval('public.invoice_items_id_seq'::regclass);


--
-- Name: invoice_resolutions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_resolutions ALTER COLUMN id SET DEFAULT nextval('public.invoice_resolutions_id_seq'::regclass);


--
-- Name: invoices id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoices ALTER COLUMN id SET DEFAULT nextval('public.invoices_id_seq'::regclass);


--
-- Name: journal_entries id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries ALTER COLUMN id SET DEFAULT nextval('public.journal_entries_id_seq'::regclass);


--
-- Name: journal_entry_lines id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entry_lines ALTER COLUMN id SET DEFAULT nextval('public.journal_entry_lines_id_seq'::regclass);


--
-- Name: partners id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.partners ALTER COLUMN id SET DEFAULT nextval('public.partners_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: product_price_history id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_price_history ALTER COLUMN id SET DEFAULT nextval('public.product_price_history_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: purchase_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items ALTER COLUMN id SET DEFAULT nextval('public.purchase_items_id_seq'::regclass);


--
-- Name: purchase_payments id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_payments ALTER COLUMN id SET DEFAULT nextval('public.purchase_payments_id_seq'::regclass);


--
-- Name: purchases id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchases ALTER COLUMN id SET DEFAULT nextval('public.purchases_id_seq'::regclass);


--
-- Name: reconciliation_lines id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.reconciliation_lines ALTER COLUMN id SET DEFAULT nextval('public.reconciliation_lines_id_seq'::regclass);


--
-- Name: repair_items id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_items ALTER COLUMN id SET DEFAULT nextval('public.repair_items_id_seq'::regclass);


--
-- Name: repair_orders id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_orders ALTER COLUMN id SET DEFAULT nextval('public.repair_orders_id_seq'::regclass);


--
-- Name: technicians id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.technicians ALTER COLUMN id SET DEFAULT nextval('public.technicians_id_seq'::regclass);


--
-- Name: treasury_transactions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions ALTER COLUMN id SET DEFAULT nextval('public.treasury_transactions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: wallet_transactions id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallet_transactions ALTER COLUMN id SET DEFAULT nextval('public.wallet_transactions_id_seq'::regclass);


--
-- Name: wallets id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallets ALTER COLUMN id SET DEFAULT nextval('public.wallets_id_seq'::regclass);


--
-- Name: warranties id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warranties ALTER COLUMN id SET DEFAULT nextval('public.warranties_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.alembic_version (version_num) FROM stdin;
da3bda880a96
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.audit_logs (id, user_id, company_id, action, entity_type, entity_id, old_values, new_values, ip_address, created_at) FROM stdin;
\.


--
-- Data for Name: bank_accounts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.bank_accounts (id, company_id, name, bank_name, account_number, account_type, currency, initial_balance, current_balance, is_active, branch_office, swift_code, routing_number, linked_account_id, created_at, updated_at) FROM stdin;
1	1	Cuenta Bancolombia 	bancolombia	91215735619	SAVINGS	COP	4679000.00	2381992.07	t	Nacional	\N	\N	9	2026-04-28 23:14:00.755461+00	2026-06-25 21:14:45.144885+00
\.


--
-- Data for Name: bank_reconciliations; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.bank_reconciliations (id, company_id, bank_account_id, statement_date, statement_balance, system_balance, outstanding_deposits, outstanding_checks, bank_fees_not_recorded, interest_not_recorded, adjusted_balance, is_balanced, status, reconciled_by, reconciled_at, notes, created_at) FROM stdin;
\.


--
-- Data for Name: cash_accounts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.cash_accounts (id, company_id, name, account_type, currency, initial_balance, current_balance, responsible_user_id, max_petty_cash_amount, is_active, linked_account_id, created_at, updated_at) FROM stdin;
1	1	Caja Principal	MAIN_CASH	COP	0.00	3855630.60	\N	\N	t	4	2026-05-04 23:34:54.444326+00	2026-06-25 21:49:38.887325+00
\.


--
-- Data for Name: chart_of_accounts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.chart_of_accounts (id, code, name, description, account_type, is_active, parent_id, company_id, created_at, updated_at) FROM stdin;
1	1000	ACTIVO	Total de activos	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
2	1100	ACTIVO CORRIENTE	Activos convertibles en efectivo dentro de un año	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
14	1120	Inversiones temporales	Inversiones a corto plazo	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
15	1130	Cuentas por cobrar	Derechos de cobro a clientes	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
16	1140	Inventarios	Mercancías para venta	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
17	1150	Gastos anticipados	Gastos pagados por anticipado	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
18	1200	ACTIVO NO CORRIENTE	Activos a largo plazo	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
19	1210	Propiedad, planta y equipo	Activos fijos	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
20	1220	Inversiones permanentes	Inversiones a largo plazo	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
21	1230	Intangibles	Activos intangibles	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
22	1240	Activos diferidos	Gastos diferidos a largo plazo	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
23	2000	PASIVO	Total de pasivos	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
24	2100	PASIVO CORRIENTE	Obligaciones a corto plazo	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
25	2110	Cuentas por pagar	Obligaciones con proveedores	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
26	2120	Documentos por pagar	Letras y pagarés	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
27	2130	Obligaciones fiscales	Impuestos por pagar	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
28	2140	Préstamos a corto plazo	Creditos vencibles en año	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
29	2150	Ingresos recibidos por anticipado	Anticipos de clientes	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
30	2200	PASIVO NO CORRIENTE	Obligaciones a largo plazo	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
31	2210	Préstamos a largo plazo	Creditos vencibles después de un año	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
32	2220	Bonos y obligaciones	Títulos de deuda	LIABILITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
33	3000	PATRIMONIO	Patrimonio de los propietarios	EQUITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
34	3100	Capital social	Aportes de los socios	EQUITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
35	3200	Reservas	Utilidades retenidas	EQUITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
36	3300	Utilidades del ejercicio	Ganancia o pérdida del periodo	EQUITY	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
37	4000	INGRESOS	Total de ingresos	REVENUE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
38	4100	Ingresos por ventas	Ventas de productos y servicios	REVENUE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
39	4200	Ingresos financieros	Intereses y ganancias cambiarias	REVENUE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
40	4300	Otros ingresos	Ingresos diversos	REVENUE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
41	5000	GASTOS	Total de gastos	EXPENSE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
43	5200	Gastos de administración	Gastos gerenciales	EXPENSE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
44	5300	Gastos de ventas	Gastos comerciales	EXPENSE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
45	5400	Gastos financieros	Intereses y comisiones	EXPENSE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
46	5500	Gastos por diferencial de cambio	Pérdidas cambiarias	EXPENSE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
47	5600	Otros gastos	Gastos diversos	EXPENSE	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
4	111001	Caja principal	Dinero en caja principal	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
5	111002	Caja menor	Fondo para gastos menores	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
6	111003	Caja registro #1	Caja de punto de venta 1	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
7	111004	Caja registro #2	Caja de punto de venta 2	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
62	2408	IVA descontable (soportado)	Impuesto sobre las ventas descontable en compras	LIABILITY	f	\N	1	2026-06-01 23:13:46.795681+00	2026-06-01 23:13:46.795681+00
9	111011	Bancos - Cuenta de ahorros	Cuentas de ahorro bancarias	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
10	111012	Bancos - Cta. moneda extranjera	Cuentas bancarias en moneda extranjera	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
11	111020	Cuentas por cobrar a terceros	Derechos de cobro a terceros	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
12	111030	Cheques en transito	Cheques emitidos no cobrados	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
13	111040	Depositos a termino	CDTs y depositos a plazo fijo	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
48	5105	Gastos de Personal	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
49	510506	Sueldos	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
50	5120	Arrendamientos	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
51	512010	Construcciones y Edificaciones (Arriendo)	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
52	5135	Servicios	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
53	513525	Acueducto y Alcantarillado	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
54	513530	Energía Eléctrica	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
55	513535	Teléfono	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
56	5145	Mantenimiento y Reparaciones	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
57	514510	Construcciones y Edificaciones (Mantenimiento)	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
58	514525	Equipo de Computación y Comunicación	\N	EXPENSE	t	\N	1	2026-04-30 22:25:32.474954+00	2026-04-30 22:25:32.474954+00
3	1110	Bancos (Transferencias)	Dinero en efectivo y equivalents	ASSET	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-30 22:44:15.588688+00
8	111010	Bancos - Cuenta Corriente	Cuentas corrientes bancarias	ASSET	t	3	1	2026-04-28 23:03:07.46712+00	2026-04-30 22:44:15.588688+00
61	2205	Proveedores	Cuentas por pagar a proveedores	LIABILITY	t	\N	1	2026-06-01 23:13:46.795681+00	2026-06-01 23:13:46.795681+00
63	6135	Costo de ventas	Costo directo de mercancías vendidas (PUC 6135)	COST	t	\N	1	2026-06-01 23:13:46.795681+00	2026-06-01 23:13:46.795681+00
42	5100	Costo de ventas	Costo directo de productos vendidos	COST	t	\N	1	2026-04-28 23:03:07.46712+00	2026-04-28 23:03:07.46712+00
\.


--
-- Data for Name: check_register; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.check_register (id, company_id, bank_account_id, check_number, payee, amount, issue_date, status, cleared_date, linked_transaction_id, notes, created_at) FROM stdin;
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.companies (id, name, nit, dv, legal_representative, address, phone, email, logo_url, regimen, fecha_inicio_actividades, resolucion_facturacion, is_active, created_at, updated_at) FROM stdin;
1	Evocomputo	98386016	0	German Alexander  Castillo	carrera 24 # 15-60 centro comercial San Agustín local 128	3103135881	germanc@evocomputo.com	/uploads/logos/e5ae9fdd-e535-4a56-ba81-0e2fffcc99a0.png	SIMPLE	2018-04-05	180607	t	2026-04-28 23:03:07.21998+00	2026-05-28 22:56:58.397297+00
\.


--
-- Data for Name: credit_debit_notes; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.credit_debit_notes (id, company_id, original_invoice_id, note_type, reason, amount, note_number, cufe, xml_ubl, estado_dian, fecha_envio_dian, motivo_rechazo, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: dian_billing_ranges; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.dian_billing_ranges (id, company_id, resolution, prefix, from_number, to_number, next_number, approval_date, expiration_date, is_active, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: fiscal_periods; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.fiscal_periods (id, company_id, start_date, end_date, is_closed, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: inventory_movements; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.inventory_movements (id, product_id, company_id, movement_type, quantity, reference, reference_id, reference_type, created_at) FROM stdin;
1	70	1	ADD	1.00	Purchase 3899	30	PURCHASE	2026-06-23 23:19:01.853825+00
2	76	1	ADD	1.00	Purchase 0001	32	PURCHASE	2026-06-25 20:47:52.230307+00
3	75	1	ADD	1.00	Purchase 0001	32	PURCHASE	2026-06-25 20:47:52.440912+00
4	77	1	ADD	1.00	Purchase 0001	32	PURCHASE	2026-06-25 20:47:52.487499+00
5	78	1	ADD	1.00	Purchase ATPE 100487	33	PURCHASE	2026-06-25 21:14:44.987082+00
\.


--
-- Data for Name: invoice_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.invoice_items (id, invoice_id, description, quantity, unit_price, discount, tax_rate, tax_amount, line_total, product_id, assembly_group_id, serial_number) FROM stdin;
1	1	portatil Hp Probook - Garantía 4 meses	1.00	750000.00	0.00	0.00	0.00	750000.00	7	\N	\N
2	2	Mantenimiento de hardware, cambio crema disipadora 	1.00	100000.00	0.00	0.00	0.00	100000.00	\N	\N	\N
3	2	Mantenimiento de software	1.00	50000.00	0.00	0.00	0.00	50000.00	\N	\N	\N
4	3	revision	1.00	0.00	0.00	0.00	0.00	0.00	\N	\N	\N
5	4	mantenimiento sistema de tinta continuo mas domicilio	1.00	72000.00	0.00	0.00	0.00	72000.00	\N	\N	\N
6	5	Teclado hp  HP ck0010la - Teclado hp  HP ck0010la	1.00	100000.00	0.00	0.00	0.00	100000.00	28	\N	\N
7	5	Instalación Teclado y mantenimiento, cambio pasta termica	1.00	40000.00	0.00	0.00	0.00	40000.00	\N	\N	\N
8	5	reparación bisagras y carcasa	1.00	80000.00	0.00	0.00	0.00	80000.00	\N	\N	\N
9	6	revisión, no  se reparo 	1.00	0.00	0.00	19.00	0.00	0.00	\N	\N	\N
11	8	 Servicio Reparación bisagras	1.00	80000.00	0.00	0.00	0.00	80000.00	\N	\N	\N
12	8	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH - UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	1.00	220000.00	0.00	0.00	0.00	220000.00	27	\N	\N
13	8	Instalación  SSD, Drivers y Software Ofimática	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
14	9	Mantenimiento de Hardware cambio pasta térmica	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
15	9	DDR4 4GB 3200MHZ PORTATIL SAMSUNG - DDR4 4GB 3200MHZ PORTATIL SAMSUNG	1.00	120000.00	0.00	0.00	0.00	120000.00	30	\N	\N
16	10	Reparación electrónica	1.00	180000.00	0.00	0.00	0.00	180000.00	\N	\N	\N
17	10	teclado repuesto Lenovo g4080	1.00	70000.00	0.00	0.00	0.00	70000.00	\N	\N	\N
18	11	mantenimiento de software	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
19	12	mantenimiento sistema impresión cabezal negro y color  	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
20	13	mantenimiento general 	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
21	14	se compra equipo	1.00	0.00	0.00	0.00	0.00	0.00	\N	\N	\N
22	15	reparación SOPORTE BISAGRAS	1.00	80000.00	0.00	0.00	0.00	80000.00	\N	\N	\N
23	16	Todo en uno Asus - Todo en uno Asus	1.00	700000.00	0.00	0.00	0.00	700000.00	2	\N	\N
24	17	instlacion office	1.00	70000.00	0.00	0.00	0.00	70000.00	\N	\N	\N
25	18	CABEZAL EPSON L - CABEZAL EPSON L	1.00	355000.00	0.00	0.00	0.00	355000.00	21	\N	\N
26	19	producto prueba - producto prueba	1.00	2.00	0.00	0.00	0.00	2.00	49	\N	000000001p
27	20	Instalación office y configuración correo PC y portátil	1.00	90000.00	0.00	0.00	0.00	90000.00	\N	\N	\N
28	21	reparación soporte bisagras  	1.00	80000.00	0.00	0.00	0.00	80000.00	\N	\N	\N
29	22	MANYENIMIENTO DE SOFTWARE	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
30	23	mantenimiento  sistema de tinta continua	1.00	70000.00	0.00	0.00	0.00	70000.00	\N	\N	\N
31	23	rellenado tinta magenta	1.00	10000.00	0.00	0.00	0.00	10000.00	\N	\N	\N
32	23	rellenado tinta yellow	1.00	10000.00	0.00	0.00	0.00	10000.00	\N	\N	\N
33	24	Mantenimiento y limpieza de cabezales obstruidos, sistema de tinta 	1.00	90000.00	0.00	0.00	0.00	90000.00	\N	\N	\N
34	25	revisión no se cobra	1.00	0.00	0.00	0.00	0.00	0.00	\N	\N	\N
35	26	PANTALLA 14.0 LED SLIM 30 PIN CONECTOR SUP INVERTI  - PANTALLA 14.0 LED SLIM 30 PIN CONECTOR SUP INVERTI 	1.00	450000.00	0.00	0.00	0.00	450000.00	41	\N	00003309
36	27	mantenimiento preventivo, cambio pasta térmica, termal pads	1.00	120000.00	0.00	0.00	0.00	120000.00	\N	\N	\N
37	28	mantenimiento de hardware, cambio pasta térmica, termal pads	1.00	120000.00	0.00	0.00	0.00	120000.00	\N	\N	\N
38	29	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH - UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	1.00	230000.00	0.00	0.00	0.00	230000.00	63	\N	AT422-256GBSATAIII25
39	29	Instalación SSD	1.00	50000.00	0.00	0.00	0.00	50000.00	\N	\N	\N
40	29	Mantenimiento correctivo	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
41	30	PORTATIL DELL CORE I5 DOCEAVA - PORTATIL DELL CORE I5 DOCEAVA	1.00	1200000.00	0.00	0.00	0.00	1200000.00	61	\N	000011212122
42	31	memoria RAM DDR3 4 GB USADA - memoria RAM DDR3 4 GB USADA	1.00	40000.00	0.00	0.00	0.00	40000.00	64	\N	0000023
43	32	mantenimiento, sistema de tinta continuo de tinta	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
44	33	ssd 250 gb mas mantenimiento 	1.00	300000.00	0.00	0.00	0.00	300000.00	\N	\N	\N
45	34	mantenimiento limpieza cabezal 	1.00	120000.00	0.00	0.00	0.00	120000.00	\N	\N	\N
46	35	mantenimiento de software	1.00	80000.00	0.00	0.00	0.00	80000.00	\N	\N	\N
47	36	Caja de Mantenimiento Epson L5590 - Caja de Mantenimiento Epson L5590	1.00	70000.00	0.00	0.00	0.00	70000.00	59	\N	0000011H
48	37	no se repraro	1.00	0.00	0.00	0.00	0.00	0.00	\N	\N	\N
49	38	mantenimiento de software	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
50	39	Servicio reparación electronica - Servicio reparación electronica	1.00	150000.00	0.00	0.00	0.00	150000.00	67	\N	0000023-1
51	40	Mantenimiento aire en el sistema 	1.00	50000.00	0.00	0.00	0.00	50000.00	\N	\N	\N
52	41	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH - UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	1.00	220000.00	0.00	0.00	0.00	220000.00	27	\N	421000249802
53	41	Servicio instalación SSD	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
54	42	Servicio instalación  office	1.00	70000.00	0.00	0.00	0.00	70000.00	\N	\N	\N
55	43	SERVICIO REPRACION ELECTRONICA LENOVO - SERVICIO REPRACION ELECTRONICA LENOVO	1.00	180000.00	0.00	0.00	0.00	180000.00	72	\N	0000000030
56	43	TECLADO LENOVO AIR 14 2020 - TECLADO LENOVO AIR 14 2020	1.00	110000.00	0.00	0.00	0.00	110000.00	70	\N	0000028
57	43	Servicio instalación teclado 	1.00	40000.00	0.00	0.00	0.00	40000.00	\N	\N	\N
58	44	reparación cargador Asus - reparación cargador Asus	1.00	40000.00	0.00	0.00	0.00	40000.00	74	\N	000000000032
59	44	Reparación electrónica portátil Asus - Reparación electrónica portátil Asus	1.00	180000.00	0.00	0.00	0.00	180000.00	73	\N	0000000031
60	44	Servicio recuperación información 	1.00	40000.00	0.00	0.00	0.00	40000.00	\N	\N	\N
61	45	Servicio  Mantenimiento  aire en el sistema	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
62	46	Servicio reset almohadillas	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
63	47	TINTA MAGENTA GYOCLCK - TINTA MAGENTA GYOCLCK	1.00	15000.00	0.00	0.00	0.00	15000.00	75	\N	000000040
64	47	TINTA YELLOW GIONCLICK - TINTA YELLOW GIONCLICK	1.00	14999.97	0.00	0.00	0.00	14999.97	77	\N	0000035
65	47	TINTA CYAN GIONCLICK - TINTA CYAN GIONCLICK	1.00	15000.00	0.00	0.00	0.00	15000.00	76	\N	000000035
66	47	Servicio Mantenimineto impresora	1.00	60000.00	0.00	0.00	0.00	60000.00	\N	\N	\N
67	48	SERVICIO MANTENIMINETO SOFTWARE	1.00	70000.00	0.00	0.00	0.00	70000.00	\N	\N	\N
68	49	Portatil ACER Aspire Core i5 cuarta generación - Portatil ACER Aspire Core i5 cuarta generación	1.00	600000.00	0.00	0.00	0.00	600000.00	62	\N	NXMXNAL0026030601E3400
69	50	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 512GB -550MB/s- ATTECH - UNIDAD DE ESTADO SOLIDO 2.5" SATA III 512GB -550MB/s- ATTECH	1.00	300000.00	0.00	0.00	0.00	300000.00	78	\N	AT422-512GBSATAIII25
70	51	Servicio mantenimiento de software pc escritorio	1.00	50000.00	0.00	0.00	0.00	50000.00	\N	\N	\N
\.


--
-- Data for Name: invoice_resolutions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.invoice_resolutions (id, company_id, resolution_type, resolution_number, prefix, start_number, end_number, current_number, start_date, end_date, is_active, created_at, updated_at) FROM stdin;
2	1	SALE	\N	INV-	1	\N	52	\N	\N	t	2026-04-30 20:42:28.842568+00	2026-06-25 21:49:38.887325+00
1	1	REPAIR	\N	REP-	1	\N	62	\N	\N	t	2026-04-29 20:04:14.728052+00	2026-06-27 19:33:33.579854+00
\.


--
-- Data for Name: invoices; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.invoices (id, invoice_number, invoice_type, partner_id, issue_date, due_date, total_amount, currency, status, cufe, xml_ubl, estado_dian, motivo_rechazo, company_id, created_at, updated_at) FROM stdin;
1	INV-00000001	SALE	5	2026-04-30 00:00:00+00	\N	750000.00	COP	CANCELLED	\N	\N	BORRADOR	\N	1	2026-04-30 20:42:28.842568+00	2026-05-04 23:33:27.274699+00
2	INV-00000002	SALE	8	2026-05-12 00:00:00+00	\N	150000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-12 21:03:22.313302+00	2026-05-12 21:03:22.313302+00
3	INV-00000003	SALE	4	2026-05-12 00:00:00+00	\N	0.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-12 21:43:06.067757+00	2026-05-12 21:43:06.067757+00
4	INV-00000004	SALE	6	2026-05-12 00:00:00+00	\N	72000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-12 21:44:29.190504+00	2026-05-12 21:44:29.190504+00
5	INV-00000005	SALE	7	2026-05-13 00:00:00+00	\N	220000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-13 22:32:20.303034+00	2026-05-13 22:32:20.303034+00
6	INV-00000006	SALE	12	2026-05-13 00:00:00+00	\N	0.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-13 23:12:05.617327+00	2026-05-13 23:12:05.617327+00
8	INV-00000008	SALE	14	2026-05-16 00:00:00+00	\N	360000.00	COP	DRAFT	\N	\N	BORRADOR	\N	1	2026-05-16 15:46:00.750432+00	2026-05-16 15:46:00.750432+00
9	INV-00000009	SALE	20	2026-05-16 00:00:00+00	\N	180000.00	COP	DRAFT	\N	\N	BORRADOR	\N	1	2026-05-16 16:57:11.187307+00	2026-05-16 16:57:11.187307+00
10	INV-00000010	SALE	26	2026-05-19 00:00:00+00	\N	250000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-19 20:25:41.250526+00	2026-05-19 20:25:41.250526+00
11	INV-00000011	SALE	21	2026-05-22 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-22 19:32:39.394987+00	2026-05-22 19:32:39.394987+00
12	INV-00000012	SALE	29	2026-05-22 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-22 21:51:03.78752+00	2026-05-22 21:51:03.78752+00
13	INV-00000013	SALE	19	2026-05-25 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-25 17:23:20.835918+00	2026-05-25 17:23:20.835918+00
14	INV-00000014	SALE	16	2026-05-25 00:00:00+00	\N	0.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-25 17:30:57.546509+00	2026-05-25 17:30:57.546509+00
15	INV-00000015	SALE	31	2026-05-26 00:00:00+00	\N	80000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-26 22:52:17.875806+00	2026-05-26 22:52:17.875806+00
16	INV-00000016	SALE	21	2026-05-26 00:00:00+00	\N	700000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-26 23:03:15.713308+00	2026-05-26 23:03:15.713308+00
17	INV-00000017	SALE	32	2026-05-26 00:00:00+00	\N	70000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-26 23:12:30.302116+00	2026-05-26 23:12:30.302116+00
18	INV-00000018	SALE	33	2026-05-27 00:00:00+00	\N	355000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-27 17:31:18.619975+00	2026-05-27 17:31:18.619975+00
19	INV-00000019	SALE	33	2026-05-27 00:00:00+00	\N	2.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-27 23:27:49.725861+00	2026-05-27 23:27:49.725861+00
20	INV-00000020	SALE	35	2026-05-28 00:00:00+00	\N	90000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-28 23:04:02.043629+00	2026-05-28 23:04:02.043629+00
21	INV-00000021	SALE	34	2026-05-28 00:00:00+00	\N	80000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-28 23:12:24.425524+00	2026-05-28 23:12:24.425524+00
22	INV-00000022	SALE	39	2026-05-30 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-05-30 17:23:03.286849+00	2026-05-30 17:23:03.286849+00
23	INV-00000023	SALE	38	2026-06-02 00:00:00+00	\N	90000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-02 22:21:01.936395+00	2026-06-02 22:21:01.936395+00
24	INV-00000024	SALE	51	2026-06-05 00:00:00+00	\N	90000.00	COP	DRAFT	\N	\N	BORRADOR	\N	1	2026-06-05 22:28:17.105524+00	2026-06-05 22:28:17.105524+00
25	INV-00000025	SALE	47	2026-06-05 00:00:00+00	\N	0.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-05 23:03:20.510616+00	2026-06-05 23:03:20.510616+00
26	INV-00000026	SALE	17	2026-06-06 00:00:00+00	\N	450000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-06 15:56:40.36728+00	2026-06-06 15:56:40.36728+00
27	INV-00000027	SALE	57	2026-06-17 00:00:00+00	\N	120000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-17 22:52:46.973801+00	2026-06-17 22:52:46.973801+00
28	INV-00000028	SALE	56	2026-06-17 00:00:00+00	\N	120000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-17 22:58:18.927884+00	2026-06-17 22:58:18.927884+00
29	INV-00000029	SALE	55	2026-06-17 00:00:00+00	\N	340000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-17 23:30:54.944943+00	2026-06-17 23:30:54.944943+00
30	INV-00000030	SALE	61	2026-06-18 00:00:00+00	\N	1200000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:21:31.352257+00	2026-06-18 14:21:31.352257+00
31	INV-00000031	SALE	62	2026-06-18 00:00:00+00	\N	40000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:26:15.930522+00	2026-06-18 14:26:15.930522+00
32	INV-00000032	SALE	24	2026-06-18 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:42:43.743057+00	2026-06-18 14:42:43.743057+00
33	INV-00000033	SALE	25	2026-06-18 00:00:00+00	\N	300000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:48:07.501685+00	2026-06-18 14:48:07.501685+00
34	INV-00000034	SALE	37	2026-06-18 00:00:00+00	\N	120000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:50:07.375028+00	2026-06-18 14:50:07.375028+00
35	INV-00000035	SALE	40	2026-06-18 00:00:00+00	\N	80000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:50:52.637048+00	2026-06-18 14:50:52.637048+00
36	INV-00000036	SALE	41	2026-06-18 00:00:00+00	\N	70000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 14:53:41.944169+00	2026-06-18 14:53:41.944169+00
37	INV-00000037	SALE	43	2026-06-18 00:00:00+00	\N	0.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 15:00:23.167782+00	2026-06-18 15:00:23.167782+00
38	INV-00000038	SALE	44	2026-06-18 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 15:01:07.967498+00	2026-06-18 15:01:07.967498+00
39	INV-00000039	SALE	45	2026-06-18 00:00:00+00	\N	150000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-18 15:06:55.888301+00	2026-06-18 15:06:55.888301+00
40	INV-00000040	SALE	60	2026-06-20 00:00:00+00	\N	50000.00	COP	DRAFT	\N	\N	BORRADOR	\N	1	2026-06-20 16:31:37.423216+00	2026-06-20 16:31:37.423216+00
41	INV-00000041	SALE	59	2026-06-20 00:00:00+00	\N	280000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-20 16:53:59.39482+00	2026-06-20 16:53:59.39482+00
42	INV-00000042	SALE	64	2026-06-20 00:00:00+00	\N	70000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-20 17:02:04.569884+00	2026-06-20 17:02:04.569884+00
43	INV-00000043	SALE	52	2026-06-24 00:00:00+00	\N	330000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-24 20:48:53.986409+00	2026-06-24 20:48:53.986409+00
44	INV-00000044	SALE	69	2026-06-24 00:00:00+00	\N	260000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-24 21:09:12.519302+00	2026-06-24 21:09:12.519302+00
45	INV-00000045	SALE	63	2026-06-24 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-24 21:17:44.04423+00	2026-06-24 21:17:44.04423+00
46	INV-00000046	SALE	70	2026-06-25 00:00:00+00	\N	60000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-25 20:34:53.911611+00	2026-06-25 20:34:53.911611+00
47	INV-00000047	SALE	72	2026-06-25 00:00:00+00	\N	104999.97	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-25 20:49:32.218383+00	2026-06-25 20:49:32.218383+00
48	INV-00000048	SALE	74	2026-06-25 00:00:00+00	\N	70000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-25 20:54:17.173165+00	2026-06-25 20:54:17.173165+00
49	INV-00000049	SALE	75	2026-06-25 00:00:00+00	\N	600000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-25 20:59:14.864093+00	2026-06-25 20:59:14.864093+00
50	INV-00000050	SALE	62	2026-06-25 00:00:00+00	\N	300000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-25 21:17:24.702376+00	2026-06-25 21:17:24.702376+00
51	INV-00000051	SALE	76	2026-06-25 00:00:00+00	\N	50000.00	COP	PAID	\N	\N	BORRADOR	\N	1	2026-06-25 21:49:38.887325+00	2026-06-25 21:49:38.887325+00
\.


--
-- Data for Name: journal_entries; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.journal_entries (id, entry_date, description, reference, is_posted, company_id, created_at, updated_at) FROM stdin;
1	2026-04-28 23:14:00.765623+00	Saldo inicial - bancolombia 91215735619	BA-OPEN-000001	t	1	2026-04-28 23:14:00.755461+00	2026-04-28 23:14:00.755461+00
2	2026-04-30 16:06:08.423928+00	Stock inicial producto - Todo en uno Asus (ID: 2)	SI-000002	t	1	2026-04-30 16:06:08.413166+00	2026-04-30 16:06:08.413166+00
3	2026-04-30 16:09:21.867332+00	Stock inicial producto - SSD NVE 512 GB Western Digita Usado  (ID: 3)	SI-000003	t	1	2026-04-30 16:09:21.86051+00	2026-04-30 16:09:21.86051+00
4	2026-04-30 16:18:07.179278+00	Stock inicial producto - Tarjeta de Video GT 710 2 GB (ID: 4)	SI-000004	t	1	2026-04-30 16:18:07.172824+00	2026-04-30 16:18:07.172824+00
5	2026-04-30 17:00:14.812128+00	Stock inicial producto - Memoria RAM DDR4 8 GB portatil usada (ID: 5)	SI-000005	t	1	2026-04-30 17:00:14.806758+00	2026-04-30 17:00:14.806758+00
6	2026-04-30 17:00:14.882514+00	Stock inicial producto - Memoria RAM DDR4 8 GB portatil usada (ID: 6)	SI-000006	t	1	2026-04-30 17:00:14.876978+00	2026-04-30 17:00:14.876978+00
7	2026-04-30 20:41:01.793184+00	Stock inicial producto - portatil Hp Probook (ID: 7)	SI-000007	t	1	2026-04-30 20:41:01.727659+00	2026-04-30 20:41:01.727659+00
8	2026-04-30 20:42:29.075751+00	Factura por INVOICE - Orden #1	INV-000001	t	1	2026-04-30 20:42:29.06761+00	2026-04-30 20:42:29.06761+00
9	2026-04-30 00:00:00+00	Mantenimiento locaciones	0001 Roberth	t	1	2026-04-30 23:04:56.439429+00	2026-04-30 23:06:29.552996+00
10	2026-05-02 19:39:00.146946+00	Stock inicial producto - Portatil asus Core i3 (ID: 8)	SI-000008	t	1	2026-05-02 19:39:00.087124+00	2026-05-02 19:39:00.087124+00
11	2026-05-02 19:58:15.812597+00	Stock inicial producto - Todo En UNO Lenovo (ID: 10)	SI-000010	t	1	2026-05-02 19:58:15.806111+00	2026-05-02 19:58:15.806111+00
12	2026-05-04 00:00:00+00	Pago deuda nu		t	1	2026-05-04 17:03:15.094578+00	2026-05-04 17:03:29.944708+00
13	2026-05-04 00:00:00+00	adelanto salario German	viaje	t	1	2026-05-04 19:46:55.427234+00	2026-05-04 19:47:03.109388+00
14	2026-05-04 23:33:27.232944+00	Anulación de Factura #INV-00000001	REV-INV-000001	t	1	2026-05-04 23:33:27.214797+00	2026-05-04 23:33:27.214797+00
15	2026-05-05 22:35:36.782866+00	Stock inicial producto - Toner HP generico 85A (ID: 12)	SI-000012	t	1	2026-05-05 22:35:36.664318+00	2026-05-05 22:35:36.664318+00
16	2026-05-05 23:15:17.681888+00	Stock inicial producto - Toner laser generico 85A (ID: 13)	SI-000013	t	1	2026-05-05 23:15:17.669528+00	2026-05-05 23:15:17.669528+00
17	2026-05-05 23:17:30.704096+00	 montoinicial		t	1	2026-05-05 23:17:30.698907+00	2026-05-05 23:17:30.698907+00
18	2026-05-05 23:19:14.241727+00	Stock inicial producto - Toner laser generico 85A 35A 36A (ID: 14)	SI-000014	t	1	2026-05-05 23:19:14.237973+00	2026-05-05 23:19:14.237973+00
20	2026-05-06 22:27:11.216725+00	abono a caja mayo 06		t	1	2026-05-06 22:27:11.210448+00	2026-05-06 22:27:11.210448+00
21	2026-05-12 21:03:22.530904+00	Factura por INVOICE - Orden #2	INV-000002	t	1	2026-05-12 21:03:22.510461+00	2026-05-12 21:03:22.510461+00
22	2026-05-05 00:00:00+00	pago Areriendo	Pago arriendo	t	1	2026-05-12 21:06:37.321241+00	2026-05-12 21:06:45.767644+00
23	2026-05-12 21:43:06.264494+00	Factura por INVOICE - Orden #3	INV-000003	t	1	2026-05-12 21:43:06.199985+00	2026-05-12 21:43:06.199985+00
24	2026-05-12 21:44:29.339059+00	Factura por INVOICE - Orden #4	INV-000004	t	1	2026-05-12 21:44:29.327297+00	2026-05-12 21:44:29.327297+00
25	2026-05-12 23:16:01.796654+00	Pago a proveedor - Factura ATPE 100220	Auto-ATPE 100220	t	1	2026-05-12 23:16:01.763085+00	2026-05-12 23:16:01.763085+00
26	2026-05-12 23:20:57.453063+00	Pago a proveedor - Factura tp00002	Auto-tp00002	t	1	2026-05-12 23:20:57.434635+00	2026-05-12 23:20:57.434635+00
27	2026-05-13 22:32:20.50064+00	Factura por INVOICE - Orden #5	INV-000005	t	1	2026-05-13 22:32:20.48595+00	2026-05-13 22:32:20.48595+00
28	2026-05-13 23:12:05.756415+00	Factura por INVOICE - Orden #6	INV-000006	t	1	2026-05-13 23:12:05.742495+00	2026-05-13 23:12:05.742495+00
29	2026-05-15 23:18:44.186876+00	Pago a proveedor - Factura 88357	Auto-88357	t	1	2026-05-15 23:18:44.162541+00	2026-05-15 23:18:44.162541+00
30	2026-05-15 23:21:01.135044+00	Factura por INVOICE - Orden #7	INV-000007	t	1	2026-05-15 23:21:01.123038+00	2026-05-15 23:21:01.123038+00
31	2026-05-16 15:46:00.938929+00	Factura por INVOICE - Orden #8	INV-000008	t	1	2026-05-16 15:46:00.926373+00	2026-05-16 15:46:00.926373+00
32	2026-05-16 16:57:11.359585+00	Factura por INVOICE - Orden #9	INV-000009	t	1	2026-05-16 16:57:11.34825+00	2026-05-16 16:57:11.34825+00
33	2026-05-19 20:25:41.379576+00	Factura por INVOICE - Orden #10	INV-000010	t	1	2026-05-19 20:25:41.367631+00	2026-05-19 20:25:41.367631+00
34	2026-05-19 22:41:34.710672+00	Stock inicial producto - SSD ADATA 250 GB (ID: 31)	SI-000031	t	1	2026-05-19 22:41:34.704111+00	2026-05-19 22:41:34.704111+00
36	2026-05-22 19:32:39.660036+00	Factura por INVOICE - Orden #11	INV-000011	t	1	2026-05-22 19:32:39.582485+00	2026-05-22 19:32:39.582485+00
37	2026-05-22 21:51:03.934576+00	Factura por INVOICE - Orden #12	INV-000012	t	1	2026-05-22 21:51:03.921764+00	2026-05-22 21:51:03.921764+00
38	2026-05-22 22:02:10.224571+00	Stock inicial producto - Portatil asus   (ID: 33)	SI-000033	t	1	2026-05-22 22:02:10.216695+00	2026-05-22 22:02:10.216695+00
40	2026-05-25 17:23:21.259868+00	Factura por INVOICE - Orden #13	INV-000013	t	1	2026-05-25 17:23:21.176596+00	2026-05-25 17:23:21.176596+00
41	2026-05-25 17:30:57.694922+00	Factura por INVOICE - Orden #14	INV-000014	t	1	2026-05-25 17:30:57.682337+00	2026-05-25 17:30:57.682337+00
42	2026-05-25 21:47:17.123469+00	Pago a proveedor - Factura FECO 66687	Auto-FECO 66687	t	1	2026-05-25 21:47:17.100429+00	2026-05-25 21:47:17.100429+00
43	2026-05-26 22:52:18.062429+00	Factura por INVOICE - Orden #15	INV-000015	t	1	2026-05-26 22:52:18.040642+00	2026-05-26 22:52:18.040642+00
44	2026-05-26 22:53:15.890014+00	PAGO FONDO COEMPRENDER	BANCOLOMBIA	t	1	2026-05-26 22:53:15.882287+00	2026-05-26 22:53:15.882287+00
45	2026-05-26 23:00:48.304452+00	ANTICIPO TODO EN UNO	WAL-2-3	t	1	2026-05-26 23:00:48.123389+00	2026-05-26 23:00:48.123389+00
46	2026-05-26 23:01:42.965056+00	DEVOLUCION	WAL-2-4	t	1	2026-05-26 23:01:42.95952+00	2026-05-26 23:01:42.95952+00
47	2026-05-26 23:03:15.894329+00	Factura por INVOICE - Orden #16	INV-000016	t	1	2026-05-26 23:03:15.881444+00	2026-05-26 23:03:15.881444+00
48	2026-05-26 23:12:30.448571+00	Factura por INVOICE - Orden #17	INV-000017	t	1	2026-05-26 23:12:30.435935+00	2026-05-26 23:12:30.435935+00
49	2026-05-27 00:00:00+00	pago internet	pago internet local	t	1	2026-05-27 17:06:43.605348+00	2026-05-27 17:07:06.73978+00
50	2026-05-27 17:31:18.847337+00	Factura por INVOICE - Orden #18	INV-000018	t	1	2026-05-27 17:31:18.826544+00	2026-05-27 17:31:18.826544+00
51	2026-05-27 23:27:12.244968+00	Stock inicial producto - producto prueba (ID: 49)	SI-000049	t	1	2026-05-27 23:27:12.222451+00	2026-05-27 23:27:12.222451+00
52	2026-05-27 23:27:49.915452+00	Factura por INVOICE - Orden #19	INV-000019	t	1	2026-05-27 23:27:49.899808+00	2026-05-27 23:27:49.899808+00
53	2026-05-28 23:04:02.203867+00	Factura por INVOICE - Orden #20	INV-000020	t	1	2026-05-28 23:04:02.184701+00	2026-05-28 23:04:02.184701+00
54	2026-05-28 23:12:24.569846+00	Factura por INVOICE - Orden #21	INV-000021	t	1	2026-05-28 23:12:24.556802+00	2026-05-28 23:12:24.556802+00
55	2026-05-30 17:23:03.426156+00	Factura por INVOICE - Orden #22	INV-000022	t	1	2026-05-30 17:23:03.413515+00	2026-05-30 17:23:03.413515+00
56	2026-06-01 23:17:45.444285+00	Compra a proveedor - Factura #24	CP-000024	t	1	2026-06-01 23:17:45.409245+00	2026-06-01 23:17:45.409245+00
57	2026-06-01 23:19:04.13339+00	Stock inicial producto - Teclado genérico usb (ID: 60)	SI-000060	t	1	2026-06-01 23:19:04.120758+00	2026-06-01 23:19:04.120758+00
58	2026-06-02 22:21:02.422952+00	Factura por INVOICE - Orden #23	INV-000023	t	1	2026-06-02 22:21:02.397895+00	2026-06-02 22:21:02.397895+00
59	2026-06-02 00:00:00+00	Pago servicio internet junio 2026		t	1	2026-06-02 23:20:53.097621+00	2026-06-02 23:21:05.861678+00
60	2026-06-02 00:00:00+00	Trasporte mensual		t	1	2026-06-02 23:26:13.546771+00	2026-06-02 23:26:21.270521+00
61	2026-06-05 22:28:17.187186+00	Factura por INVOICE - Orden #24	INV-000024	t	1	2026-06-05 22:28:17.175308+00	2026-06-05 22:28:17.175308+00
62	2026-06-05 23:03:20.88696+00	Factura por INVOICE - Orden #25	INV-000025	t	1	2026-06-05 23:03:20.875153+00	2026-06-05 23:03:20.875153+00
63	2026-06-06 15:56:40.533646+00	Factura por INVOICE - Orden #26	INV-000026	t	1	2026-06-06 15:56:40.520144+00	2026-06-06 15:56:40.520144+00
64	2026-06-05 00:00:00+00	pago arriendo local mes junio		t	1	2026-06-17 22:32:42.256082+00	2026-06-17 22:33:02.49837+00
65	2026-06-17 22:40:04.932668+00	Stock inicial producto - PORTATIL DELL CORE I5 DOCEAVA (ID: 61)	SI-000061	t	1	2026-06-17 22:40:04.808022+00	2026-06-17 22:40:04.808022+00
66	2026-06-17 22:52:47.630292+00	Factura por INVOICE - Orden #27	INV-000027	t	1	2026-06-17 22:52:47.613631+00	2026-06-17 22:52:47.613631+00
67	2026-06-17 22:58:19.072823+00	Factura por INVOICE - Orden #28	INV-000028	t	1	2026-06-17 22:58:19.060762+00	2026-06-17 22:58:19.060762+00
68	2026-06-17 23:03:29.954271+00	Stock inicial producto - Portatil ACER Aspire Core i5 cuarta generación (ID: 62)	SI-000062	t	1	2026-06-17 23:03:29.940954+00	2026-06-17 23:03:29.940954+00
69	2026-06-17 23:28:23.529156+00	Compra a proveedor - Factura #25	CP-000025	t	1	2026-06-17 23:28:23.523198+00	2026-06-17 23:28:23.523198+00
70	2026-06-17 23:28:23.56625+00	Pago a proveedor - Factura ATPE 100488	Auto-ATPE 100488	t	1	2026-06-17 23:28:23.558952+00	2026-06-17 23:28:23.558952+00
71	2026-06-17 23:30:55.138624+00	Factura por INVOICE - Orden #29	INV-000029	t	1	2026-06-17 23:30:55.121173+00	2026-06-17 23:30:55.121173+00
72	2026-06-18 14:13:04.524171+00	Compra a proveedor - Factura #26	CP-000026	t	1	2026-06-18 14:13:04.430302+00	2026-06-18 14:13:04.430302+00
73	2026-06-18 14:13:04.642782+00	Pago a proveedor - Factura 100508	Auto-100508	t	1	2026-06-18 14:13:04.624253+00	2026-06-18 14:13:04.624253+00
74	2026-06-18 14:21:31.591283+00	Factura por INVOICE - Orden #30	INV-000030	t	1	2026-06-18 14:21:31.576795+00	2026-06-18 14:21:31.576795+00
75	2026-06-18 14:25:00.105714+00	Stock inicial producto - memoria RAM DDR3 4 GB USADA (ID: 64)	SI-000064	t	1	2026-06-18 14:24:59.983314+00	2026-06-18 14:24:59.983314+00
85	2026-06-18 15:01:08.10911+00	Factura por INVOICE - Orden #38	INV-000038	t	1	2026-06-18 15:01:08.097229+00	2026-06-18 15:01:08.097229+00
76	2026-06-18 14:26:16.116092+00	Factura por INVOICE - Orden #31	INV-000031	t	1	2026-06-18 14:26:16.10438+00	2026-06-18 14:26:16.10438+00
77	2026-06-18 14:42:43.891092+00	Factura por INVOICE - Orden #32	INV-000032	t	1	2026-06-18 14:42:43.875931+00	2026-06-18 14:42:43.875931+00
78	2026-06-18 14:48:07.650537+00	Factura por INVOICE - Orden #33	INV-000033	t	1	2026-06-18 14:48:07.637794+00	2026-06-18 14:48:07.637794+00
79	2026-06-18 14:50:07.524376+00	Factura por INVOICE - Orden #34	INV-000034	t	1	2026-06-18 14:50:07.511664+00	2026-06-18 14:50:07.511664+00
80	2026-06-18 14:50:52.781682+00	Factura por INVOICE - Orden #35	INV-000035	t	1	2026-06-18 14:50:52.769959+00	2026-06-18 14:50:52.769959+00
81	2026-06-18 14:52:52.699477+00	Pago a proveedor - Factura SI-PUR-1780355865-59		t	1	2026-06-18 14:52:52.685328+00	2026-06-18 14:52:52.685328+00
82	2026-06-18 14:53:42.169574+00	Factura por INVOICE - Orden #36	INV-000036	t	1	2026-06-18 14:53:42.158038+00	2026-06-18 14:53:42.158038+00
83	2026-06-18 14:59:25.976612+00	Compra a proveedor - Factura #27	CP-000027	t	1	2026-06-18 14:59:25.955792+00	2026-06-18 14:59:25.955792+00
84	2026-06-18 15:00:23.309457+00	Factura por INVOICE - Orden #37	INV-000037	t	1	2026-06-18 15:00:23.297722+00	2026-06-18 15:00:23.297722+00
86	2026-06-18 15:04:36.759114+00	Stock inicial producto - Servicio reparación electronica (ID: 67)	SI-000067	t	1	2026-06-18 15:04:36.745471+00	2026-06-18 15:04:36.745471+00
87	2026-06-18 15:06:56.060049+00	Factura por INVOICE - Orden #39	INV-000039	t	1	2026-06-18 15:06:56.048588+00	2026-06-18 15:06:56.048588+00
89	2026-06-20 16:53:59.568344+00	Factura por INVOICE - Orden #41	INV-000041	t	1	2026-06-20 16:53:59.554485+00	2026-06-20 16:53:59.554485+00
90	2026-06-20 17:02:04.711635+00	Factura por INVOICE - Orden #42	INV-000042	t	1	2026-06-20 17:02:04.70278+00	2026-06-20 17:02:04.70278+00
88	2026-06-20 16:31:37.552037+00	Factura por INVOICE - Orden #40	INV-000040	t	1	2026-06-20 16:31:37.540198+00	2026-06-20 16:31:37.540198+00
91	2026-06-23 22:07:52.960218+00	Pago a proveedor - Factura SI-PUR-1781794765-65		t	1	2026-06-23 22:07:52.940222+00	2026-06-23 22:07:52.940222+00
92	2026-06-23 23:19:01.969934+00	Compra a proveedor - Factura #30	CP-000030	t	1	2026-06-23 23:19:01.95306+00	2026-06-23 23:19:01.95306+00
93	2026-06-23 23:19:02.030096+00	Pago a proveedor - Factura 3899	Auto-3899	t	1	2026-06-23 23:19:02.011844+00	2026-06-23 23:19:02.011844+00
94	2026-06-23 23:24:11.886149+00	Stock inicial producto - SERVICIO REPRACION ELECTRONICA LENOVO (ID: 71)	SI-000071	t	1	2026-06-23 23:24:11.871288+00	2026-06-23 23:24:11.871288+00
95	2026-06-23 23:26:44.187247+00	Compra a proveedor - Factura #31	CP-000031	t	1	2026-06-23 23:26:44.162809+00	2026-06-23 23:26:44.162809+00
96	2026-06-24 20:48:54.098022+00	Factura por INVOICE - Orden #43	INV-000043	t	1	2026-06-24 20:48:53.986409+00	2026-06-24 20:48:53.986409+00
97	2026-06-24 21:01:26.043455+00	Stock inicial producto - Reparación electrónica portátil Asus (ID: 73)	SI-000073	t	1	2026-06-24 21:01:25.90794+00	2026-06-24 21:01:25.90794+00
98	2026-06-24 21:04:21.33034+00	Stock inicial producto - reparación cargador Asus (ID: 74)	SI-000074	t	1	2026-06-24 21:04:21.315474+00	2026-06-24 21:04:21.315474+00
99	2026-06-24 21:09:12.537241+00	Factura por INVOICE - Orden #44	INV-000044	t	1	2026-06-24 21:09:12.519302+00	2026-06-24 21:09:12.519302+00
100	2026-06-24 21:17:44.062557+00	Factura por INVOICE - Orden #45	INV-000045	t	1	2026-06-24 21:17:44.04423+00	2026-06-24 21:17:44.04423+00
102	2026-06-23 00:00:00+00	Pago Salud y pension		t	1	2026-06-24 22:18:10.652307+00	2026-06-24 22:18:24.419791+00
103	2026-06-24 00:00:00+00	gimnasio santiago		t	1	2026-06-25 20:30:05.494127+00	2026-06-25 20:30:40.590274+00
104	2026-06-16 00:00:00+00	gastos varios casa		t	1	2026-06-25 20:33:09.051354+00	2026-06-25 20:33:18.291295+00
105	2026-06-25 20:34:53.937536+00	Factura por INVOICE - Orden #46	INV-000046	t	1	2026-06-25 20:34:53.911611+00	2026-06-25 20:34:53.911611+00
106	2026-06-25 20:47:52.534043+00	Compra a proveedor - Factura #32	CP-000032	t	1	2026-06-25 20:47:52.523164+00	2026-06-25 20:47:52.523164+00
107	2026-06-25 20:47:52.586798+00	Pago a proveedor - Factura 0001	Auto-0001	t	1	2026-06-25 20:47:52.570064+00	2026-06-25 20:47:52.570064+00
108	2026-06-25 20:49:32.237534+00	Factura por INVOICE - Orden #47	INV-000047	t	1	2026-06-25 20:49:32.218383+00	2026-06-25 20:49:32.218383+00
109	2026-06-25 20:54:17.19076+00	Factura por INVOICE - Orden #48	INV-000048	t	1	2026-06-25 20:54:17.173165+00	2026-06-25 20:54:17.173165+00
110	2026-06-25 20:59:14.881045+00	Factura por INVOICE - Orden #49	INV-000049	t	1	2026-06-25 20:59:14.864093+00	2026-06-25 20:59:14.864093+00
111	2026-06-25 21:14:45.0858+00	Compra a proveedor - Factura #33	CP-000033	t	1	2026-06-25 21:14:45.074926+00	2026-06-25 21:14:45.074926+00
112	2026-06-25 21:14:45.154617+00	Pago a proveedor - Factura ATPE 100487	Auto-ATPE 100487	t	1	2026-06-25 21:14:45.144885+00	2026-06-25 21:14:45.144885+00
113	2026-06-25 21:17:24.718657+00	Factura por INVOICE - Orden #50	INV-000050	t	1	2026-06-25 21:17:24.702376+00	2026-06-25 21:17:24.702376+00
114	2026-06-25 21:49:38.904534+00	Factura por INVOICE - Orden #51	INV-000051	t	1	2026-06-25 21:49:38.887325+00	2026-06-25 21:49:38.887325+00
\.


--
-- Data for Name: journal_entry_lines; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.journal_entry_lines (id, journal_entry_id, account_id, debit_amount, credit_amount, description, created_at) FROM stdin;
1	1	9	4679000.00	0.00	Saldo inicial cuenta bancaria	2026-04-28 23:14:00.755461+00
2	1	9	0.00	4679000.00	Contra partida saldo inicial	2026-04-28 23:14:00.755461+00
3	2	16	280000.00	0.00	Inventarios - Stock inicial Todo en uno Asus	2026-04-30 16:06:08.413166+00
4	2	4	0.00	280000.00	Pago stock inicial - CASH	2026-04-30 16:06:08.413166+00
5	3	16	50000.00	0.00	Inventarios - Stock inicial SSD NVE 512 GB Western Digita Usado 	2026-04-30 16:09:21.86051+00
6	3	4	0.00	50000.00	Pago stock inicial - CASH	2026-04-30 16:09:21.86051+00
7	4	16	50000.00	0.00	Inventarios - Stock inicial Tarjeta de Video GT 710 2 GB	2026-04-30 16:18:07.172824+00
8	4	4	0.00	50000.00	Pago stock inicial - CASH	2026-04-30 16:18:07.172824+00
9	5	16	50000.00	0.00	Inventarios - Stock inicial Memoria RAM DDR4 8 GB portatil usada	2026-04-30 17:00:14.806758+00
10	5	4	0.00	50000.00	Pago stock inicial - CASH	2026-04-30 17:00:14.806758+00
11	6	16	50000.00	0.00	Inventarios - Stock inicial Memoria RAM DDR4 8 GB portatil usada	2026-04-30 17:00:14.876978+00
12	6	4	0.00	50000.00	Pago stock inicial - CASH	2026-04-30 17:00:14.876978+00
13	7	16	250000.00	0.00	Inventarios - Stock inicial portatil Hp Probook	2026-04-30 20:41:01.727659+00
14	7	4	0.00	250000.00	Pago stock inicial - CASH	2026-04-30 20:41:01.727659+00
15	8	15	750000.00	0.00	Cuentas por cobrar - Factura INV-000001	2026-04-30 20:42:29.06761+00
16	8	38	0.00	750000.00	Ingresos por servicios - Régimen Simple	2026-04-30 20:42:29.06761+00
17	9	57	700000.00	0.00	gasto	2026-04-30 23:04:56.439429+00
18	9	3	0.00	700000.00	dinero por mantenimineto 	2026-04-30 23:04:56.439429+00
19	10	16	180000.00	0.00	Inventarios - Stock inicial Portatil asus Core i3	2026-05-02 19:39:00.087124+00
20	10	4	0.00	180000.00	Pago stock inicial - CASH	2026-05-02 19:39:00.087124+00
21	11	16	300000.00	0.00	Inventarios - Stock inicial Todo En UNO Lenovo	2026-05-02 19:58:15.806111+00
22	11	4	0.00	300000.00	Pago stock inicial - CASH	2026-05-02 19:58:15.806111+00
23	12	25	320000.00	0.00	pago NU	2026-05-04 17:03:15.094578+00
24	12	3	0.00	320000.00	pago nu	2026-05-04 17:03:15.094578+00
25	13	25	300000.00	0.00	adelanto salario German	2026-05-04 19:46:55.427234+00
26	13	3	0.00	300000.00	pago adelanto german	2026-05-04 19:46:55.427234+00
27	14	15	0.00	750000.00	Reversión: Cuentas por cobrar - Factura INV-000001	2026-05-04 23:33:27.214797+00
28	14	38	750000.00	0.00	Reversión: Ingresos por servicios - Régimen Simple	2026-05-04 23:33:27.214797+00
29	15	16	25000.00	0.00	Inventarios - Stock inicial Toner HP generico 85A	2026-05-05 22:35:36.664318+00
30	15	4	0.00	25000.00	Pago stock inicial - CASH	2026-05-05 22:35:36.664318+00
31	16	16	25000.00	0.00	Inventarios - Stock inicial Toner laser generico 85A	2026-05-05 23:15:17.669528+00
32	16	4	0.00	25000.00	Pago stock inicial - CASH	2026-05-05 23:15:17.669528+00
33	17	4	100000.00	0.00	Ingreso caja - Caja Principal	2026-05-05 23:17:30.698907+00
34	17	4	0.00	100000.00	Contra partida	2026-05-05 23:17:30.698907+00
35	18	16	25000.00	0.00	Inventarios - Stock inicial Toner laser generico 85A 35A 36A	2026-05-05 23:19:14.237973+00
36	18	4	0.00	25000.00	Pago stock inicial - CASH	2026-05-05 23:19:14.237973+00
39	20	4	2000000.00	0.00	Ingreso caja - Caja Principal	2026-05-06 22:27:11.210448+00
40	20	4	0.00	2000000.00	Contra partida	2026-05-06 22:27:11.210448+00
41	21	15	150000.00	0.00	Cuentas por cobrar - Factura INV-000002	2026-05-12 21:03:22.510461+00
42	21	38	0.00	150000.00	Ingresos por servicios - Régimen Simple	2026-05-12 21:03:22.510461+00
43	21	15	0.00	150000.00	Recaudo - Factura INV-000002	2026-05-12 21:03:22.510461+00
44	21	4	150000.00	0.00	Ingreso de dinero - CASH	2026-05-12 21:03:22.510461+00
45	22	41	900000.00	0.00	pago arriendo	2026-05-12 21:06:37.321241+00
46	22	3	0.00	900000.00	pago arriendo	2026-05-12 21:06:37.321241+00
47	23	15	0.00	0.00	Cuentas por cobrar - Factura INV-000003	2026-05-12 21:43:06.199985+00
48	23	38	0.00	0.00	Ingresos por servicios - Régimen Simple	2026-05-12 21:43:06.199985+00
49	23	15	0.00	0.00	Recaudo - Factura INV-000003	2026-05-12 21:43:06.199985+00
50	23	4	0.00	0.00	Ingreso de dinero - CASH	2026-05-12 21:43:06.199985+00
51	24	15	72000.00	0.00	Cuentas por cobrar - Factura INV-000004	2026-05-12 21:44:29.327297+00
52	24	38	0.00	72000.00	Ingresos por servicios - Régimen Simple	2026-05-12 21:44:29.327297+00
53	24	15	0.00	72000.00	Recaudo - Factura INV-000004	2026-05-12 21:44:29.327297+00
54	24	4	72000.00	0.00	Ingreso de dinero - CASH	2026-05-12 21:44:29.327297+00
55	25	45	158823.00	0.00	Retiro - Pago a proveedor - Factura ATPE 100220	2026-05-12 23:16:01.763085+00
56	25	4	0.00	158823.00	Salida de CASH	2026-05-12 23:16:01.763085+00
57	26	45	75000.00	0.00	Retiro - Pago a proveedor - Factura tp00002	2026-05-12 23:20:57.434635+00
58	26	4	0.00	75000.00	Salida de CASH	2026-05-12 23:20:57.434635+00
59	27	15	220000.00	0.00	Cuentas por cobrar - Factura INV-000005	2026-05-13 22:32:20.48595+00
60	27	38	0.00	220000.00	Ingresos por servicios - Régimen Simple	2026-05-13 22:32:20.48595+00
61	27	15	0.00	220000.00	Recaudo - Factura INV-000005	2026-05-13 22:32:20.48595+00
62	27	8	220000.00	0.00	Ingreso de dinero - TRANSFER	2026-05-13 22:32:20.48595+00
63	28	15	0.00	0.00	Cuentas por cobrar - Factura INV-000006	2026-05-13 23:12:05.742495+00
64	28	38	0.00	0.00	Ingresos por servicios - Régimen Simple	2026-05-13 23:12:05.742495+00
65	28	15	0.00	0.00	Recaudo - Factura INV-000006	2026-05-13 23:12:05.742495+00
66	28	4	0.00	0.00	Ingreso de dinero - CASH	2026-05-13 23:12:05.742495+00
67	29	45	1899000.00	0.00	Retiro - Pago a proveedor - Factura 88357	2026-05-15 23:18:44.162541+00
68	29	9	0.00	1899000.00	Salida de BANK	2026-05-15 23:18:44.162541+00
69	30	15	2100000.00	0.00	Cuentas por cobrar - Factura INV-000007	2026-05-15 23:21:01.123038+00
70	30	38	0.00	2100000.00	Ingresos por servicios - Régimen Simple	2026-05-15 23:21:01.123038+00
71	31	15	360000.00	0.00	Cuentas por cobrar - Factura INV-000008	2026-05-16 15:46:00.926373+00
72	31	38	0.00	360000.00	Ingresos por servicios - Régimen Simple	2026-05-16 15:46:00.926373+00
73	32	15	180000.00	0.00	Cuentas por cobrar - Factura INV-000009	2026-05-16 16:57:11.34825+00
74	32	38	0.00	180000.00	Ingresos por servicios - Régimen Simple	2026-05-16 16:57:11.34825+00
75	33	15	250000.00	0.00	Cuentas por cobrar - Factura INV-000010	2026-05-19 20:25:41.367631+00
76	33	38	0.00	250000.00	Ingresos por servicios - Régimen Simple	2026-05-19 20:25:41.367631+00
77	33	15	0.00	250000.00	Recaudo - Factura INV-000010	2026-05-19 20:25:41.367631+00
78	33	4	250000.00	0.00	Ingreso de dinero - CASH	2026-05-19 20:25:41.367631+00
79	34	16	180000.00	0.00	Inventarios - Stock inicial SSD ADATA 250 GB	2026-05-19 22:41:34.704111+00
80	34	4	0.00	180000.00	Pago stock inicial - CASH	2026-05-19 22:41:34.704111+00
83	36	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000011	2026-05-22 19:32:39.582485+00
84	36	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-05-22 19:32:39.582485+00
85	36	15	0.00	60000.00	Recaudo - Factura INV-000011	2026-05-22 19:32:39.582485+00
86	36	8	60000.00	0.00	Ingreso de dinero - TRANSFER	2026-05-22 19:32:39.582485+00
87	37	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000012	2026-05-22 21:51:03.921764+00
88	37	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-05-22 21:51:03.921764+00
89	37	15	0.00	60000.00	Recaudo - Factura INV-000012	2026-05-22 21:51:03.921764+00
90	37	8	60000.00	0.00	Ingreso de dinero - TRANSFER	2026-05-22 21:51:03.921764+00
91	38	16	480000.00	0.00	Inventarios - Stock inicial Portatil asus  	2026-05-22 22:02:10.216695+00
92	38	8	0.00	480000.00	Pago stock inicial - BANK_TRANSFER	2026-05-22 22:02:10.216695+00
95	40	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000013	2026-05-25 17:23:21.176596+00
96	40	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-05-25 17:23:21.176596+00
97	40	15	0.00	60000.00	Recaudo - Factura INV-000013	2026-05-25 17:23:21.176596+00
98	40	4	60000.00	0.00	Ingreso de dinero - CASH	2026-05-25 17:23:21.176596+00
99	41	15	0.00	0.00	Cuentas por cobrar - Factura INV-000014	2026-05-25 17:30:57.682337+00
100	41	38	0.00	0.00	Ingresos por servicios - Régimen Simple	2026-05-25 17:30:57.682337+00
101	42	45	436548.00	0.00	Retiro - Pago a proveedor - Factura FECO 66687	2026-05-25 21:47:17.100429+00
102	42	4	0.00	436548.00	Salida de CASH	2026-05-25 21:47:17.100429+00
103	43	15	80000.00	0.00	Cuentas por cobrar - Factura INV-000015	2026-05-26 22:52:18.040642+00
104	43	38	0.00	80000.00	Ingresos por servicios - Régimen Simple	2026-05-26 22:52:18.040642+00
105	43	15	0.00	80000.00	Recaudo - Factura INV-000015	2026-05-26 22:52:18.040642+00
106	43	4	80000.00	0.00	Ingreso de dinero - CASH	2026-05-26 22:52:18.040642+00
107	44	9	2200000.00	0.00	Deposito - Cuenta Bancolombia 	2026-05-26 22:53:15.882287+00
108	44	4	0.00	2200000.00	Contra partida deposito	2026-05-26 22:53:15.882287+00
109	45	9	3000000.00	0.00	Ingreso de dinero - Monedero	2026-05-26 23:00:48.123389+00
110	45	29	0.00	3000000.00	Anticipo de cliente	2026-05-26 23:00:48.123389+00
111	46	29	2700000.00	0.00	Retiro de anticipo - Monedero	2026-05-26 23:01:42.95952+00
112	46	9	0.00	2700000.00	Salida de dinero	2026-05-26 23:01:42.95952+00
113	47	15	700000.00	0.00	Cuentas por cobrar - Factura INV-000016	2026-05-26 23:03:15.881444+00
114	47	38	0.00	700000.00	Ingresos por servicios - Régimen Simple	2026-05-26 23:03:15.881444+00
115	47	15	0.00	300000.00	Recaudo con monedero - Factura INV-000016	2026-05-26 23:03:15.881444+00
116	47	29	300000.00	0.00	Aplicación de anticipo - Monedero	2026-05-26 23:03:15.881444+00
117	47	15	0.00	400000.00	Recaudo - Factura INV-000016	2026-05-26 23:03:15.881444+00
118	47	4	400000.00	0.00	Ingreso de dinero - CASH	2026-05-26 23:03:15.881444+00
119	48	15	70000.00	0.00	Cuentas por cobrar - Factura INV-000017	2026-05-26 23:12:30.435935+00
120	48	38	0.00	70000.00	Ingresos por servicios - Régimen Simple	2026-05-26 23:12:30.435935+00
121	48	15	0.00	70000.00	Recaudo - Factura INV-000017	2026-05-26 23:12:30.435935+00
122	48	4	70000.00	0.00	Ingreso de dinero - CASH	2026-05-26 23:12:30.435935+00
123	49	4	90000.00	0.00	pago internet	2026-05-27 17:06:43.605348+00
124	49	4	0.00	90000.00	pago interner	2026-05-27 17:06:43.605348+00
125	50	15	355000.00	0.00	Cuentas por cobrar - Factura INV-000018	2026-05-27 17:31:18.826544+00
126	50	38	0.00	355000.00	Ingresos por servicios - Régimen Simple	2026-05-27 17:31:18.826544+00
127	50	15	0.00	355000.00	Recaudo - Factura INV-000018	2026-05-27 17:31:18.826544+00
128	50	8	355000.00	0.00	Ingreso de dinero - TRANSFER	2026-05-27 17:31:18.826544+00
129	51	16	1.00	0.00	Inventarios - Stock inicial producto prueba	2026-05-27 23:27:12.222451+00
130	51	4	0.00	1.00	Pago stock inicial - CASH	2026-05-27 23:27:12.222451+00
131	52	15	2.00	0.00	Cuentas por cobrar - Factura INV-000019	2026-05-27 23:27:49.899808+00
132	52	38	0.00	2.00	Ingresos por servicios - Régimen Simple	2026-05-27 23:27:49.899808+00
133	52	15	0.00	2.00	Recaudo - Factura INV-000019	2026-05-27 23:27:49.899808+00
134	52	4	2.00	0.00	Ingreso de dinero - CASH	2026-05-27 23:27:49.899808+00
135	53	15	90000.00	0.00	Cuentas por cobrar - Factura INV-000020	2026-05-28 23:04:02.184701+00
136	53	38	0.00	90000.00	Ingresos por servicios - Régimen Simple	2026-05-28 23:04:02.184701+00
137	53	15	0.00	90000.00	Recaudo - Factura INV-000020	2026-05-28 23:04:02.184701+00
138	53	4	90000.00	0.00	Ingreso de dinero - CASH	2026-05-28 23:04:02.184701+00
139	54	15	80000.00	0.00	Cuentas por cobrar - Factura INV-000021	2026-05-28 23:12:24.556802+00
140	54	38	0.00	80000.00	Ingresos por servicios - Régimen Simple	2026-05-28 23:12:24.556802+00
141	54	15	0.00	80000.00	Recaudo - Factura INV-000021	2026-05-28 23:12:24.556802+00
142	54	4	80000.00	0.00	Ingreso de dinero - CASH	2026-05-28 23:12:24.556802+00
143	55	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000022	2026-05-30 17:23:03.413515+00
144	55	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-05-30 17:23:03.413515+00
145	55	15	0.00	60000.00	Recaudo - Factura INV-000022	2026-05-30 17:23:03.413515+00
146	55	4	60000.00	0.00	Ingreso de dinero - CASH	2026-05-30 17:23:03.413515+00
147	56	16	50000.00	0.00	Inventarios - Compra CP-000024	2026-06-01 23:17:45.409245+00
148	56	4	0.00	50000.00	Pago a proveedor - Compra CP-000024	2026-06-01 23:17:45.409245+00
149	57	16	20000.00	0.00	Inventarios - Stock inicial Teclado genérico usb	2026-06-01 23:19:04.120758+00
150	57	4	0.00	20000.00	Pago stock inicial - CASH	2026-06-01 23:19:04.120758+00
151	58	15	90000.00	0.00	Cuentas por cobrar - Factura INV-000023	2026-06-02 22:21:02.397895+00
152	58	38	0.00	90000.00	Ingresos por servicios - Régimen Simple	2026-06-02 22:21:02.397895+00
153	58	15	0.00	90000.00	Recaudo - Factura INV-000023	2026-06-02 22:21:02.397895+00
154	58	4	90000.00	0.00	Ingreso de dinero - CASH	2026-06-02 22:21:02.397895+00
155	59	43	90000.00	0.00	pago internet	2026-06-02 23:20:53.097621+00
156	59	9	0.00	90000.00	pago internet	2026-06-02 23:20:53.097621+00
157	60	47	237000.00	0.00	pago trasporte	2026-06-02 23:26:13.546771+00
158	60	4	0.00	237000.00	pago trasporte	2026-06-02 23:26:13.546771+00
159	61	15	90000.00	0.00	Cuentas por cobrar - Factura INV-000024	2026-06-05 22:28:17.175308+00
160	61	38	0.00	90000.00	Ingresos por servicios - Régimen Simple	2026-06-05 22:28:17.175308+00
161	62	15	0.00	0.00	Cuentas por cobrar - Factura INV-000025	2026-06-05 23:03:20.875153+00
162	62	38	0.00	0.00	Ingresos por servicios - Régimen Simple	2026-06-05 23:03:20.875153+00
163	63	15	450000.00	0.00	Cuentas por cobrar - Factura INV-000026	2026-06-06 15:56:40.520144+00
164	63	38	0.00	450000.00	Ingresos por servicios - Régimen Simple	2026-06-06 15:56:40.520144+00
165	63	15	0.00	450000.00	Recaudo - Factura INV-000026	2026-06-06 15:56:40.520144+00
166	63	4	450000.00	0.00	Ingreso de dinero - CASH	2026-06-06 15:56:40.520144+00
167	63	63	260504.00	0.00	Costo de ventas - Factura INV-000026	2026-06-06 15:56:40.520144+00
168	63	16	0.00	260504.00	Salida de inventario - Factura INV-000026	2026-06-06 15:56:40.520144+00
169	64	50	920000.00	0.00	pago arriendo local	2026-06-17 22:32:42.256082+00
170	64	9	0.00	920000.00	pago arriendo local	2026-06-17 22:32:42.256082+00
171	65	16	400000.00	0.00	Inventarios - Stock inicial PORTATIL DELL CORE I5 DOCEAVA	2026-06-17 22:40:04.808022+00
172	65	8	0.00	400000.00	Pago stock inicial - BANK_TRANSFER	2026-06-17 22:40:04.808022+00
173	66	15	120000.00	0.00	Cuentas por cobrar - Factura INV-000027	2026-06-17 22:52:47.613631+00
174	66	38	0.00	120000.00	Ingresos por servicios - Régimen Simple	2026-06-17 22:52:47.613631+00
175	66	15	0.00	120000.00	Recaudo - Factura INV-000027	2026-06-17 22:52:47.613631+00
176	66	8	120000.00	0.00	Ingreso de dinero - TRANSFER	2026-06-17 22:52:47.613631+00
177	67	15	120000.00	0.00	Cuentas por cobrar - Factura INV-000028	2026-06-17 22:58:19.060762+00
178	67	38	0.00	120000.00	Ingresos por servicios - Régimen Simple	2026-06-17 22:58:19.060762+00
179	67	15	0.00	120000.00	Recaudo - Factura INV-000028	2026-06-17 22:58:19.060762+00
180	67	4	120000.00	0.00	Ingreso de dinero - CASH	2026-06-17 22:58:19.060762+00
181	68	16	220000.00	0.00	Inventarios - Stock inicial Portatil ACER Aspire Core i5 cuarta generación	2026-06-17 23:03:29.940954+00
182	68	8	0.00	220000.00	Pago stock inicial - BANK_TRANSFER	2026-06-17 23:03:29.940954+00
185	70	45	188020.00	0.00	Retiro - Pago a proveedor - Factura ATPE 100488	2026-06-17 23:28:23.558952+00
186	70	9	0.00	188020.00	Salida de BANK	2026-06-17 23:28:23.558952+00
183	69	16	188020.00	0.00	Inventarios - Compra CP-000025	2026-06-17 23:28:23.523198+00
184	69	8	0.00	188020.00	Pago a proveedor - Compra CP-000025	2026-06-17 23:28:23.523198+00
187	71	15	340000.00	0.00	Cuentas por cobrar - Factura INV-000029	2026-06-17 23:30:55.121173+00
188	71	38	0.00	340000.00	Ingresos por servicios - Régimen Simple	2026-06-17 23:30:55.121173+00
189	71	15	0.00	340000.00	Recaudo - Factura INV-000029	2026-06-17 23:30:55.121173+00
190	71	4	340000.00	0.00	Ingreso de dinero - CASH	2026-06-17 23:30:55.121173+00
191	71	63	158000.00	0.00	Costo de ventas - Factura INV-000029	2026-06-17 23:30:55.121173+00
192	71	16	0.00	158000.00	Salida de inventario - Factura INV-000029	2026-06-17 23:30:55.121173+00
193	72	16	188999.37	0.00	Inventarios - Compra CP-000026	2026-06-18 14:13:04.430302+00
194	72	4	0.00	188999.37	Pago a proveedor - Compra CP-000026	2026-06-18 14:13:04.430302+00
195	73	45	188999.37	0.00	Retiro - Pago a proveedor - Factura 100508	2026-06-18 14:13:04.624253+00
196	73	4	0.00	188999.37	Salida de CASH	2026-06-18 14:13:04.624253+00
197	74	15	1200000.00	0.00	Cuentas por cobrar - Factura INV-000030	2026-06-18 14:21:31.576795+00
198	74	38	0.00	1200000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:21:31.576795+00
199	74	15	0.00	1200000.00	Recaudo - Factura INV-000030	2026-06-18 14:21:31.576795+00
200	74	8	1200000.00	0.00	Ingreso de dinero - TRANSFER	2026-06-18 14:21:31.576795+00
201	74	63	400000.00	0.00	Costo de ventas - Factura INV-000030	2026-06-18 14:21:31.576795+00
202	74	16	0.00	400000.00	Salida de inventario - Factura INV-000030	2026-06-18 14:21:31.576795+00
203	75	16	10000.00	0.00	Inventarios - Stock inicial memoria RAM DDR3 4 GB USADA	2026-06-18 14:24:59.983314+00
204	75	4	0.00	10000.00	Pago stock inicial - CASH	2026-06-18 14:24:59.983314+00
205	76	15	40000.00	0.00	Cuentas por cobrar - Factura INV-000031	2026-06-18 14:26:16.10438+00
206	76	38	0.00	40000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:26:16.10438+00
207	76	15	0.00	40000.00	Recaudo - Factura INV-000031	2026-06-18 14:26:16.10438+00
208	76	4	40000.00	0.00	Ingreso de dinero - CASH	2026-06-18 14:26:16.10438+00
209	76	63	10000.00	0.00	Costo de ventas - Factura INV-000031	2026-06-18 14:26:16.10438+00
210	76	16	0.00	10000.00	Salida de inventario - Factura INV-000031	2026-06-18 14:26:16.10438+00
211	77	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000032	2026-06-18 14:42:43.875931+00
212	77	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:42:43.875931+00
213	77	15	0.00	60000.00	Recaudo - Factura INV-000032	2026-06-18 14:42:43.875931+00
214	77	4	60000.00	0.00	Ingreso de dinero - CASH	2026-06-18 14:42:43.875931+00
215	78	15	300000.00	0.00	Cuentas por cobrar - Factura INV-000033	2026-06-18 14:48:07.637794+00
216	78	38	0.00	300000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:48:07.637794+00
217	78	15	0.00	300000.00	Recaudo - Factura INV-000033	2026-06-18 14:48:07.637794+00
218	78	4	300000.00	0.00	Ingreso de dinero - CASH	2026-06-18 14:48:07.637794+00
219	79	15	120000.00	0.00	Cuentas por cobrar - Factura INV-000034	2026-06-18 14:50:07.511664+00
220	79	38	0.00	120000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:50:07.511664+00
221	79	15	0.00	120000.00	Recaudo - Factura INV-000034	2026-06-18 14:50:07.511664+00
222	79	4	120000.00	0.00	Ingreso de dinero - CASH	2026-06-18 14:50:07.511664+00
223	80	15	80000.00	0.00	Cuentas por cobrar - Factura INV-000035	2026-06-18 14:50:52.769959+00
224	80	38	0.00	80000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:50:52.769959+00
225	80	15	0.00	80000.00	Recaudo - Factura INV-000035	2026-06-18 14:50:52.769959+00
226	80	4	80000.00	0.00	Ingreso de dinero - CASH	2026-06-18 14:50:52.769959+00
227	81	45	50000.00	0.00	Retiro - Pago a proveedor - Factura SI-PUR-1780355865-59	2026-06-18 14:52:52.685328+00
228	81	9	0.00	50000.00	Salida de BANK	2026-06-18 14:52:52.685328+00
229	82	15	70000.00	0.00	Cuentas por cobrar - Factura INV-000036	2026-06-18 14:53:42.158038+00
230	82	38	0.00	70000.00	Ingresos por servicios - Régimen Simple	2026-06-18 14:53:42.158038+00
231	82	15	0.00	70000.00	Recaudo - Factura INV-000036	2026-06-18 14:53:42.158038+00
232	82	4	70000.00	0.00	Ingreso de dinero - CASH	2026-06-18 14:53:42.158038+00
233	82	63	50000.00	0.00	Costo de ventas - Factura INV-000036	2026-06-18 14:53:42.158038+00
234	82	16	0.00	50000.00	Salida de inventario - Factura INV-000036	2026-06-18 14:53:42.158038+00
235	83	16	450000.00	0.00	Inventarios - Compra CP-000027	2026-06-18 14:59:25.955792+00
236	83	8	0.00	450000.00	Pago a proveedor - Compra CP-000027	2026-06-18 14:59:25.955792+00
237	84	15	0.00	0.00	Cuentas por cobrar - Factura INV-000037	2026-06-18 15:00:23.297722+00
238	84	38	0.00	0.00	Ingresos por servicios - Régimen Simple	2026-06-18 15:00:23.297722+00
239	85	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000038	2026-06-18 15:01:08.097229+00
240	85	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-06-18 15:01:08.097229+00
241	85	15	0.00	60000.00	Recaudo - Factura INV-000038	2026-06-18 15:01:08.097229+00
242	85	4	60000.00	0.00	Ingreso de dinero - CASH	2026-06-18 15:01:08.097229+00
243	86	16	30000.00	0.00	Inventarios - Stock inicial Servicio reparación electronica	2026-06-18 15:04:36.745471+00
244	86	4	0.00	30000.00	Pago stock inicial - CASH	2026-06-18 15:04:36.745471+00
245	87	15	150000.00	0.00	Cuentas por cobrar - Factura INV-000039	2026-06-18 15:06:56.048588+00
246	87	38	0.00	150000.00	Ingresos por servicios - Régimen Simple	2026-06-18 15:06:56.048588+00
247	87	15	0.00	150000.00	Recaudo - Factura INV-000039	2026-06-18 15:06:56.048588+00
248	87	4	150000.00	0.00	Ingreso de dinero - CASH	2026-06-18 15:06:56.048588+00
249	87	63	30000.00	0.00	Costo de ventas - Factura INV-000039	2026-06-18 15:06:56.048588+00
250	87	16	0.00	30000.00	Salida de inventario - Factura INV-000039	2026-06-18 15:06:56.048588+00
251	88	15	50000.00	0.00	Cuentas por cobrar - Factura INV-000040	2026-06-20 16:31:37.540198+00
252	88	38	0.00	50000.00	Ingresos por servicios - Régimen Simple	2026-06-20 16:31:37.540198+00
253	89	15	280000.00	0.00	Cuentas por cobrar - Factura INV-000041	2026-06-20 16:53:59.554485+00
254	89	38	0.00	280000.00	Ingresos por servicios - Régimen Simple	2026-06-20 16:53:59.554485+00
255	89	15	0.00	280000.00	Recaudo - Factura INV-000041	2026-06-20 16:53:59.554485+00
256	89	4	280000.00	0.00	Ingreso de dinero - CASH	2026-06-20 16:53:59.554485+00
257	89	63	158823.00	0.00	Costo de ventas - Factura INV-000041	2026-06-20 16:53:59.554485+00
258	89	16	0.00	158823.00	Salida de inventario - Factura INV-000041	2026-06-20 16:53:59.554485+00
259	90	15	70000.00	0.00	Cuentas por cobrar - Factura INV-000042	2026-06-20 17:02:04.70278+00
260	90	38	0.00	70000.00	Ingresos por servicios - Régimen Simple	2026-06-20 17:02:04.70278+00
261	90	15	0.00	70000.00	Recaudo - Factura INV-000042	2026-06-20 17:02:04.70278+00
262	90	4	70000.00	0.00	Ingreso de dinero - CASH	2026-06-20 17:02:04.70278+00
263	91	45	450000.00	0.00	Retiro - Pago a proveedor - Factura SI-PUR-1781794765-65	2026-06-23 22:07:52.940222+00
264	91	4	0.00	450000.00	Salida de CASH	2026-06-23 22:07:52.940222+00
265	92	16	90000.00	0.00	Inventarios - Compra CP-000030	2026-06-23 23:19:01.95306+00
266	92	4	0.00	90000.00	Pago a proveedor - Compra CP-000030	2026-06-23 23:19:01.95306+00
267	93	45	90000.00	0.00	Retiro - Pago a proveedor - Factura 3899	2026-06-23 23:19:02.011844+00
268	93	4	0.00	90000.00	Salida de CASH	2026-06-23 23:19:02.011844+00
269	94	16	120000.00	0.00	Inventarios - Stock inicial SERVICIO REPRACION ELECTRONICA LENOVO	2026-06-23 23:24:11.871288+00
270	94	4	0.00	120000.00	Pago stock inicial - CASH	2026-06-23 23:24:11.871288+00
271	95	16	120000.00	0.00	Inventarios - Compra CP-000031	2026-06-23 23:26:44.162809+00
272	95	4	0.00	120000.00	Pago a proveedor - Compra CP-000031	2026-06-23 23:26:44.162809+00
273	96	15	330000.00	0.00	Cuentas por cobrar - Factura INV-000043	2026-06-24 20:48:53.986409+00
274	96	38	0.00	330000.00	Ingresos por servicios - Régimen Simple	2026-06-24 20:48:53.986409+00
275	96	15	0.00	330000.00	Recaudo - Factura INV-000043	2026-06-24 20:48:53.986409+00
276	96	4	330000.00	0.00	Ingreso de dinero - CASH	2026-06-24 20:48:53.986409+00
277	97	16	90000.00	0.00	Inventarios - Stock inicial Reparación electrónica portátil Asus	2026-06-24 21:01:25.90794+00
278	97	4	0.00	90000.00	Pago stock inicial - CASH	2026-06-24 21:01:25.90794+00
279	98	16	10000.00	0.00	Inventarios - Stock inicial reparación cargador Asus	2026-06-24 21:04:21.315474+00
280	98	4	0.00	10000.00	Pago stock inicial - CASH	2026-06-24 21:04:21.315474+00
281	99	15	260000.00	0.00	Cuentas por cobrar - Factura INV-000044	2026-06-24 21:09:12.519302+00
282	99	38	0.00	260000.00	Ingresos por servicios - Régimen Simple	2026-06-24 21:09:12.519302+00
283	99	15	0.00	260000.00	Recaudo - Factura INV-000044	2026-06-24 21:09:12.519302+00
284	99	8	260000.00	0.00	Ingreso de dinero - TRANSFER	2026-06-24 21:09:12.519302+00
285	100	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000045	2026-06-24 21:17:44.04423+00
286	100	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-06-24 21:17:44.04423+00
287	100	15	0.00	60000.00	Recaudo - Factura INV-000045	2026-06-24 21:17:44.04423+00
288	100	4	60000.00	0.00	Ingreso de dinero - CASH	2026-06-24 21:17:44.04423+00
291	102	47	520000.00	0.00	Pago Salud y pension	2026-06-24 22:18:10.652307+00
292	102	9	0.00	520000.00	Pago Salud y pension	2026-06-24 22:18:10.652307+00
293	103	47	100000.00	0.00	gym	2026-06-25 20:30:05.494127+00
294	103	4	0.00	100000.00	gym	2026-06-25 20:30:05.494127+00
295	104	47	300000.00	0.00	gastos varios casa	2026-06-25 20:33:09.051354+00
296	104	4	0.00	300000.00	gastos varios casa	2026-06-25 20:33:09.051354+00
297	105	15	60000.00	0.00	Cuentas por cobrar - Factura INV-000046	2026-06-25 20:34:53.911611+00
298	105	38	0.00	60000.00	Ingresos por servicios - Régimen Simple	2026-06-25 20:34:53.911611+00
299	105	15	0.00	60000.00	Recaudo - Factura INV-000046	2026-06-25 20:34:53.911611+00
300	105	4	60000.00	0.00	Ingreso de dinero - CASH	2026-06-25 20:34:53.911611+00
301	106	16	16000.00	0.00	Inventarios - Compra CP-000032	2026-06-25 20:47:52.523164+00
302	106	8	0.00	16000.00	Pago a proveedor - Compra CP-000032	2026-06-25 20:47:52.523164+00
303	107	45	16000.00	0.00	Retiro - Pago a proveedor - Factura 0001	2026-06-25 20:47:52.570064+00
304	107	9	0.00	16000.00	Salida de BANK	2026-06-25 20:47:52.570064+00
305	108	15	104999.97	0.00	Cuentas por cobrar - Factura INV-000047	2026-06-25 20:49:32.218383+00
306	108	38	0.00	104999.97	Ingresos por servicios - Régimen Simple	2026-06-25 20:49:32.218383+00
307	108	15	0.00	104999.97	Recaudo - Factura INV-000047	2026-06-25 20:49:32.218383+00
308	108	4	104999.97	0.00	Ingreso de dinero - CASH	2026-06-25 20:49:32.218383+00
309	109	15	70000.00	0.00	Cuentas por cobrar - Factura INV-000048	2026-06-25 20:54:17.173165+00
310	109	38	0.00	70000.00	Ingresos por servicios - Régimen Simple	2026-06-25 20:54:17.173165+00
311	109	15	0.00	70000.00	Recaudo - Factura INV-000048	2026-06-25 20:54:17.173165+00
312	109	8	70000.00	0.00	Ingreso de dinero - TRANSFER	2026-06-25 20:54:17.173165+00
313	110	15	600000.00	0.00	Cuentas por cobrar - Factura INV-000049	2026-06-25 20:59:14.864093+00
314	110	38	0.00	600000.00	Ingresos por servicios - Régimen Simple	2026-06-25 20:59:14.864093+00
315	110	15	0.00	600000.00	Recaudo - Factura INV-000049	2026-06-25 20:59:14.864093+00
316	110	8	600000.00	0.00	Ingreso de dinero - TRANSFER	2026-06-25 20:59:14.864093+00
317	111	16	288987.93	0.00	Inventarios - Compra CP-000033	2026-06-25 21:14:45.074926+00
318	111	8	0.00	288987.93	Pago a proveedor - Compra CP-000033	2026-06-25 21:14:45.074926+00
319	112	45	288987.93	0.00	Retiro - Pago a proveedor - Factura ATPE 100487	2026-06-25 21:14:45.144885+00
320	112	9	0.00	288987.93	Salida de BANK	2026-06-25 21:14:45.144885+00
321	113	15	300000.00	0.00	Cuentas por cobrar - Factura INV-000050	2026-06-25 21:17:24.702376+00
322	113	38	0.00	300000.00	Ingresos por servicios - Régimen Simple	2026-06-25 21:17:24.702376+00
323	113	15	0.00	300000.00	Recaudo - Factura INV-000050	2026-06-25 21:17:24.702376+00
324	113	4	300000.00	0.00	Ingreso de dinero - CASH	2026-06-25 21:17:24.702376+00
325	114	15	50000.00	0.00	Cuentas por cobrar - Factura INV-000051	2026-06-25 21:49:38.887325+00
326	114	38	0.00	50000.00	Ingresos por servicios - Régimen Simple	2026-06-25 21:49:38.887325+00
327	114	15	0.00	50000.00	Recaudo - Factura INV-000051	2026-06-25 21:49:38.887325+00
328	114	4	50000.00	0.00	Ingreso de dinero - CASH	2026-06-25 21:49:38.887325+00
\.


--
-- Data for Name: partners; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.partners (id, nit, dv, name, partner_type, responsibility_fiscal, address, phone, email, contact_person, credit_limit, is_active, company_id, created_at, updated_at) FROM stdin;
1	9001638619	\N	Janus	SUPPLIER	RESPONSABLE IVA	Bogota	3165459795	\N	\N	\N	t	1	2026-04-28 23:22:21.744404+00	2026-04-28 23:22:21.744404+00
2	900617819	9	ATTECH	SUPPLIER	RESPONSABLE IVA	carrera 24 # 15-60 centro comercial San Agustín	3186566587	\N	\N	\N	t	1	2026-04-28 23:25:06.872548+00	2026-04-28 23:25:06.872548+00
3	8909000943	1	Corveta	SUPPLIER	RESPONSABLE IVA	Pasto	3164374894	\N	\N	\N	t	1	2026-04-28 23:26:39.698661+00	2026-04-28 23:26:39.698661+00
4	1089031394	\N	Enilse Hernadez	CUSTOMER	NO RESPONSABLE	Pasto	3177822508	enilseh28@gmail.com	\N	\N	t	1	2026-04-29 20:02:10.921085+00	2026-04-29 20:02:10.921085+00
5	56565656565	\N	Nancy Burbano	CUSTOMER	NO RESPONSABLE	Pasto	3218441353	\N	\N	\N	t	1	2026-04-30 20:41:51.852106+00	2026-04-30 20:41:51.852106+00
6	65656565	\N	Yolanda Tienda	CUSTOMER	NO RESPONSABLE	Atahualpa pasto	318 5853688	yolanda@gmail.com	\N	\N	t	1	2026-05-02 15:06:29.69808+00	2026-05-02 15:06:29.69808+00
7	6656565689888	\N	Dario Villada	CUSTOMER	NO RESPONSABLE	Pasto	3122063695	dario@gmail.com	\N	\N	t	1	2026-05-02 15:54:20.119166+00	2026-05-02 15:54:20.119166+00
8	5658787822112	\N	Sobrino Alonso	CUSTOMER	NO RESPONSABLE	Pasto	318 8630549	sobalonso@gmail.com	\N	\N	t	1	2026-05-02 20:54:02.722961+00	2026-05-02 20:54:02.722961+00
9	65656565	\N	Harol Paredes	SUPPLIER	NO RESPONSABLE	carrera 24 # 15-60 centro comercial San Agustin	317 2218243	haroll@gmail.com	\N	\N	t	1	2026-05-02 21:03:01.914611+00	2026-05-02 21:03:01.914611+00
10	1085245039	9	Todo Portatiles	SUPPLIER	NO RESPONSABLE	cc el Dorado local 26	3207542850	dario@gmail.com	\N	\N	t	1	2026-05-06 16:37:08.49558+00	2026-05-06 16:37:08.49558+00
11	900163861	9	Janus	SUPPLIER	RESPONSABLE IVA	Bogota	3165459795	Janus@gmail.com	\N	\N	t	1	2026-05-06 22:26:21.672264+00	2026-05-06 22:26:21.672264+00
12	100414663	\N	Samara Quigua	CUSTOMER	NO RESPONSABLE	Pasto	3105285974	quiguahivon@gmail.com	\N	\N	t	1	2026-05-07 20:00:17.3269+00	2026-05-07 20:00:17.3269+00
13	1245455	1	TYS	SUPPLIER	RESPONSABLE IVA	Calle 5 # 25-15 Bogota	57 313 820 4798	comercial@tyscomp.com	\N	\N	t	1	2026-05-08 22:38:00.769543+00	2026-05-08 22:38:00.769543+00
14	27547873	\N	Marleny obando	CUSTOMER	NO RESPONSABLE	Pasto	3104615834	mar1960oba@gmail.com	\N	\N	t	1	2026-05-09 14:49:59.119267+00	2026-05-09 14:49:59.119267+00
15	56565656	\N	Harol Paredes	SUPPLIER	NO RESPONSABLE	San Agustín 	317 2218243	harol@gmail.com	\N	\N	t	1	2026-05-09 16:16:12.236674+00	2026-05-09 16:16:12.236674+00
16	1143995608	\N	Diara Garcia	CUSTOMER	NO RESPONSABLE	Pasto	3186260393	diaracar957@gmail.com	\N	\N	t	1	2026-05-11 19:52:11.623446+00	2026-05-11 19:52:11.623446+00
17	1004134255	\N	William Ortega	CUSTOMER	NO RESPONSABLE	\N	3186113572	wortegas@unal.edu.co	\N	\N	t	1	2026-05-12 20:20:42.686237+00	2026-05-12 20:20:42.686237+00
18	10852450399	\N	TODO PORTATILES 	SUPPLIER	NO RESPONSABLE	centro comercial el Dorado 	3207542850	dario@gmail.com	\N	\N	t	1	2026-05-12 21:51:06.771936+00	2026-05-12 21:51:06.771936+00
19	87063205	\N	Fabian Montilla	CUSTOMER	NO RESPONSABLE	Pasto	3004077948	fabrixio83@hormail.es	\N	\N	t	1	2026-05-15 15:16:22.220954+00	2026-05-15 15:16:22.220954+00
20	1085257145	\N	Heidi Tulcán	CUSTOMER	NO RESPONSABLE	Pasto	3173399976	heiditulcan@gmail.com	\N	\N	t	1	2026-05-15 15:23:48.316475+00	2026-05-15 15:23:48.316475+00
21	12979170	\N	Luis Carlos Ortega	CUSTOMER	NO RESPONSABLE	Pasto	3148942235	luiscarlosortegafuertes@yahoo.es	\N	\N	t	1	2026-05-15 16:24:34.719032+00	2026-05-15 16:24:34.719032+00
22	000012545	\N	David Quintero	CUSTOMER	NO RESPONSABLE	Villa garzón Putumayo	 318 3850461	davidq@gmail.com	\N	\N	t	1	2026-05-15 23:05:29.851274+00	2026-05-15 23:05:29.851274+00
23	901476410	8	Ledacon	SUPPLIER	RESPONSABLE IVA	cr 52A  10 70	4442406	ledacon@ledacom.com	\N	\N	t	1	2026-05-15 23:12:58.61605+00	2026-05-15 23:12:58.61605+00
24	12967894	\N	José Tello Benavides	CUSTOMER	NO RESPONSABLE	\N	3157412391	jose.benavides894@hotmail.com	\N	\N	t	1	2026-05-19 14:29:45.080048+00	2026-05-19 14:29:45.080048+00
25	1085278381	\N	Yaneth Zambrano	CUSTOMER	NO RESPONSABLE	\N	3012687739	yaneth_z@hotmail.com	\N	\N	t	1	2026-05-19 19:44:16.493382+00	2026-05-19 19:44:16.493382+00
26	39619764	\N	Janeth Sanzon	CUSTOMER	NO RESPONSABLE	Pasto	3189897302	janetsansin06@gmail.com	\N	\N	t	1	2026-05-19 20:22:42.502278+00	2026-05-19 20:22:42.502278+00
27	1004551082	\N	kevin chaves	CUSTOMER	NO RESPONSABLE	Pasto	3015255591	kevin12chaves13@gmail.com	\N	\N	t	1	2026-05-19 20:43:03.963239+00	2026-05-19 20:43:03.963239+00
28	1085283868	\N	Yesica Hernadez	CUSTOMER	NO RESPONSABLE	\N	3103732886	nena12075@gmail.com	\N	\N	t	1	2026-05-20 15:26:59.678314+00	2026-05-20 15:26:59.678314+00
29	12965992	\N	Harol Enriquez	CUSTOMER	NO RESPONSABLE	\N	3225140129	enriquezharol@hotmail.com	\N	\N	t	1	2026-05-20 20:22:41.329316+00	2026-05-20 20:22:41.329316+00
30	830085336	5	Digital MTX	SUPPLIER	NO RESPONSABLE	AUT MEDELLIN KM 3 BG 41 MD 2 CC METROPOLITANO	316 8311535	ventasnacionales@digitalmte.com	\N	\N	t	1	2026-05-25 19:30:05.422383+00	2026-05-25 19:30:05.422383+00
31	212121212	\N	Jose gabriel	CUSTOMER	NO RESPONSABLE	Pasto	318 3818217	jose@gmail.com	\N	\N	t	1	2026-05-26 22:35:38.848543+00	2026-05-26 22:35:38.848543+00
32	54545456656	\N	ABOGADO MAC	CUSTOMER	NO RESPONSABLE	pasto	256556655	abogado@gmail.com	\N	\N	t	1	2026-05-26 23:11:10.112448+00	2026-05-26 23:11:10.112448+00
33	5256565	\N	Diwin 	CUSTOMER	NO RESPONSABLE	llorente	316 5508522	diwin@gmail.com	\N	\N	t	1	2026-05-27 17:27:17.610344+00	2026-05-27 17:27:17.610344+00
34	5213812	\N	ROMULO ZAMBRANO	CUSTOMER	NO RESPONSABLE	Pasto	3175811961	rpofiza@gmail.com	\N	\N	t	1	2026-05-27 21:41:41.482957+00	2026-05-27 21:41:41.482957+00
35	656565656	\N	Alberto del Castillo	CUSTOMER	NO RESPONSABLE	Pasto	6565656	Albertodelcastillo@gmail.com	\N	\N	t	1	2026-05-28 23:01:15.30188+00	2026-05-28 23:01:15.30188+00
36	1085290273	\N	ANDRES GUERRERO 	CUSTOMER	NO RESPONSABLE	Pasto	3136072606	jeloandres@hotmail.com	\N	\N	t	1	2026-05-29 19:30:22.265423+00	2026-05-29 19:30:22.265423+00
37	12981670	\N	CARLOS RAMIREZ	CUSTOMER	NO RESPONSABLE	pasto	3173741925	carlitosalb64@hotmail.es	\N	\N	t	1	2026-05-29 20:39:11.582968+00	2026-05-29 20:39:11.582968+00
38	30728817	\N	ROCIO CABRERA	CUSTOMER	NO RESPONSABLE	PASTO	3206776250	CABRERAROCIO49@GMAIL.COM	\N	\N	t	1	2026-05-29 20:50:08.313702+00	2026-05-29 20:50:08.313702+00
39	27212965	\N	MAGALY LOPEZ	CUSTOMER	NO RESPONSABLE	Pasto	3138232449	mariaceballos3547@gmail.com	\N	\N	t	1	2026-05-29 20:54:27.848366+00	2026-05-29 20:54:27.848366+00
40	13062381	\N	LUIS EDUAEDO MOLINA	CUSTOMER	NO RESPONSABLE	pasto	3164426013	lemov64@gmail.com	\N	\N	t	1	2026-05-30 15:57:17.152437+00	2026-05-30 15:57:17.152437+00
41	87573960	\N	ARMANDO ROJAS	CUSTOMER	NO RESPONSABLE	pasto	3172411739	arrb3353@gmail.com	\N	\N	t	1	2026-05-30 17:19:32.703399+00	2026-05-30 17:19:32.703399+00
42	1085283490	\N	CLAUDIA LILIANA ESPINOZA	CUSTOMER	NO RESPONSABLE	PASTO	3154686419	CLAUDIALILIANA@GMAIL.COM	\N	\N	t	1	2026-05-30 20:58:22.03976+00	2026-05-30 20:58:22.03976+00
43	1084846476	\N	ANDRES VALLEJO	CUSTOMER	NO RESPONSABLE	PASTO	3153787092	PIPE0108200@GMAIL.COM	\N	\N	t	1	2026-06-01 15:46:27.221115+00	2026-06-01 15:46:27.221115+00
44	78106737	\N	UBALDO GELIZ	CUSTOMER	NO RESPONSABLE	Pasto	3136428414	uglizher60@gmail.com	\N	\N	t	1	2026-06-03 13:44:49.237555+00	2026-06-03 13:44:49.237555+00
45	12961490	\N	HUGO CORAL	CUSTOMER	NO RESPONSABLE	pasto	3136433059	hugocoral54@gmail.com	\N	\N	t	1	2026-06-03 15:46:49.926786+00	2026-06-03 15:46:49.926786+00
46	27093608	\N	CLAUDIA ZAPATA	CUSTOMER	NO RESPONSABLE	Pasto	3116256986	cludiaelizabeth0@hotmail.com	\N	\N	t	1	2026-06-03 19:41:49.326826+00	2026-06-03 19:41:49.326826+00
47	1033098460	\N	IVAN MORENO	CUSTOMER	NO RESPONSABLE	pasto	3238607088	immcrty777@gmail.com	\N	\N	t	1	2026-06-03 20:00:14.955667+00	2026-06-03 20:00:14.955667+00
48	307282043	\N	Ana Patricia Rueda	CUSTOMER	NO RESPONSABLE	Pasto	3005725850	ana@gmail.com	\N	\N	t	1	2026-06-04 13:42:09.494114+00	2026-06-04 13:42:09.494114+00
49	5309773	\N	EMILIO HERNADEZ	CUSTOMER	NO RESPONSABLE	PASTO	3188798928	ANDRES@GMAIL.COM	\N	\N	t	1	2026-06-04 15:35:46.529424+00	2026-06-04 15:35:46.529424+00
50	87066839	\N	ALBEIRO MORA	CUSTOMER	NO RESPONSABLE	PASTO	3165506590	ALBEIROMORA11@GMAIL.COM	\N	\N	t	1	2026-06-05 21:47:26.351597+00	2026-06-05 21:47:26.351597+00
51	900972966	4	LUZ MEDICA	CUSTOMER	NO RESPONSABLE	Cra 32a N 9 75 barrio la Aurora	316 4237979	LUZMEDICA@GMAIL.COM	\N	\N	t	1	2026-06-05 22:23:06.809892+00	2026-06-05 22:23:06.809892+00
52	1083752268	\N	DANILO MAIGUA	CUSTOMER	NO RESPONSABLE	PASTO	3217597265	danilomaigua8@gmail.com	\N	\N	t	1	2026-06-09 22:01:07.989218+00	2026-06-09 22:01:07.989218+00
53	1085913330	\N	LUISA ROSERO	CUSTOMER	NO RESPONSABLE	pasto	3157943794	luisamariaroserochamorro@gmail.com	\N	\N	t	1	2026-06-11 15:10:01.368757+00	2026-06-11 15:10:01.368757+00
54	59822702	\N	AMANDA RIVAS	CUSTOMER	NO RESPONSABLE	Pasto	310443185	amandisrb@hotmail.com	\N	\N	t	1	2026-06-11 21:06:40.091601+00	2026-06-11 21:06:40.091601+00
55	16723433	\N	JAIRO BERDUGO	CUSTOMER	NO RESPONSABLE	Pasto	3203759173	jberdug@hotmail.com	\N	\N	t	1	2026-06-11 22:18:34.2592+00	2026-06-11 22:18:34.2592+00
56	1144109035	\N	CARLOS CORONEL	CUSTOMER	NO RESPONSABLE	PASTO	3128816104	carloscc2808@gmail.com	\N	\N	t	1	2026-06-12 17:05:36.37923+00	2026-06-12 17:05:36.37923+00
57	94553171	\N	CARLOS RODRIGUEZ	CUSTOMER	NO RESPONSABLE	PASTO	3128101148	CARLOS@GMAIL.COM	\N	\N	t	1	2026-06-13 15:24:59.327086+00	2026-06-13 15:24:59.327086+00
58	12964756	\N	WILLIAN MONTERO	CUSTOMER	NO RESPONSABLE	PASTO	3174506195	NELEYHERAZO28@GMAIL.COM	\N	\N	t	1	2026-06-16 14:14:21.246813+00	2026-06-16 14:14:21.246813+00
59	18147798	\N	JULIO CESAR MEJIA	CUSTOMER	NO RESPONSABLE	Pasto	3212330629	mejia18147@gmail.com	\N	\N	t	1	2026-06-17 17:29:31.749051+00	2026-06-17 17:29:31.749051+00
60	000000000000	\N	OLGA PUBLIMARK	CUSTOMER	NO RESPONSABLE	Cra. 25 #15-62 Local 103	312 6642838	publimar@gmail.com	\N	\N	t	1	2026-06-17 20:43:47.26055+00	2026-06-17 20:43:47.26055+00
61	87068949	\N	Camilo Lasso	CUSTOMER	NO RESPONSABLE	Pasto	\N	camilo@gmail.com	\N	\N	t	1	2026-06-18 14:17:53.930266+00	2026-06-18 14:17:53.930266+00
62	0000000	\N	Rosa Pachana Montenegro	CUSTOMER	NO RESPONSABLE	Pasto	\N	rosa@gmail.com	\N	\N	t	1	2026-06-18 14:26:03.712251+00	2026-06-18 14:26:03.712251+00
63	1085257737	\N	ALEXANDRA DELGADO	CUSTOMER	NO RESPONSABLE	Pasto	3022586459	lucanodelgadoluisalejandro@gmail.com	\N	\N	t	1	2026-06-19 14:35:00.208387+00	2026-06-19 14:35:00.208387+00
64	00000	\N	Catalina Revelo	CUSTOMER	NO RESPONSABLE	bogota	000000000	cata@gmail.com	\N	\N	t	1	2026-06-20 17:01:22.984329+00	2026-06-20 17:01:22.984329+00
65	1085271185	\N	LILIANA ROSALES	CUSTOMER	NO RESPONSABLE	Pasto	3167640857	deyliros22@hotmail.com	\N	\N	t	1	2026-06-22 19:33:40.851531+00	2026-06-22 19:33:40.851531+00
66	1085330743	\N	PAOLA RAMIREZ	CUSTOMER	NO RESPONSABLE	Pasto	3113000159	paoramirez@umariana.edu.com	\N	\N	t	1	2026-06-23 15:18:22.245887+00	2026-06-23 15:18:22.245887+00
67	59827327	\N	Cristina Prieto	CUSTOMER	NO RESPONSABLE	Pasto	3103712429	geralexcas@gmail.com	\N	\N	t	1	2026-06-24 15:58:42.013989+00	2026-06-24 15:58:42.013989+00
68	1088198321	\N	ANGELA BENAVIDES	CUSTOMER	NO RESPONSABLE	pasto	3183206668	angellabenavides11@gmail.com	\N	\N	t	1	2026-06-24 17:18:57.957083+00	2026-06-24 17:18:57.957083+00
69	000000000	\N	Andrés Gomez	CUSTOMER	NO RESPONSABLE	pasto	310 5930154	andres@gmail.com	\N	\N	t	1	2026-06-24 21:06:45.253912+00	2026-06-24 21:06:45.253912+00
70	1085314680	\N	ALISON DELGADO	CUSTOMER	NO RESPONSABLE	Pasto	3172286956	alisonximenadelgadoruano@gmail.com	\N	\N	t	1	2026-06-25 14:16:09.963605+00	2026-06-25 14:16:09.963605+00
71	10302170	\N	JOSE MUÑOZ	CUSTOMER	NO RESPONSABLE	Pasto	3103895912	jose-munoz89@hotmail.com	\N	\N	t	1	2026-06-25 14:25:10.744006+00	2026-06-25 14:25:10.744006+00
72	0000000	\N	Granero 	CUSTOMER	NO RESPONSABLE	Pasto Agualongo	00000000	granero@gmail.com	\N	\N	t	1	2026-06-25 20:36:46.220276+00	2026-06-25 20:36:46.220276+00
73	00000	\N	DYSION CALI	SUPPLIER	NO RESPONSABLE	CALI	000000	DYSION@GMAIL.COM	\N	\N	t	1	2026-06-25 20:40:28.242753+00	2026-06-25 20:40:28.242753+00
74	00000000000	\N	sobrina ruben	CUSTOMER	NO RESPONSABLE	pasto	00000000000	sobrina@gmail.com	\N	\N	t	1	2026-06-25 20:52:41.535384+00	2026-06-25 20:52:41.535384+00
75	1061819947	\N	Karemn Preciado	CUSTOMER	NO RESPONSABLE	Pasto	00000	karen@gmail.com	\N	\N	t	1	2026-06-25 20:58:22.861295+00	2026-06-25 20:58:22.861295+00
76	8901025134	4	iglesia pentecostal unidad de Colombia	CUSTOMER	NO RESPONSABLE	Pasto	311 7818022	iglecia@gmail.com	\N	\N	t	1	2026-06-25 21:48:54.295301+00	2026-06-25 21:48:54.295301+00
77	52430134	\N	SANDRA VALLEJO	CUSTOMER	NO RESPONSABLE	Pasto	30252255111	SVALLEJOLAGOS@GMAIL.COM	\N	\N	t	1	2026-06-26 20:59:27.803931+00	2026-06-26 20:59:27.803931+00
78	1087108453	\N	Alexis de la cruz Quiñones	CUSTOMER	NO RESPONSABLE	Tumaco	3163812722	alex@gmail.com	\N	\N	t	1	2026-06-27 19:31:57.49537+00	2026-06-27 19:31:57.49537+00
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.permissions (id, name, module, action) FROM stdin;
\.


--
-- Data for Name: product_price_history; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.product_price_history (id, product_id, company_id, price, effective_date) FROM stdin;
1	70	1	90000.00	2026-06-23 23:19:01.853825+00
2	76	1	5000.00	2026-06-25 20:47:52.230307+00
3	75	1	5500.00	2026-06-25 20:47:52.440912+00
4	77	1	5500.00	2026-06-25 20:47:52.487499+00
5	78	1	242847.00	2026-06-25 21:14:44.987082+00
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.products (id, sku, barcode, name, description, category, brand, model, unit_of_measure, purchase_price, sale_price, stock_level, min_stock_level, max_stock_level, is_active, company_id, supplier_id, created_at, updated_at, payment_method) FROM stdin;
3	0002	230738538512115727321516322454988	SSD NVE 512 GB Western Digita Usado 	SSD NVE 512 GB Western Digita Usado 	Almacenamiento 	\N	\N	UNIDAD	50000.00	220000.00	1.00	1.00	1.00	t	1	\N	2026-04-30 16:09:21.72912+00	2026-04-30 16:09:21.72912+00	CASH
4	0003	816909078305	Tarjeta de Video GT 710 2 GB	Tarjeta de Video GT 710 2 GB	T Video	\N	\N	UNIDAD	50000.00	190000.00	1.00	1.00	1.00	t	1	\N	2026-04-30 16:18:07.043139+00	2026-04-30 16:18:07.043139+00	CASH
5	0006-S117C9D60	S117C9D60	Memoria RAM DDR4 8 GB portatil usada	Memoria RAM DDR4 8 GB portátil usada	Memoria RAM Portatil	\N	\N	UNIDAD	50000.00	150000.00	1.00	1.00	5.00	t	1	\N	2026-04-30 17:00:14.662245+00	2026-04-30 17:00:14.662245+00	CASH
6	0006-HMAG68EXNSA051N BC 309	HMAG68EXNSA051N BC 309	Memoria RAM DDR4 8 GB portatil usada	Memoria RAM DDR4 8 GB portátil usada	Memoria RAM Portatil	\N	\N	UNIDAD	50000.00	150000.00	1.00	1.00	5.00	t	1	\N	2026-04-30 17:00:14.842162+00	2026-04-30 17:00:14.842162+00	CASH
8	0007		Portatil asus Core i3	Portátil Asus Core i3 quinta generación, memoria RAM 4 GB SSD 250 Gb , disco duro 1 tb Pantalla 15.6"	Portátiles Remanufacturados	\N	\N	UNIDAD	180000.00	580000.00	1.00	1.00	999999.99	t	1	\N	2026-05-02 19:38:59.938431+00	2026-05-02 19:38:59.938431+00	CASH
10	00008	0007	Todo En UNO Lenovo	Celeron 4 GB RAM SSD 250 GB pantalla 20"	Pc remanofacturado	\N	\N	UNIDAD	300000.00	650000.00	1.00	1.00	999999.99	t	1	\N	2026-05-02 19:58:15.671955+00	2026-05-02 19:58:15.671955+00	CASH
7	0006	000001	portatil Hp Probook	Core i5 Sexta generación, memoria RAM 8 GB SSD 250 GB	Portátiles Remanufacturados	\N	\N	UNIDAD	250000.00	750000.00	1.00	1.00	5.00	t	1	\N	2026-04-30 20:41:01.517988+00	2026-05-04 23:33:27.074822+00	CASH
19	00000010	00100010037011	PC DE ESCIROTIO JANUS CORE I5 12400	PROCESADOR CORE I5 12400 MEMORIA RAM 8 GB SSD 500GB SATA	PC DE ESCRITORIO	\N	\N	UNIDAD	1685000.00	1850000.00	1.00	1.00	999999.99	t	1	1	2026-05-07 14:13:43.606105+00	2026-05-07 14:13:43.606105+00	CASH
23	0000012	00025855	Tóner HP 26x genérico	Tóner HP 26x genérico	Toner laser	\N	\N	UNIDAD	50000.00	85000.00	0.00	1.00	999999.99	t	1	9	2026-05-09 16:23:08.607478+00	2026-05-09 16:23:08.607478+00	CASH
29	000000012-TBNOCV15E477478A	TBNOCV15E477478A	PORTATIL ASUS AMD RYZEN 7 5825U	PORTATIL ASUS AMD RYZEN 7 5825U RAM 16 GB SSD 512GB PANTALLA 15.6" FHD	PORTATILES	\N	\N	UNIDAD	1899000.00	2100000.00	1.00	1.00	999999.99	t	1	23	2026-05-15 23:18:19.09225+00	2026-05-15 23:21:01.087438+00	CASH
28	tp00002	00002	Teclado hp  HP ck0010la	HP ck0010la	Teclados computador portatil	\N	\N	UNIDAD	75000.00	100000.00	0.00	1.00	999999.99	t	1	10	2026-05-12 23:20:25.856201+00	2026-05-13 22:32:20.439473+00	CASH
30	BWA43100001558-1	43100001558	DDR4 4GB 3200MHZ PORTATIL SAMSUNG	DDR4 4GB 3200MHZ PORTATIL SAMSUNG	Memoria RAM Portatil	\N	\N	UNIDAD	89000.00	120000.00	0.00	1.00	999999.99	t	1	2	2026-05-16 16:55:00.027672+00	2026-05-16 16:57:11.312546+00	CASH
31	000000013-1	000000013	SSD ADATA 250 GB	SSD ADATA 250 GB	Almacenamiento 	\N	\N	UNIDAD	180000.00	230000.00	1.00	1.00	999999.99	t	1	\N	2026-05-19 22:41:34.58233+00	2026-05-19 22:41:34.58233+00	CASH
32	0000014-1	00000014	MEMORIA RAM DDR4 8 GB PORTATIL	MEMORIA RAM DDR4 8 GB PARA PORTATIL	Memoria RAM Portatil	\N	\N	UNIDAD	50000.00	290000.00	0.00	0.00	999999.99	t	1	\N	2026-05-19 22:44:06.161524+00	2026-05-19 22:44:06.161524+00	CASH
33	000000014-1	11992468	Portatil asus  	procesador Intel Core i7 octava generación, 12 GB memoria RAM SSD128 GB , disco duro 1 TB  Pantalla 15.6, tarjeta de video NVIDIA 2 GB	Portátiles Remanufacturados	\N	\N	UNIDAD	480000.00	800000.00	1.00	1.00	999999.99	t	1	\N	2026-05-22 22:02:10.047882+00	2026-05-22 22:13:10.405096+00	CASH
45	00005207 -00003711	00003711	CARGADOR GENERICO ACER 19V 3.42 ULTRABOOK	CARGADOR GENERICO ACER 19V\n3.42 ULTRABOOK	Cargador Portatil	\N	\N	UNIDAD	21848.00	50000.00	1.00	1.00	999999.99	t	1	30	2026-05-25 20:13:00.485196+00	2026-05-25 20:13:00.485196+00	CASH
47	00005207 1	00005207	CARGADOR GENERICO HP 19V 3.33A AZU	CARGADOR GENERICO HP 19V 3.33A\nAZU	Cargador Portatil	\N	\N	UNIDAD	22268.00	50000.00	3.00	1.00	999999.99	t	1	30	2026-05-25 20:23:40.676939+00	2026-05-25 21:47:16.979822+00	CASH
48	000037111	000037111	CARGADOR PARA ACER 19V 3.42A	CARGADOR PARA ACER 19V 3.42A\nGENERICO punta amarilla	Cargador Portatil	\N	\N	UNIDAD	21848.00	50000.00	3.00	1.00	999999.99	t	1	30	2026-05-25 21:45:50.258501+00	2026-05-25 21:47:17.01541+00	CASH
46	00005207 -100003711	100003711	CARGADOR GENERICO ACER 19V 3.42 ULTRABOOK	CARGADOR GENERICO ACER 19V\n3.42 ULTRABOOK	Cargador Portatil	\N	\N	UNIDAD	21848.00	50000.00	3.00	1.00	999999.99	t	1	30	2026-05-25 20:13:00.611347+00	2026-05-25 21:47:17.051188+00	CASH
2	0001	5160239500004	Todo en uno Asus	 procesador Core i3 Séptima generación, 2.4 GHZ, memoria RAM 8 Gb SSD 250 GB pantalla 21"	PC remanofacturado	\N	\N	UNIDAD	280000.00	700000.00	0.00	1.00	1.00	t	1	\N	2026-04-30 16:06:08.208368+00	2026-05-26 23:03:15.845787+00	CASH
21	0000011	0011254788	CABEZAL EPSON L	L210 L220 L3210 L555 L675 L3210 L3110 L3250	REPUESTOS IMPRESORAS	\N	\N	UNIDAD	255000.00	355000.00	0.00	1.00	999999.99	t	1	13	2026-05-08 23:49:57.547391+00	2026-05-27 17:31:18.779737+00	BANK_TRANSFER
49	000000001	000000001p	producto prueba	producto prueba		\N	\N	UNIDAD	1.00	2.00	0.00	1.00	999999.99	t	1	\N	2026-05-27 23:27:12.222451+00	2026-05-27 23:27:49.865258+00	CASH
42	00005207-00005361	00005361	CARGADOR GENERICO HP 19V 3.33A AZUL	CARGADOR GENERICO HP 19V 3.33A\nAZUL	Cargador Portatil	\N	\N	UNIDAD	27000.00	50000.00	1.00	1.00	999999.99	t	1	30	2026-05-25 20:05:10.695184+00	2026-06-18 14:15:15.057722+00	CASH
59	000001H	0000011H	Caja de Mantenimiento Epson L5590	Caja de Mantenimiento Epson L5590	REPUESTOS IMPRESORAS	\N	\N	UNIDAD	50000.00	70000.00	0.00	1.00	999999.99	t	1	9	2026-06-01 23:17:45.409245+00	2026-06-18 14:53:42.109172+00	CASH
27	421000249802	421000249802	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	SSD ATTECH 256 GB	Almacenamiento 	\N	\N	UNIDAD	158823.00	220000.00	0.00	1.00	999999.99	t	1	2	2026-05-12 23:15:44.765143+00	2026-06-20 16:53:59.518895+00	CASH
60	00000020	00000020	Teclado genérico usb	Teclado genérico USB	Perifericos	\N	\N	UNIDAD	10000.00	30000.00	2.00	1.00	999999.99	t	1	\N	2026-06-01 23:19:04.120758+00	2026-06-01 23:19:04.120758+00	CASH
41	00003309-1	00003309	PANTALLA 14.0 LED SLIM 30 PIN CONECTOR SUP INVERTI 	PANTALLA 14.0 LED SLIM 30 PIN\nCONECTOR SUP INVERTI 	Pantalla Portatil	\N	\N	UNIDAD	260504.00	450000.00	0.00	1.00	999999.99	t	1	30	2026-05-25 20:03:37.505025+00	2026-06-06 15:56:40.484509+00	CASH
62	0000022	NXMXNAL0026030601E3400	Portatil ACER Aspire Core i5 cuarta generación	Portátil ACER Aspire Core i5 cuarta generación, memoria RAM 8 GB SSD 250 GB, pantalla 14"	Portátiles Remanufacturados	\N	\N	UNIDAD	220000.00	600000.00	1.00	1.00	999999.99	t	1	\N	2026-06-17 23:03:29.940954+00	2026-06-17 23:03:29.940954+00	BANK_TRANSFER
63	AT422-256GBSATAIII2.5	AT422-256GBSATAIII25	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	Almacenamiento 	\N	\N	UNIDAD	158000.00	230000.00	0.00	1.00	999999.99	t	1	2	2026-06-17 23:25:37.99716+00	2026-06-17 23:30:55.08553+00	CASH
76	000000035	000000035	TINTA CYAN GIONCLICK	TINTA CYAN GIONCLICK	Tintas Impresoras	\N	\N	UNIDAD	5000.00	15000.00	1.00	1.00	999999.99	t	1	73	2026-06-25 20:44:23.053953+00	2026-06-25 20:47:52.230307+00	CASH
61	00000021	000011212122	PORTATIL DELL CORE I5 DOCEAVA	portatil dell inspiron core i5 doceava generacion , 8 Gb memoria RAM, DDS 512 GB NVME, disco duro mecanico 1 TB, pantalla 15.62 	Portátiles Remanufacturados	\N	\N	UNIDAD	400000.00	1200000.00	0.00	1.00	999999.99	t	1	\N	2026-06-17 22:40:04.808022+00	2026-06-18 14:21:31.542155+00	BANK_TRANSFER
64	0000023	0000023	memoria RAM DDR3 4 GB USADA	memoria RAM DDR3 4 GB USADA	Memoria RAM Portatil	\N	\N	UNIDAD	10000.00	40000.00	0.00	1.00	999999.99	t	1	\N	2026-06-18 14:24:59.983314+00	2026-06-18 14:26:16.068778+00	CASH
65	14'DQ2533LA,802c4la·abm,5cd319dfy0	14DQ2533LA802c4laabm5cd319dfy0	Portátil hp Core i5 onceava generación	Portátil hp Core i5 onceava generación 8 GB memoria RAM SSD 512  GB, pantalla 14"	Portátiles Remanufacturados	\N	\N	UNIDAD	450000.00	1100000.00	1.00	1.00	999999.99	t	1	43	2026-06-18 14:59:25.955792+00	2026-06-18 14:59:25.955792+00	BANK_TRANSFER
67	0000023-1	0000023-1	Servicio reparación electronica	Servicio reparación electrónica jhon	repracion electronica	\N	\N	UNIDAD	30000.00	150000.00	0.00	1.00	999999.99	t	1	\N	2026-06-18 15:04:36.745471+00	2026-06-18 15:06:56.012883+00	CASH
75	000000040	000000040	TINTA MAGENTA GYOCLCK	TINTA MAGENTA GYOCLCK EPSON L	Tintas Impresoras	\N	\N	UNIDAD	5500.00	15000.00	1.00	1.00	999999.99	t	1	73	2026-06-25 20:42:03.566709+00	2026-06-25 20:47:52.440912+00	CASH
77	0000035	0000035	TINTA YELLOW GIONCLICK	TINTA YELLOW GIONCLICK L	Tintas Impresoras	\N	\N	UNIDAD	5500.00	14999.97	1.00	0.00	999999.99	t	1	73	2026-06-25 20:46:45.319436+00	2026-06-25 20:47:52.487499+00	CASH
70	00000028	0000028	TECLADO LENOVO AIR 14 2020	TECLADO LENOVO AIR 14 2020 INTERNA	Teclados computador portatil	\N	\N	UNIDAD	90000.00	110000.00	1.00	1.00	999999.99	t	1	18	2026-06-23 23:18:18.328393+00	2026-06-23 23:19:01.853825+00	CASH
71	0000000029	0000000029	SERVICIO REPRACION ELECTRONICA LENOVO	mantenimiento, cambio de pasta termimica, cambio cristal del pocesador e instalacion de win, INSTLACION Y cambio de teclado	repracion electronica	\N	\N	UNIDAD	120000.00	180000.00	1.00	1.00	999999.99	t	1	\N	2026-06-23 23:24:11.871288+00	2026-06-23 23:24:11.871288+00	CASH
72	0000000030	0000000030	SERVICIO REPRACION ELECTRONICA LENOVO	mantenimiento, cambio de pasta termimica, cambio cristal del pocesador e instalacion de win, INSTLACION Y cambio de teclado	repracion electronica	\N	\N	UNIDAD	120000.00	180000.00	1.00	1.00	999999.99	f	1	9	2026-06-23 23:26:44.162809+00	2026-06-24 15:41:59.836163+00	CASH
73	0000000031	0000000031	Reparación electrónica portátil Asus	Reparación electrónica portátil Asus	reparación electrónica	\N	\N	UNIDAD	90000.00	180000.00	1.00	1.00	999999.99	t	1	\N	2026-06-24 21:01:25.90794+00	2026-06-24 21:01:25.90794+00	CASH
74	000000000032	000000000032	reparación cargador Asus	reparación cargador Asus	reparación electrónica	\N	\N	UNIDAD	10000.00	40000.00	1.00	0.00	999999.99	t	1	\N	2026-06-24 21:04:21.315474+00	2026-06-24 21:04:21.315474+00	CASH
78	AT422-512GBSATAIII2.5	AT422-512GBSATAIII25	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 512GB -550MB/s- ATTECH	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 512GB -550MB/s- ATTECH	Almacenamiento 	\N	\N	UNIDAD	242847.00	300000.00	1.00	0.97	999999.99	t	1	2	2026-06-25 21:13:12.916919+00	2026-06-25 21:14:44.987082+00	CASH
\.


--
-- Data for Name: purchase_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchase_items (id, purchase_id, product_id, description, quantity, unit_price, discount_percent, discount_amount, tax_rate, tax_amount, line_total, created_at, serial_number) FROM stdin;
1	11	27	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	1.00	158823.00	0.00	0.00	19.00	0.00	158823.00	2026-05-12 23:16:01.61075+00	\N
2	12	28	Teclado hp  HP ck0010la	1.00	75000.00	0.00	0.00	0.00	0.00	75000.00	2026-05-12 23:20:57.294401+00	\N
3	13	29	PORTATIL ASUS AMD RYZEN 7 5825U	1.00	1899000.00	0.00	0.00	0.00	0.00	1899000.00	2026-05-15 23:18:44.023569+00	\N
4	14	41	PANTALLA 14.0 LED SLIM 30 PIN CONECTOR SUP INVERTI 	1.00	260504.00	0.00	0.00	19.00	0.00	260504.00	2026-05-25 21:47:16.817483+00	\N
5	14	47	CARGADOR GENERICO HP 19V 3.33A AZU	3.00	22268.00	0.00	0.00	19.00	0.00	66804.00	2026-05-25 21:47:16.817483+00	\N
6	14	48	CARGADOR PARA ACER 19V 3.42A	3.00	21848.00	0.00	0.00	19.00	0.00	65544.00	2026-05-25 21:47:16.817483+00	\N
7	14	46	CARGADOR GENERICO ACER 19V 3.42 ULTRABOOK	2.00	21848.00	0.00	0.00	19.00	0.00	43696.00	2026-05-25 21:47:16.817483+00	\N
17	24	59	Stock inicial - Caja de Mantenimiento Epson L5590	1.00	50000.00	0.00	0.00	0.00	0.00	50000.00	2026-06-01 23:17:45.409245+00	0000011H
18	25	63	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	1.00	158000.00	0.00	0.00	19.00	30020.00	188020.00	2026-06-17 23:28:23.345357+00	AT422-256GBSATAIII2.5
19	26	27	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 256GB -560MB/s- ATTECH	1.00	158823.00	0.00	0.00	19.00	30176.37	188999.37	2026-06-18 14:13:04.255869+00	AT422-256GBSATAIII2.5
20	27	65	Stock inicial - Portátil hp Core i5 onceava generación	1.00	450000.00	0.00	0.00	0.00	0.00	450000.00	2026-06-18 14:59:25.955792+00	14DQ2533LA802c4laabm5cd319dfy0
23	30	70	TECLADO LENOVO AIR 14 2020	1.00	90000.00	0.00	0.00	0.00	0.00	90000.00	2026-06-23 23:19:01.853825+00	\N
24	31	72	Stock inicial - SERVICIO REPRACION ELECTRONICA LENOVO	1.00	120000.00	0.00	0.00	0.00	0.00	120000.00	2026-06-23 23:26:44.162809+00	0000000030
25	32	76	TINTA CYAN GIONCLICK	1.00	5000.00	0.00	0.00	0.00	0.00	5000.00	2026-06-25 20:47:52.230307+00	\N
26	32	75	TINTA MAGENTA GYOCLCK	1.00	5500.00	0.00	0.00	0.00	0.00	5500.00	2026-06-25 20:47:52.230307+00	\N
27	32	77	TINTA YELLOW GIONCLICK	1.00	5500.00	0.00	0.00	0.00	0.00	5500.00	2026-06-25 20:47:52.230307+00	\N
28	33	78	UNIDAD DE ESTADO SOLIDO 2.5" SATA III 512GB -550MB/s- ATTECH	1.00	242847.00	0.00	0.00	19.00	46140.93	288987.93	2026-06-25 21:14:44.987082+00	\N
\.


--
-- Data for Name: purchase_payments; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchase_payments (id, purchase_id, payment_method, amount, payment_date, reference, notes, created_by, created_at) FROM stdin;
1	11	CASH	158823.00	2026-05-12 00:00:00+00	Auto-ATPE 100220	\N	1	2026-05-12 23:16:01.763085+00
2	12	CASH	75000.00	2026-05-12 00:00:00+00	Auto-tp00002	\N	1	2026-05-12 23:20:57.434635+00
3	13	BANK_TRANSFER	1899000.00	2026-05-11 00:00:00+00	Auto-88357	\N	2	2026-05-15 23:18:44.162541+00
4	14	CASH	436548.00	2026-05-15 00:00:00+00	Auto-FECO 66687	\N	1	2026-05-25 21:47:17.100429+00
5	25	BANK_TRANSFER	188020.00	2026-06-12 00:00:00+00	Auto-ATPE 100488	\N	2	2026-06-17 23:28:23.558952+00
6	26	CASH	188999.37	2026-06-17 00:00:00+00	Auto-100508	\N	1	2026-06-18 14:13:04.624253+00
7	24	BANK_TRANSFER	50000.00	2026-06-18 00:00:00+00			2	2026-06-18 14:52:52.561626+00
8	27	CASH	450000.00	2026-06-23 00:00:00+00			2	2026-06-23 22:07:52.806264+00
9	30	CASH	90000.00	2026-06-23 00:00:00+00	Auto-3899	\N	1	2026-06-23 23:19:02.011844+00
10	32	BANK_TRANSFER	16000.00	2026-06-25 00:00:00+00	Auto-0001	\N	2	2026-06-25 20:47:52.570064+00
11	33	BANK_TRANSFER	288987.93	2026-06-12 00:00:00+00	Auto-ATPE 100487	\N	2	2026-06-25 21:14:45.144885+00
\.


--
-- Data for Name: purchases; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.purchases (id, purchase_number, partner_id, purchase_date, due_date, subtotal, tax_amount, total_amount, discount_amount, currency, payment_method, status, notes, company_id, created_by, created_at, updated_at) FROM stdin;
11	ATPE 100220	2	2026-05-12 00:00:00+00	\N	158823.00	0.00	158823.00	0.00	COP	CASH	PAID	\N	1	1	2026-05-12 23:16:01.61075+00	2026-05-12 23:16:01.763085+00
12	tp00002	10	2026-05-12 00:00:00+00	\N	75000.00	0.00	75000.00	0.00	COP	CASH	PAID	\N	1	1	2026-05-12 23:20:57.294401+00	2026-05-12 23:20:57.434635+00
13	88357	23	2026-05-11 00:00:00+00	\N	1899000.00	0.00	1899000.00	0.00	COP	BANK_TRANSFER	PAID	\N	1	2	2026-05-15 23:18:44.023569+00	2026-05-15 23:18:44.162541+00
14	FECO 66687	30	2026-05-15 00:00:00+00	\N	436548.00	0.00	436548.00	0.00	COP	CASH	PAID	\N	1	1	2026-05-25 21:47:16.817483+00	2026-05-25 21:47:17.100429+00
25	ATPE 100488	2	2026-06-12 00:00:00+00	\N	158000.00	30020.00	188020.00	0.00	COP	BANK_TRANSFER	PAID	\N	1	2	2026-06-17 23:28:23.345357+00	2026-06-17 23:28:23.558952+00
26	100508	2	2026-06-17 00:00:00+00	\N	158823.00	30176.37	188999.37	0.00	COP	CASH	PAID	\N	1	1	2026-06-18 14:13:04.255869+00	2026-06-18 14:13:04.624253+00
24	SI-PUR-1780355865-59	9	2026-06-01 23:17:45.409245+00	\N	50000.00	0.00	50000.00	0.00	COP	CASH	PAID	Stock inicial generado automáticamente desde inventario	1	\N	2026-06-01 23:17:45.409245+00	2026-06-18 14:52:52.561626+00
27	SI-PUR-1781794765-65	43	2026-06-18 14:59:25.955792+00	\N	450000.00	0.00	450000.00	0.00	COP	BANK_TRANSFER	PAID	Stock inicial generado automáticamente desde inventario	1	\N	2026-06-18 14:59:25.955792+00	2026-06-23 22:07:52.806264+00
30	3899	10	2026-06-23 00:00:00+00	\N	90000.00	0.00	90000.00	0.00	COP	CASH	PAID	\N	1	1	2026-06-23 23:19:01.853825+00	2026-06-23 23:19:02.011844+00
31	SI-PUR-1782257204-72	9	2026-06-23 23:26:44.162809+00	\N	120000.00	0.00	120000.00	0.00	COP	CASH	ISSUED	Stock inicial generado automáticamente desde inventario	1	\N	2026-06-23 23:26:44.162809+00	2026-06-23 23:26:44.162809+00
32	0001	73	2026-06-25 00:00:00+00	\N	16000.00	0.00	16000.00	0.00	COP	BANK_TRANSFER	PAID	\N	1	2	2026-06-25 20:47:52.230307+00	2026-06-25 20:47:52.570064+00
33	ATPE 100487	2	2026-06-12 00:00:00+00	\N	242847.00	46140.93	288987.93	0.00	COP	BANK_TRANSFER	PAID	\N	1	2	2026-06-25 21:14:44.987082+00	2026-06-25 21:14:45.144885+00
\.


--
-- Data for Name: reconciliation_lines; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.reconciliation_lines (id, reconciliation_id, treasury_transaction_id, is_matched, amount, description, statement_date, system_date, difference, notes, created_at) FROM stdin;
\.


--
-- Data for Name: repair_items; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.repair_items (id, repair_order_id, description, serial_number, model, brand, issue_reported, quantity, unit_cost, discount, tax_rate, tax_amount, line_total, warranty_status, warranty_days, product_id) FROM stdin;
1	1	IMPRESORA	XAGB728379	L3210	Epson	error luces intermitentes, posible atasco	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
2	2	IMPRESORA	X7GP301219	L3250	Epson	Impresión defectuosa	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
3	3	LAPTOP	3px23LA#AB	ck0010la	HP	teclado no funciona, bisagra rota	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
4	4	LAPTOP	K3NRCX00F33413A	FX504	Asus TUFF	sistema operativo no carga	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
5	5	IMPRESORA		G4110	Canom	impresión defectuosa aire en el sistema	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
6	6	LAPTOP	httpÑ--support.lenovo.com-qrcode S-NÑPF0J16RH MOÑPF9XB6706077 MTMÑ80Q600ARLM	idea pad 300	Lenovo	reparación bisagras, instalar ssd 250 GB 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
7	7	LAPTOP	h8n0cx24624735f	X541U	ASUS	NO ENCIENDE	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
8	8	LAPTOP	CU104650	LATITUDE 7480	DELL	FALLO EN PANTALLA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
9	9	IMPRESORA	X4FQ000760	L396	Epson	impresión defectuosa  magenta	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
10	10	LAPTOP	sin serial	Core i3 decima generación	HP	no video 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
11	11	ESCRITORIO	8CC7110XF9	todo en unos	HP	revisar  software y se apaga 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
12	12	ESCRITORIO	W8AY005389	L655	Epson	impresión defectuosa color negro 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
13	13	ESCRITORIO	A6	AMD A6	COMPUMAX	INSTLACION SSD 250 GB SATA Y MANTENIMINETO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
14	14	LAPTOP	313262900123	g4080	lenovo	no enciende	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
15	15	LAPTOP	MP2FFD5EMPNXB3714171 	idea pad gamin 3	lenovo	problemas de audio 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
16	16	IMPRESORA	x644546146	L3110	EPSON	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
17	17	IMPRESORA	 CN11H4S1Q906YR	smarttank 515	hp	impresión defectuosa	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
18	18	LAPTOP	SIN SERIAL	INSPIRON 15	DELL	BISAGRA IZQUIERDA SOPORTE ROTO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
19	19	LAPTOP	sin serial	air	mac	instalar office	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
20	20	CELULAR	X644678304	L3110	Epson	impresion defectuosa	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
21	21	LAPTOP	93604331434	ASPIRE 3	ACER	BISAGRA ROTA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
22	22	ESCRITORIO	sin serial	clon	amd	configuracion correo y office	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
23	23	IMPRESORA	kkrn48383m	G2100	canon	ERROR LED PANEL, SIN TAPAS  TANQUES DE TIBNTA, DERRAME TINTA AZUL 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
24	24	IMPRESORA	se8y008051	M205	EPSON	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
25	25	IMPRESORA	kkdx36971m	G2100	CANON	IMPRESION  DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
26	26	LAPTOP	40200238445	ASPIRE LITE 14	ACER	CARGADOR SI 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
27	27	LAPTOP	sinserial	mac	apel	error no carga sistema operativo	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
28	28	IMPRESORA	xbbv371045	L5590	EPSON	ERROR ALMOHADILLAS	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
29	29	ESCRITORIO	xagz210722	L3250	EPSON	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
30	30	LAPTOP	14'DQ2533LA,802c4la·abm,5cd319dfy0		HP	MANTENIMINETO DE SOFTWARE	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
31	31	ESCRITORIO	s-nñ00139732	HG00941	intel nuc	REINICIAR PARA ABRIR DOCUMENTOS 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
32	32	LAPTOP	SIN SERIAL	NEURON G6	LANIX	NO VIDEO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
33	33	LAPTOP	82500	ASPIRE	ACER	REVISION 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
34	34	IMPRESORA	TNUK238331	l120	epson	error tintas	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
35	35	IMPRESORA	x644349113	L3110	EPSON	ATASCO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
36	36	IMPRESORA	x2pc022184	L495	EPSON	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
37	37	ESCRITORIO	SIN SERIAL	IDEA CENTRE	LENOVO	PANTALLA AZUL ERROR	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
38	38	IMPRESORA	cn8ao4g11w06ph	HP INK TANK 315	HP	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
39	39	LAPTOP	SIN SERIAL	LENOVO	LENOVO	VENTILADOR ATOPE, NO VIDEO 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
40	40	IMPRESORA	vjdy021659	L565	EPSON	EROR GENERAL	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
41	41	IMPRESORA	xagz210722	L3250	EPSON	TINTA DE RESIDUO DERRAMADA, IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
42	42	IMPRESORA	x5e8158152	L3150	EPSON	IMPRESION DEFECTUOSA, ERROR ALMOHADILLAS	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
43	43	LAPTOP	HTTPñ--SUPPORT.LENOVO.COM-QRCODE s-nñmp09fuyj moñmpnxb582601l  mtmñ80mh004mlm	IDEA PAD 100	LENOVO	CARGADOR SI 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
44	44	LAPTOP	638634	ASPIRE NITRO	ACER 	MANTENIMIENTO HADWARE, CAMBIO PASTA TERMICA, TERMAL PADS 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
45	45	LAPTOP	SIN SERIAL	ZENBOOK	ASUS	REVISION	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
46	46	LAPTOP	SIN SERIAL	INSPIRON CORE I7	DELL	NO VIDEO 	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
47	47	LAPTOP	SIN SERIAL 	HP BLANCO 	HP	NO CARGA SISTEMA OPERATIVO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
48	48	IMPRESORA	xagz508684	L3250	EPSON	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
49	49	IMPRESORA	xagz909888	L3250	EPSON	IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
50	50	CELULAR		PENTIUM	PC SAMRT	REVISION NO CARGA SISTEMA OPERATIVO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
51	51	LAPTOP	300sn59802	ONIX	COMPUMAX	FUNCIONAMIENTO LENTO	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
52	52	LAPTOP	0080887777	g40	lenovo	bisagra rota	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
53	53	LAPTOP	SIN SERIAL	HP 14	HP	PANTALLA ROTA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
54	54	LAPTOP	sin serial	asus 	asus	no videoo, cargador roto y punta rota	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
55	55	IMPRESORA	WBGK058857	l375	epson	error de almohadillas	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
56	56	DISCO DURO	cnba5902759d00cb2124b10	ST320	segate	NO SE DETECTA PARTICIONES	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
57	57	IMPRESORA	SIN SERIAL	L375	EPSON	IMPRESION DEFECTUOSA Y TINTAS COLOR VACIAS	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
58	58	LAPTOP	SIN SERIAL	NITRO	ACER	PANTALLA SE VUELBE NEGRA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
59	59	IMPRESORA	800026	SMART TANK 580	HP	MANTENIMIENTO IMPRESION DEFECTUOSA	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
60	60	IMPRESORA	X9LM036618	l120	Epson	reprara bandeja, atasco de papel	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
61	61	ESCRITORIO	sin serial	RAYZEN	CLON	se apaga	1	0.00	0.00	0.00	0.00	0.00	NO_WARRANTY	\N	\N
\.


--
-- Data for Name: repair_orders; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.repair_orders (id, order_number, partner_id, technician_id, issue_date, expected_delivery_date, actual_delivery_date, problem_description, diagnosis, service_notes, status, warranty_applied, total_labor_cost, total_parts_cost, total_amount, currency, cufe, xml_ubl, estado_dian, motivo_rechazo, invoice_id, company_id, created_at, updated_at) FROM stdin;
4	REP-00000004	8	2	2026-05-02 20:53:13.495+00	\N	\N	sistema operativo no carga	mantenimiento de software y hardware, cambio pasta térmica 	cargador si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	2	1	2026-05-02 20:57:39.84747+00	2026-05-12 21:03:22.510461+00
1	REP-00000001	4	2	2026-04-29 20:02:16.315+00	\N	\N	error luces intermitentes, posible atasco		cables no	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	3	1	2026-04-29 20:04:14.728052+00	2026-05-12 21:43:06.199985+00
2	REP-00000002	6	2	2026-05-02 15:05:02.629+00	\N	\N	Impresión defectuosa	sin bandeja posterior	sin cables, falta bandeja posterior	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	4	1	2026-05-02 15:09:52.561565+00	2026-05-12 21:44:29.327297+00
3	REP-00000003	7	2	2026-05-02 15:09:53.003+00	\N	\N	teclado no funciona, bisagra rota		cargador no 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	5	1	2026-05-02 15:57:45.99116+00	2026-05-13 22:32:20.439473+00
5	REP-00000005	12	2	2026-05-07 19:58:55.209+00	\N	\N	impresión defectuosa aire en el sistema, tarjeta dañada por cucarachas, se devuelve la maquina		cables no	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	6	1	2026-05-07 20:01:15.424421+00	2026-05-13 23:12:05.742495+00
6	REP-00000006	14	2	2026-05-09 14:48:58.246+00	\N	\N	reparación bisagras, instalar ssd 250 GB 	presupuesto $ 280.000	cargador si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	8	1	2026-05-09 14:52:21.25492+00	2026-05-16 15:46:00.890705+00
10	REP-00000010	20	\N	2026-05-15 15:22:42.979+00	\N	\N	no video 		cargador no 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	9	1	2026-05-15 15:24:54.445707+00	2026-05-16 16:57:11.312546+00
14	REP-00000014	26	2	2026-05-19 20:21:16.917+00	\N	\N	no enciende	reparación electrónica	cargador si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	10	1	2026-05-19 20:23:37.618682+00	2026-05-19 20:25:41.367631+00
15	REP-00000015	27	2	2026-05-19 20:42:09.362+00	\N	\N	problemas de audio 		cargador si	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-05-19 20:44:52.523359+00	2026-05-19 20:44:52.523359+00
16	REP-00000016	28	2	2026-05-20 15:26:15.202+00	\N	\N	IMPRESION DEFECTUOSA		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-05-20 15:28:00.365377+00	2026-05-20 15:28:00.365377+00
11	REP-00000011	21	2	2026-05-15 16:22:22.292+00	\N	\N	revisar  software y se apaga 		cargador 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	11	1	2026-05-15 16:27:24.55707+00	2026-05-22 19:32:39.582485+00
17	REP-00000017	29	2	2026-05-20 20:21:59.754+00	\N	\N	impresión defectuosa		cables no 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	12	1	2026-05-20 20:24:02.299347+00	2026-05-22 21:51:03.921764+00
9	REP-00000009	19	\N	2026-05-15 15:15:21.968+00	\N	\N	impresión defectuosa  magenta		cables no 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	13	1	2026-05-15 15:17:39.163088+00	2026-05-25 17:23:21.176596+00
7	REP-00000007	16	\N	2026-05-11 19:51:14.813+00	\N	\N	NO ENCIENDE		CARGADOR NO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	14	1	2026-05-11 19:53:15.473734+00	2026-05-25 17:30:57.682337+00
18	REP-00000018	31	2	2026-05-26 22:34:42.933+00	\N	\N	BISAGRA IZQUIERDA SOPORTE ROTO	RECOJIO HAROL 	CARGADOR NO 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	15	1	2026-05-26 22:50:52.987177+00	2026-05-26 22:52:18.040642+00
19	REP-00000019	32	2	2026-05-26 23:10:23.519+00	\N	\N	instalar office		cargador si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	17	1	2026-05-26 23:11:55.679044+00	2026-05-26 23:12:30.435935+00
20	REP-00000020	33	2	2026-05-27 15:57:57.098+00	\N	\N	impresion defectuosa		cables no	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	18	1	2026-05-27 17:28:51.309295+00	2026-05-27 17:31:18.779737+00
22	REP-00000022	35	2	2026-05-28 23:00:08.174+00	\N	\N	configuracion correo y office			DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	20	1	2026-05-28 23:01:59.799002+00	2026-05-28 23:04:02.184701+00
21	REP-00000021	34	2	2026-05-27 21:40:38.56+00	\N	\N	BISAGRA ROTA		CARGADOR NO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	21	1	2026-05-27 21:43:19.072132+00	2026-05-28 23:12:24.556802+00
23	REP-00000023	36	2	2026-05-29 19:28:50.382+00	\N	\N	ERROR LED PANEL, SIN TAPAS  TANQUES DE TIBNTA, DERRAME TINTA AZUL 		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-05-29 19:32:25.914448+00	2026-05-29 19:32:25.914448+00
26	REP-00000026	39	2	2026-05-29 20:51:06.653+00	\N	\N	CARGADOR SI 	MANTENIMINETO DE SOFTWARE	PANTALLA  SE COLOCA NEGRA 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	22	1	2026-05-29 21:10:04.234513+00	2026-05-30 17:23:03.413515+00
29	REP-00000029	42	2	2026-05-30 20:07:00.675+00	\N	\N	IMPRESION DEFECTUOSA		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-05-30 20:59:17.962847+00	2026-05-30 20:59:17.962847+00
25	REP-00000025	38	\N	2026-05-29 20:49:19.992+00	\N	\N	IMPRESION  DEFECTUOSA		CABLES NO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	23	1	2026-05-29 20:50:54.20331+00	2026-06-02 22:21:02.397895+00
33	REP-00000033	46	2	2026-06-03 19:39:43.71+00	\N	\N	REVISION 		DCARGADOR NO 	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-03 19:42:52.590144+00	2026-06-03 19:42:52.590144+00
35	REP-00000035	48	2	2026-06-04 13:41:11.048+00	\N	\N	ATASCO		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-04 13:43:16.290404+00	2026-06-04 13:43:16.290404+00
36	REP-00000036	49	2	2026-06-04 15:35:01.704+00	\N	\N	IMPRESION DEFECTUOSA		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-04 15:36:35.55555+00	2026-06-04 15:36:35.55555+00
37	REP-00000037	50	2	2026-06-05 21:46:33.7+00	\N	\N	PANTALLA AZUL ERROR		CARGADOR SI 	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-05 21:49:43.369551+00	2026-06-05 21:49:43.369551+00
38	REP-00000038	51	2	2026-06-05 22:21:20.795+00	\N	\N	IMPRESION DEFECTUOSA		CABLES NO 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	24	1	2026-06-05 22:25:54.538937+00	2026-06-05 22:28:17.175308+00
34	REP-00000034	47	2	2026-06-03 19:59:21.054+00	\N	\N	error tintas		cables si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	25	1	2026-06-03 20:01:07.777992+00	2026-06-05 23:03:20.875153+00
8	REP-00000008	17	\N	2026-05-12 20:19:50.399+00	\N	\N	FALLO EN PANTALLA	SIN SELLOS DE GARANTIA	CARGADOR NO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	26	1	2026-05-12 20:23:18.507443+00	2026-06-06 15:56:40.484509+00
40	REP-00000040	53	2	2026-06-11 15:08:56.723+00	\N	\N	EROR GENERAL		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-11 15:11:04.950898+00	2026-06-11 15:11:04.950898+00
41	REP-00000041	42	2	2026-06-11 15:16:40.472+00	\N	\N	TINTA DE RESIDUO DERRAMADA, IMPRESION DEFECTUOSA		CABLES NO 	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-11 15:19:02.553969+00	2026-06-11 15:19:02.553969+00
42	REP-00000042	54	2	2026-06-11 21:05:51.472+00	\N	\N	IMPRESION DEFECTUOSA, ERROR ALMOHADILLAS		CABLES NO 	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-11 21:07:53.064674+00	2026-06-11 21:07:53.064674+00
46	REP-00000046	58	2	2026-06-16 14:13:28.406+00	\N	\N	NO VIDEO 		CARGADOR SI	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-16 14:15:17.21569+00	2026-06-16 14:15:17.21569+00
45	REP-00000045	57	2	2026-06-13 15:23:55.221+00	\N	\N	REVISION		CARGADOR SI	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	27	1	2026-06-13 15:26:16.112793+00	2026-06-17 22:52:47.613631+00
43	REP-00000043	55	2	2026-06-11 22:17:39.574+00	\N	\N	CARGADOR SI 		NO VIDEO 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	29	1	2026-06-11 22:19:39.066881+00	2026-06-17 23:30:55.08553+00
12	REP-00000012	24	2	2026-05-19 14:28:37.695+00	\N	\N	impresión defectuosa color negro 		cables no	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	32	1	2026-05-19 14:31:04.10549+00	2026-06-18 14:42:43.875931+00
13	REP-00000013	25	2	2026-05-19 19:42:50.893+00	\N	\N	INSTLACION SSD 250 GB SATA Y MANTENIMINETO			DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	33	1	2026-05-19 19:45:29.785728+00	2026-06-18 14:48:07.637794+00
24	REP-00000024	37	2	2026-05-29 20:38:18.845+00	\N	\N	IMPRESION DEFECTUOSA		CABLES NO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	34	1	2026-05-29 20:40:06.985507+00	2026-06-18 14:50:07.511664+00
27	REP-00000027	40	2	2026-05-30 15:56:26.096+00	\N	\N	error no carga sistema operativo		cargador si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	35	1	2026-05-30 15:58:09.986765+00	2026-06-18 14:50:52.769959+00
28	REP-00000028	41	2	2026-05-30 17:18:45.899+00	\N	\N	ERROR ALMOHADILLAS		CABLES SI 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	36	1	2026-05-30 17:20:33.84349+00	2026-06-18 14:53:42.109172+00
30	REP-00000030	43	2	2026-06-01 15:45:35.076+00	\N	\N	MANTENIMINETO DE SOFTWARE		NO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	37	1	2026-06-01 15:48:31.252741+00	2026-06-18 15:00:23.297722+00
31	REP-00000031	44	2	2026-06-03 13:43:17.909+00	\N	\N	REINICIAR PARA ABRIR DOCUMENTOS 		CARGADOR SI	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	38	1	2026-06-03 13:46:49.361186+00	2026-06-18 15:01:08.097229+00
32	REP-00000032	45	2	2026-06-03 15:45:52.905+00	\N	\N	NO VIDEO		CARGADOR SI	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	39	1	2026-06-03 15:47:55.632425+00	2026-06-18 15:06:56.012883+00
47	REP-00000047	59	2	2026-06-17 17:28:43.284+00	\N	\N	NO CARGA SISTEMA OPERATIVO	DETALLES VARIOS	CARGADOR SI 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	41	1	2026-06-17 17:31:11.694209+00	2026-06-20 16:53:59.518895+00
39	REP-00000039	52	2	2026-06-09 15:32:21.392+00	\N	\N	VENTILADOR ATOPE, NO VIDEO 		CARGADOR NO 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	43	1	2026-06-09 22:02:20.981697+00	2026-06-24 20:48:53.986409+00
44	REP-00000044	56	2	2026-06-12 17:04:47.626+00	\N	\N	MANTENIMIENTO HADWARE, CAMBIO PASTA TERMICA, TERMAL PADS 	BISAGRAS FLOJAS	CARGADOR SI	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	28	1	2026-06-12 17:07:49.311398+00	2026-06-17 22:58:19.060762+00
48	REP-00000048	60	2	2026-06-17 20:35:15.591+00	\N	\N	IMPRESION DEFECTUOSA	AIRE EN EL SISTEMA. ALINEACION DE CABEZALES	CABLES NO 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	40	1	2026-06-17 20:46:09.856805+00	2026-06-20 16:31:37.540198+00
50	REP-00000050	65	2	2026-06-22 19:32:44.184+00	\N	\N	REVISION NO CARGA SISTEMA OPERATIVO		CABLE NO 	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-22 19:34:55.385738+00	2026-06-22 19:34:55.385738+00
51	REP-00000051	66	2	2026-06-23 15:17:32.89+00	\N	\N	FUNCIONAMIENTO LENTO		CARGADOR SI	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-23 15:19:10.11355+00	2026-06-23 15:19:10.11355+00
52	REP-00000052	67	2	2026-06-24 15:42:38.808+00	\N	\N	bisagra rota	rota	cargador si	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-24 16:01:05.175699+00	2026-06-24 16:01:05.175699+00
53	REP-00000053	68	2	2026-06-24 17:17:47.323+00	\N	\N	PANTALLA ROTA		CARGADOR NO 	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-24 17:20:21.211249+00	2026-06-24 17:20:21.211249+00
54	REP-00000054	69	2	2026-06-24 21:05:47.942+00	\N	\N	no videoo, cargador roto y punta rota	enviado desde el putumayo	cargador si	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	44	1	2026-06-24 21:08:07.542522+00	2026-06-24 21:09:12.519302+00
49	REP-00000049	63	2	2026-06-19 14:34:02.873+00	\N	\N	IMPRESION DEFECTUOSA		CABLES NO 	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	45	1	2026-06-19 14:35:55.532347+00	2026-06-24 21:17:44.04423+00
56	REP-00000056	71	2	2026-06-25 14:24:05.346+00	\N	\N	NO SE DETECTA PARTICIONES		CABLES NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-25 14:26:25.220731+00	2026-06-25 14:26:25.220731+00
55	REP-00000055	70	2	2026-06-25 14:15:18.977+00	\N	\N	error de almohadillas		cables no	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	46	1	2026-06-25 14:17:06.846189+00	2026-06-25 20:34:53.911611+00
57	REP-00000057	72	2	2026-06-25 20:36:57.015+00	\N	\N	IMPRESION DEFECTUOSA Y TINTAS COLOR VACIAS		NINGUNO	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	47	1	2026-06-25 20:37:52.584668+00	2026-06-25 20:49:32.218383+00
58	REP-00000058	74	2	2026-06-25 20:52:03.235+00	\N	\N	PANTALLA SE VUELBE NEGRA		CARGADOR SI	DELIVERED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	48	1	2026-06-25 20:53:32.827673+00	2026-06-25 20:54:17.173165+00
59	REP-00000059	20	\N	2026-06-26 16:04:05.205+00	\N	\N	MANTENIMIENTO IMPRESION DEFECTUOSA		NO	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-26 16:06:29.916197+00	2026-06-26 16:06:29.916197+00
60	REP-00000060	77	\N	2026-06-26 20:58:42.959+00	\N	\N	reprara bandeja, atasco de papel	bandeja rota	cables	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-26 21:01:16.765438+00	2026-06-26 21:01:16.765438+00
61	REP-00000061	78	2	2026-06-27 19:29:11.509+00	\N	\N	se apaga		no	RECEIVED	f	0.00	0.00	0.00	COP	\N	\N	BORRADOR	\N	\N	1	2026-06-27 19:33:33.579854+00	2026-06-27 19:33:33.579854+00
\.


--
-- Data for Name: technicians; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.technicians (id, employee_id, first_name, last_name, specialty, is_active, company_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: treasury_transactions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.treasury_transactions (id, company_id, account_type, bank_account_id, cash_account_id, transaction_type, amount, currency, description, reference, reference_type, reference_id, journal_entry_id, balance_after, created_by, created_at) FROM stdin;
2	1	BANK	1	\N	WITHDRAWAL	700000.00	COP	dinero por mantenimineto 	0001 Roberth	\N	\N	9	3979000.00	\N	2026-05-04 22:15:18.590474+00
3	1	BANK	1	\N	WITHDRAWAL	320000.00	COP	pago nu	REPAIR-JE-12	\N	\N	12	3659000.00	\N	2026-05-04 22:15:18.590474+00
4	1	BANK	1	\N	WITHDRAWAL	300000.00	COP	pago adelanto german	viaje	\N	\N	13	3359000.00	\N	2026-05-04 22:15:18.590474+00
5	1	CASH	\N	1	DEPOSIT	100000.00	COP	 montoinicial		\N	\N	17	100000.00	1	2026-05-05 23:17:30.834949+00
7	1	CASH	\N	1	DEPOSIT	2000000.00	COP	abono a caja mayo 06		\N	\N	20	2075000.00	1	2026-05-06 22:27:11.446743+00
8	1	CASH	\N	1	DEPOSIT	150000.00	COP	Pago - Factura INV-00000002	INV-2	\N	\N	\N	2225000.00	\N	2026-05-12 21:03:22.659168+00
9	1	BANK	1	\N	WITHDRAWAL	900000.00	COP	pago arriendo	Pago arriendo	\N	\N	22	2459000.00	\N	2026-05-12 21:06:45.767644+00
10	1	CASH	\N	1	DEPOSIT	72000.00	COP	Pago - Factura INV-00000004	INV-4	\N	\N	\N	2297000.00	\N	2026-05-12 21:44:29.435286+00
11	1	CASH	\N	1	WITHDRAWAL	158823.00	COP	Pago a proveedor - Factura ATPE 100220	Auto-ATPE 100220	\N	\N	25	2138177.00	\N	2026-05-12 23:16:01.84872+00
12	1	CASH	\N	1	WITHDRAWAL	75000.00	COP	Pago a proveedor - Factura tp00002	Auto-tp00002	\N	\N	26	2063177.00	\N	2026-05-12 23:20:57.494723+00
13	1	BANK	1	\N	DEPOSIT	220000.00	COP	Pago - Factura INV-00000005	INV-5	\N	\N	\N	2679000.00	\N	2026-05-13 22:32:20.579634+00
14	1	BANK	1	\N	WITHDRAWAL	1899000.00	COP	Pago a proveedor - Factura 88357	Auto-88357	\N	\N	29	780000.00	\N	2026-05-15 23:18:44.222559+00
15	1	CASH	\N	1	DEPOSIT	250000.00	COP	Pago - Factura INV-00000010	INV-10	\N	\N	\N	2313177.00	\N	2026-05-19 20:25:41.451073+00
17	1	BANK	1	\N	DEPOSIT	60000.00	COP	Pago - Factura INV-00000011	INV-11	\N	\N	\N	840000.00	\N	2026-05-22 19:32:39.744816+00
18	1	BANK	1	\N	DEPOSIT	60000.00	COP	Pago - Factura INV-00000012	INV-12	\N	\N	\N	900000.00	\N	2026-05-22 21:51:04.02887+00
20	1	CASH	\N	1	DEPOSIT	60000.00	COP	Pago - Factura INV-00000013	INV-13	\N	\N	\N	2193177.00	\N	2026-05-25 17:23:21.370325+00
21	1	CASH	\N	1	WITHDRAWAL	436548.00	COP	Pago a proveedor - Factura FECO 66687	Auto-FECO 66687	\N	\N	42	1756629.00	\N	2026-05-25 21:47:17.160998+00
6	1	CASH	\N	1	WITHDRAWAL	25000.00	COP	Stock inicial - Toner laser generico 85A 35A 36A	SI-000014	\N	\N	18	75000.00	\N	2026-05-05 23:19:14.382308+00
16	1	CASH	\N	1	WITHDRAWAL	180000.00	COP	Stock inicial - SSD ADATA 250 GB	SI-000031	\N	\N	34	2133177.00	\N	2026-05-19 22:41:34.788726+00
19	1	BANK	1	\N	WITHDRAWAL	480000.00	COP	Stock inicial - Portatil asus  	SI-000033	\N	\N	38	420000.00	\N	2026-05-22 22:02:10.31454+00
22	1	CASH	\N	1	DEPOSIT	80000.00	COP	Pago - Factura INV-00000015	INV-15	\N	\N	\N	1836629.00	\N	2026-05-26 22:52:18.145104+00
23	1	BANK	1	\N	DEPOSIT	2200000.00	COP	PAGO FONDO COEMPRENDER	BANCOLOMBIA	\N	\N	44	2620000.00	1	2026-05-26 22:53:16.023603+00
24	1	BANK	1	\N	DEPOSIT	3000000.00	COP	ANTICIPO TODO EN UNO	WAL-2-3	\N	\N	45	5620000.00	2	2026-05-26 23:00:48.35089+00
25	1	BANK	1	\N	WITHDRAWAL	2700000.00	COP	DEVOLUCION	WAL-2-4	\N	\N	46	2920000.00	1	2026-05-26 23:01:43.092323+00
26	1	CASH	\N	1	DEPOSIT	400000.00	COP	Pago - Factura INV-00000016	INV-16	\N	\N	\N	2236629.00	\N	2026-05-26 23:03:16.010905+00
27	1	CASH	\N	1	DEPOSIT	70000.00	COP	Pago - Factura INV-00000017	INV-17	\N	\N	\N	2306629.00	\N	2026-05-26 23:12:30.51845+00
28	1	CASH	\N	1	DEPOSIT	90000.00	COP	pago internet	pago internet local	\N	\N	49	2396629.00	\N	2026-05-27 17:07:06.73978+00
29	1	CASH	\N	1	WITHDRAWAL	90000.00	COP	pago interner	pago internet local	\N	\N	49	2306629.00	\N	2026-05-27 17:07:06.73978+00
30	1	BANK	1	\N	DEPOSIT	355000.00	COP	Pago - Factura INV-00000018	INV-18	\N	\N	\N	3275000.00	\N	2026-05-27 17:31:18.931108+00
31	1	CASH	\N	1	WITHDRAWAL	1.00	COP	Stock inicial - producto prueba	SI-000049	\N	\N	\N	2306628.00	\N	2026-05-27 23:27:12.395629+00
32	1	CASH	\N	1	DEPOSIT	2.00	COP	Pago - Factura INV-00000019	INV-19	\N	\N	\N	2306630.00	\N	2026-05-27 23:27:49.993367+00
33	1	CASH	\N	1	DEPOSIT	90000.00	COP	Pago - Factura INV-00000020	INV-20	\N	\N	\N	2396630.00	\N	2026-05-28 23:04:02.278165+00
34	1	CASH	\N	1	DEPOSIT	80000.00	COP	Pago - Factura INV-00000021	INV-21	\N	\N	\N	2476630.00	\N	2026-05-28 23:12:24.639267+00
35	1	CASH	\N	1	DEPOSIT	60000.00	COP	Pago - Factura INV-00000022	INV-22	\N	\N	\N	2536630.00	\N	2026-05-30 17:23:03.495968+00
36	1	CASH	\N	1	WITHDRAWAL	50000.00	COP	Pago stock inicial - Caja de Mantenimiento Epson L5590	PUR-000024	\N	\N	\N	2486630.00	\N	2026-06-01 23:17:45.826613+00
37	1	CASH	\N	1	WITHDRAWAL	20000.00	COP	Stock inicial - Teclado genérico usb	SI-000060	\N	\N	\N	2466630.00	\N	2026-06-01 23:19:04.278394+00
38	1	CASH	\N	1	DEPOSIT	90000.00	COP	Pago - Factura INV-00000023	INV-23	\N	\N	\N	2556630.00	\N	2026-06-02 22:21:02.501407+00
39	1	BANK	1	\N	WITHDRAWAL	90000.00	COP	pago internet	JE-59	\N	\N	59	3185000.00	\N	2026-06-02 23:21:05.861678+00
40	1	CASH	\N	1	WITHDRAWAL	237000.00	COP	pago trasporte	JE-60	\N	\N	60	2319630.00	\N	2026-06-02 23:26:21.270521+00
41	1	CASH	\N	1	DEPOSIT	450000.00	COP	Pago - Factura INV-00000026	INV-26	\N	\N	\N	2769630.00	\N	2026-06-06 15:56:40.613791+00
42	1	BANK	1	\N	WITHDRAWAL	920000.00	COP	pago arriendo local	JE-64	\N	\N	64	2265000.00	\N	2026-06-17 22:33:02.49837+00
43	1	BANK	1	\N	WITHDRAWAL	400000.00	COP	Stock inicial - PORTATIL DELL CORE I5 DOCEAVA	SI-000061	\N	\N	\N	1865000.00	\N	2026-06-17 22:40:05.00826+00
44	1	BANK	1	\N	DEPOSIT	120000.00	COP	Pago - Factura INV-00000027	INV-27	\N	\N	\N	1985000.00	\N	2026-06-17 22:52:47.810408+00
45	1	CASH	\N	1	DEPOSIT	120000.00	COP	Pago - Factura INV-00000028	INV-28	\N	\N	\N	2889630.00	\N	2026-06-17 22:58:19.157539+00
46	1	BANK	1	\N	WITHDRAWAL	220000.00	COP	Stock inicial - Portatil ACER Aspire Core i5 cuarta generación	SI-000062	\N	\N	\N	1765000.00	\N	2026-06-17 23:03:30.144914+00
47	1	BANK	1	\N	WITHDRAWAL	188020.00	COP	Pago a proveedor - Factura ATPE 100488	Auto-ATPE 100488	\N	\N	70	1576980.00	\N	2026-06-17 23:28:23.597042+00
48	1	CASH	\N	1	DEPOSIT	340000.00	COP	Pago - Factura INV-00000029	INV-29	\N	\N	\N	3229630.00	\N	2026-06-17 23:30:55.214806+00
49	1	CASH	\N	1	WITHDRAWAL	188999.37	COP	Pago a proveedor - Factura 100508	Auto-100508	\N	\N	73	3040630.63	\N	2026-06-18 14:13:04.684177+00
50	1	BANK	1	\N	DEPOSIT	1200000.00	COP	Pago - Factura INV-00000030	INV-30	\N	\N	\N	2776980.00	\N	2026-06-18 14:21:31.673889+00
51	1	CASH	\N	1	WITHDRAWAL	10000.00	COP	Stock inicial - memoria RAM DDR3 4 GB USADA	SI-000064	\N	\N	\N	3030630.63	\N	2026-06-18 14:25:00.180561+00
52	1	CASH	\N	1	DEPOSIT	40000.00	COP	Pago - Factura INV-00000031	INV-31	\N	\N	\N	3070630.63	\N	2026-06-18 14:26:16.198038+00
53	1	CASH	\N	1	DEPOSIT	60000.00	COP	Pago - Factura INV-00000032	INV-32	\N	\N	\N	3130630.63	\N	2026-06-18 14:42:43.994117+00
54	1	CASH	\N	1	DEPOSIT	300000.00	COP	Pago - Factura INV-00000033	INV-33	\N	\N	\N	3430630.63	\N	2026-06-18 14:48:07.722682+00
55	1	CASH	\N	1	DEPOSIT	120000.00	COP	Pago - Factura INV-00000034	INV-34	\N	\N	\N	3550630.63	\N	2026-06-18 14:50:07.596539+00
56	1	CASH	\N	1	DEPOSIT	80000.00	COP	Pago - Factura INV-00000035	INV-35	\N	\N	\N	3630630.63	\N	2026-06-18 14:50:52.852465+00
57	1	BANK	1	\N	WITHDRAWAL	50000.00	COP	Pago a proveedor - Factura SI-PUR-1780355865-59		\N	\N	81	2726980.00	\N	2026-06-18 14:52:52.836905+00
58	1	CASH	\N	1	DEPOSIT	70000.00	COP	Pago - Factura INV-00000036	INV-36	\N	\N	\N	3700630.63	\N	2026-06-18 14:53:42.240544+00
59	1	BANK	1	\N	WITHDRAWAL	450000.00	COP	Pago stock inicial - Portátil hp Core i5 onceava generación	PUR-000027	\N	\N	\N	2276980.00	\N	2026-06-18 14:59:26.138205+00
60	1	CASH	\N	1	DEPOSIT	60000.00	COP	Pago - Factura INV-00000038	INV-38	\N	\N	\N	3760630.63	\N	2026-06-18 15:01:08.17974+00
61	1	CASH	\N	1	WITHDRAWAL	30000.00	COP	Stock inicial - Servicio reparación electronica	SI-000067	\N	\N	\N	3730630.63	\N	2026-06-18 15:04:36.91396+00
62	1	CASH	\N	1	DEPOSIT	150000.00	COP	Pago - Factura INV-00000039	INV-39	\N	\N	\N	3880630.63	\N	2026-06-18 15:06:56.131079+00
63	1	CASH	\N	1	DEPOSIT	280000.00	COP	Pago - Factura INV-00000041	INV-41	\N	\N	\N	4160630.63	\N	2026-06-20 16:53:59.648078+00
64	1	CASH	\N	1	DEPOSIT	70000.00	COP	Pago - Factura INV-00000042	INV-42	\N	\N	\N	4230630.63	\N	2026-06-20 17:02:04.785278+00
65	1	CASH	\N	1	WITHDRAWAL	90000.00	COP	Pago a proveedor - Factura 3899	Auto-3899	\N	\N	93	3690630.63	\N	2026-06-23 23:19:02.071887+00
66	1	CASH	\N	1	DEPOSIT	330000.00	COP	Pago - Factura INV-00000043	INV-000043	\N	\N	\N	3780630.63	\N	2026-06-24 20:48:53.986409+00
67	1	CASH	\N	1	WITHDRAWAL	90000.00	COP	Stock inicial - Reparación electrónica portátil Asus	SI-000073	\N	\N	\N	3690630.63	\N	2026-06-24 21:01:26.121068+00
68	1	CASH	\N	1	WITHDRAWAL	10000.00	COP	Stock inicial - reparación cargador Asus	SI-000074	\N	\N	\N	3680630.63	\N	2026-06-24 21:04:21.477327+00
70	1	CASH	\N	1	DEPOSIT	60000.00	COP	Pago - Factura INV-00000045	INV-000045	\N	\N	\N	3740630.63	\N	2026-06-24 21:17:44.04423+00
69	1	BANK	1	\N	DEPOSIT	260000.00	COP	Pago - Factura INV-00000044	INV-000044	\N	\N	\N	2536980.00	\N	2026-06-24 21:09:12.519302+00
71	1	BANK	1	\N	WITHDRAWAL	520000.00	COP	Pago Salud y pension	JE-102	\N	\N	102	2016980.00	\N	2026-06-24 22:18:24.419791+00
72	1	CASH	\N	1	WITHDRAWAL	100000.00	COP	gym	JE-103	\N	\N	103	3640630.63	\N	2026-06-25 20:30:40.590274+00
73	1	CASH	\N	1	WITHDRAWAL	300000.00	COP	gastos varios casa	JE-104	\N	\N	104	3340630.63	\N	2026-06-25 20:33:18.291295+00
74	1	CASH	\N	1	DEPOSIT	60000.00	COP	Pago - Factura INV-00000046	INV-000046	\N	\N	\N	3400630.63	\N	2026-06-25 20:34:53.911611+00
75	1	BANK	1	\N	WITHDRAWAL	16000.00	COP	Pago a proveedor - Factura 0001	Auto-0001	\N	\N	107	2000980.00	\N	2026-06-25 20:47:52.631244+00
76	1	CASH	\N	1	DEPOSIT	104999.97	COP	Pago - Factura INV-00000047	INV-000047	\N	\N	\N	3505630.60	\N	2026-06-25 20:49:32.218383+00
77	1	BANK	1	\N	DEPOSIT	70000.00	COP	Pago - Factura INV-00000048	INV-000048	\N	\N	\N	2070980.00	\N	2026-06-25 20:54:17.173165+00
78	1	BANK	1	\N	DEPOSIT	600000.00	COP	Pago - Factura INV-00000049	INV-000049	\N	\N	\N	2670980.00	\N	2026-06-25 20:59:14.864093+00
79	1	BANK	1	\N	WITHDRAWAL	288987.93	COP	Pago a proveedor - Factura ATPE 100487	Auto-ATPE 100487	\N	\N	112	2381992.07	\N	2026-06-25 21:14:45.196329+00
80	1	CASH	\N	1	DEPOSIT	300000.00	COP	Pago - Factura INV-00000050	INV-000050	\N	\N	\N	3805630.60	\N	2026-06-25 21:17:24.702376+00
81	1	CASH	\N	1	DEPOSIT	50000.00	COP	Pago - Factura INV-00000051	INV-000051	\N	\N	\N	3855630.60	\N	2026-06-25 21:49:38.887325+00
\.


--
-- Data for Name: user_permissions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.user_permissions (user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.users (id, email, username, hashed_password, full_name, role, is_active, is_superuser, company_id, hashed_refresh_token, created_at, updated_at) FROM stdin;
2	geralexcas@gmail.com	geralexcas	$2b$12$sEGAoVN6x5/JWVolXEEtiucmHBMs2NPhbz4nQVUXckKo1KR6ajyp2	German Alexander Castillo	TECNICO	t	f	1	$2b$12$XwavGl83Nk.VpT0BubnSSuTinK.EwCXvRhUtx7gMfLTah/mMbplaO	2026-04-29 19:40:49.889996+00	2026-06-27 16:10:44.900904+00
1	admin@reloadmatrix.com	admin	$2b$12$dCb2fX5mpan9d.cYAsrtE.I8jkokgGH39ldxU8HI3ILbur.dNky3W	Administrador Sistema	ADMINISTRADOR	t	t	\N	$2b$12$JxUxUaoijVE/O.thYImU5.Ef4vTn6CeBCATZwrh0pede3oaeppUNa	2026-04-28 21:24:07.289848+00	2026-06-27 20:46:46.065833+00
\.


--
-- Data for Name: wallet_transactions; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.wallet_transactions (id, wallet_id, transaction_type, amount, description, reference_type, reference_id, balance_after, created_at) FROM stdin;
1	1	DEPOSIT	2100000.00	anticipo portátil Asus Ryzen 7	\N	\N	2100000.00	2026-05-15 23:06:53.403105+00
2	1	WITHDRAWAL	2100000.00	Aplicación parcial a Factura INV-00000007	\N	\N	0.00	2026-05-15 23:21:01.172085+00
3	2	DEPOSIT	3000000.00	ANTICIPO TODO EN UNO	\N	\N	3000000.00	2026-05-26 23:00:48.123389+00
4	2	WITHDRAWAL	2700000.00	DEVOLUCION	\N	\N	300000.00	2026-05-26 23:01:42.95952+00
5	2	WITHDRAWAL	300000.00	Aplicación parcial a Factura INV-00000016	\N	\N	0.00	2026-05-26 23:03:15.941611+00
\.


--
-- Data for Name: wallets; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.wallets (id, partner_id, user_id, balance, loyalty_points, currency, is_active, company_id, created_at, updated_at) FROM stdin;
1	22	\N	0.00	0.00	COP	t	1	2026-05-15 23:05:46.654512+00	2026-05-15 23:21:01.172085+00
2	21	\N	0.00	0.00	COP	t	1	2026-05-26 23:00:00.058685+00	2026-05-26 23:03:15.941611+00
\.


--
-- Data for Name: warranties; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.warranties (id, repair_order_id, repair_item_id, company_id, warranty_type, start_date, end_date, status, description, terms_and_conditions, claim_date, claim_description, claim_resolution, created_at, updated_at) FROM stdin;
\.


--
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- Name: bank_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.bank_accounts_id_seq', 1, true);


--
-- Name: bank_reconciliations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.bank_reconciliations_id_seq', 1, false);


--
-- Name: cash_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.cash_accounts_id_seq', 1, true);


--
-- Name: chart_of_accounts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.chart_of_accounts_id_seq', 63, true);


--
-- Name: check_register_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.check_register_id_seq', 1, false);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.companies_id_seq', 1, true);


--
-- Name: credit_debit_notes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.credit_debit_notes_id_seq', 1, false);


--
-- Name: dian_billing_ranges_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.dian_billing_ranges_id_seq', 1, false);


--
-- Name: fiscal_periods_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.fiscal_periods_id_seq', 1, false);


--
-- Name: inventory_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.inventory_movements_id_seq', 5, true);


--
-- Name: invoice_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.invoice_items_id_seq', 70, true);


--
-- Name: invoice_resolutions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.invoice_resolutions_id_seq', 2, true);


--
-- Name: invoices_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.invoices_id_seq', 51, true);


--
-- Name: journal_entries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.journal_entries_id_seq', 114, true);


--
-- Name: journal_entry_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.journal_entry_lines_id_seq', 328, true);


--
-- Name: partners_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.partners_id_seq', 78, true);


--
-- Name: permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.permissions_id_seq', 1, false);


--
-- Name: product_price_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.product_price_history_id_seq', 5, true);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.products_id_seq', 78, true);


--
-- Name: purchase_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchase_items_id_seq', 28, true);


--
-- Name: purchase_payments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchase_payments_id_seq', 11, true);


--
-- Name: purchases_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.purchases_id_seq', 33, true);


--
-- Name: reconciliation_lines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.reconciliation_lines_id_seq', 1, false);


--
-- Name: repair_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.repair_items_id_seq', 61, true);


--
-- Name: repair_orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.repair_orders_id_seq', 61, true);


--
-- Name: technicians_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.technicians_id_seq', 1, false);


--
-- Name: treasury_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.treasury_transactions_id_seq', 81, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.users_id_seq', 2, true);


--
-- Name: wallet_transactions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.wallet_transactions_id_seq', 5, true);


--
-- Name: wallets_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.wallets_id_seq', 2, true);


--
-- Name: warranties_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.warranties_id_seq', 1, false);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: bank_accounts bank_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_pkey PRIMARY KEY (id);


--
-- Name: bank_reconciliations bank_reconciliations_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_pkey PRIMARY KEY (id);


--
-- Name: cash_accounts cash_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_accounts
    ADD CONSTRAINT cash_accounts_pkey PRIMARY KEY (id);


--
-- Name: chart_of_accounts chart_of_accounts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT chart_of_accounts_pkey PRIMARY KEY (id);


--
-- Name: check_register check_register_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.check_register
    ADD CONSTRAINT check_register_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: credit_debit_notes credit_debit_notes_note_number_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.credit_debit_notes
    ADD CONSTRAINT credit_debit_notes_note_number_key UNIQUE (note_number);


--
-- Name: credit_debit_notes credit_debit_notes_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.credit_debit_notes
    ADD CONSTRAINT credit_debit_notes_pkey PRIMARY KEY (id);


--
-- Name: dian_billing_ranges dian_billing_ranges_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.dian_billing_ranges
    ADD CONSTRAINT dian_billing_ranges_pkey PRIMARY KEY (id);


--
-- Name: fiscal_periods fiscal_periods_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.fiscal_periods
    ADD CONSTRAINT fiscal_periods_pkey PRIMARY KEY (id);


--
-- Name: inventory_movements inventory_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_pkey PRIMARY KEY (id);


--
-- Name: invoice_items invoice_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_pkey PRIMARY KEY (id);


--
-- Name: invoice_resolutions invoice_resolutions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_resolutions
    ADD CONSTRAINT invoice_resolutions_pkey PRIMARY KEY (id);


--
-- Name: invoices invoices_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_pkey PRIMARY KEY (id);


--
-- Name: journal_entries journal_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_pkey PRIMARY KEY (id);


--
-- Name: journal_entry_lines journal_entry_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT journal_entry_lines_pkey PRIMARY KEY (id);


--
-- Name: partners partners_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_name_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_name_key UNIQUE (name);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: product_price_history product_price_history_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_price_history
    ADD CONSTRAINT product_price_history_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: purchase_items purchase_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_pkey PRIMARY KEY (id);


--
-- Name: purchase_payments purchase_payments_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_payments
    ADD CONSTRAINT purchase_payments_pkey PRIMARY KEY (id);


--
-- Name: purchases purchases_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_pkey PRIMARY KEY (id);


--
-- Name: reconciliation_lines reconciliation_lines_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.reconciliation_lines
    ADD CONSTRAINT reconciliation_lines_pkey PRIMARY KEY (id);


--
-- Name: repair_items repair_items_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_items
    ADD CONSTRAINT repair_items_pkey PRIMARY KEY (id);


--
-- Name: repair_orders repair_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_orders
    ADD CONSTRAINT repair_orders_pkey PRIMARY KEY (id);


--
-- Name: technicians technicians_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.technicians
    ADD CONSTRAINT technicians_pkey PRIMARY KEY (id);


--
-- Name: treasury_transactions treasury_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions
    ADD CONSTRAINT treasury_transactions_pkey PRIMARY KEY (id);


--
-- Name: invoice_resolutions uq_active_resolution_per_company_type; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_resolutions
    ADD CONSTRAINT uq_active_resolution_per_company_type UNIQUE (company_id, resolution_type, is_active);


--
-- Name: chart_of_accounts uq_chart_code_company; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT uq_chart_code_company UNIQUE (code, company_id);


--
-- Name: invoices uq_invoice_number_per_company; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT uq_invoice_number_per_company UNIQUE (company_id, invoice_number);


--
-- Name: products uq_product_barcode_company; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT uq_product_barcode_company UNIQUE (barcode, company_id);


--
-- Name: products uq_product_sku_company; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT uq_product_sku_company UNIQUE (sku, company_id);


--
-- Name: user_permissions user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_pkey PRIMARY KEY (user_id, permission_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: wallet_transactions wallet_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_pkey PRIMARY KEY (id);


--
-- Name: wallets wallets_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_pkey PRIMARY KEY (id);


--
-- Name: warranties warranties_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warranties
    ADD CONSTRAINT warranties_pkey PRIMARY KEY (id);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_bank_accounts_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_bank_accounts_company_id ON public.bank_accounts USING btree (company_id);


--
-- Name: ix_bank_accounts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_bank_accounts_id ON public.bank_accounts USING btree (id);


--
-- Name: ix_bank_reconciliations_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_bank_reconciliations_company_id ON public.bank_reconciliations USING btree (company_id);


--
-- Name: ix_bank_reconciliations_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_bank_reconciliations_id ON public.bank_reconciliations USING btree (id);


--
-- Name: ix_cash_accounts_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_cash_accounts_company_id ON public.cash_accounts USING btree (company_id);


--
-- Name: ix_cash_accounts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_cash_accounts_id ON public.cash_accounts USING btree (id);


--
-- Name: ix_chart_of_accounts_code; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_chart_of_accounts_code ON public.chart_of_accounts USING btree (code);


--
-- Name: ix_chart_of_accounts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_chart_of_accounts_id ON public.chart_of_accounts USING btree (id);


--
-- Name: ix_check_register_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_check_register_company_id ON public.check_register USING btree (company_id);


--
-- Name: ix_check_register_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_check_register_id ON public.check_register USING btree (id);


--
-- Name: ix_companies_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_companies_id ON public.companies USING btree (id);


--
-- Name: ix_companies_nit; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_companies_nit ON public.companies USING btree (nit);


--
-- Name: ix_credit_debit_notes_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_credit_debit_notes_id ON public.credit_debit_notes USING btree (id);


--
-- Name: ix_dian_billing_ranges_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_dian_billing_ranges_id ON public.dian_billing_ranges USING btree (id);


--
-- Name: ix_fiscal_periods_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_fiscal_periods_company_id ON public.fiscal_periods USING btree (company_id);


--
-- Name: ix_fiscal_periods_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_fiscal_periods_id ON public.fiscal_periods USING btree (id);


--
-- Name: ix_inventory_movements_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_inventory_movements_company_id ON public.inventory_movements USING btree (company_id);


--
-- Name: ix_inventory_movements_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_inventory_movements_id ON public.inventory_movements USING btree (id);


--
-- Name: ix_inventory_movements_product_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_inventory_movements_product_id ON public.inventory_movements USING btree (product_id);


--
-- Name: ix_invoice_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_invoice_items_id ON public.invoice_items USING btree (id);


--
-- Name: ix_invoice_resolutions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_invoice_resolutions_id ON public.invoice_resolutions USING btree (id);


--
-- Name: ix_invoices_cufe; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_invoices_cufe ON public.invoices USING btree (cufe);


--
-- Name: ix_invoices_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_invoices_id ON public.invoices USING btree (id);


--
-- Name: ix_invoices_invoice_number; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_invoices_invoice_number ON public.invoices USING btree (invoice_number);


--
-- Name: ix_journal_entries_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_journal_entries_id ON public.journal_entries USING btree (id);


--
-- Name: ix_journal_entry_lines_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_journal_entry_lines_id ON public.journal_entry_lines USING btree (id);


--
-- Name: ix_partners_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_partners_id ON public.partners USING btree (id);


--
-- Name: ix_partners_nit; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_partners_nit ON public.partners USING btree (nit);


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);


--
-- Name: ix_product_price_history_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_product_price_history_company_id ON public.product_price_history USING btree (company_id);


--
-- Name: ix_product_price_history_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_product_price_history_id ON public.product_price_history USING btree (id);


--
-- Name: ix_product_price_history_product_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_product_price_history_product_id ON public.product_price_history USING btree (product_id);


--
-- Name: ix_products_barcode; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_products_barcode ON public.products USING btree (barcode);


--
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_products_id ON public.products USING btree (id);


--
-- Name: ix_products_sku; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_products_sku ON public.products USING btree (sku);


--
-- Name: ix_purchase_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_items_id ON public.purchase_items USING btree (id);


--
-- Name: ix_purchase_payments_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchase_payments_id ON public.purchase_payments USING btree (id);


--
-- Name: ix_purchases_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_purchases_id ON public.purchases USING btree (id);


--
-- Name: ix_purchases_purchase_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_purchases_purchase_number ON public.purchases USING btree (purchase_number);


--
-- Name: ix_reconciliation_lines_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_reconciliation_lines_id ON public.reconciliation_lines USING btree (id);


--
-- Name: ix_repair_items_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_repair_items_id ON public.repair_items USING btree (id);


--
-- Name: ix_repair_orders_cufe; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_repair_orders_cufe ON public.repair_orders USING btree (cufe);


--
-- Name: ix_repair_orders_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_repair_orders_id ON public.repair_orders USING btree (id);


--
-- Name: ix_repair_orders_order_number; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_repair_orders_order_number ON public.repair_orders USING btree (order_number);


--
-- Name: ix_technicians_employee_id; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_technicians_employee_id ON public.technicians USING btree (employee_id);


--
-- Name: ix_technicians_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_technicians_id ON public.technicians USING btree (id);


--
-- Name: ix_treasury_transactions_company_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_treasury_transactions_company_id ON public.treasury_transactions USING btree (company_id);


--
-- Name: ix_treasury_transactions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_treasury_transactions_id ON public.treasury_transactions USING btree (id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_wallet_transactions_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_wallet_transactions_id ON public.wallet_transactions USING btree (id);


--
-- Name: ix_wallets_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_wallets_id ON public.wallets USING btree (id);


--
-- Name: ix_warranties_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_warranties_id ON public.warranties USING btree (id);


--
-- Name: audit_logs audit_logs_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: bank_accounts bank_accounts_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: bank_accounts bank_accounts_linked_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_accounts
    ADD CONSTRAINT bank_accounts_linked_account_id_fkey FOREIGN KEY (linked_account_id) REFERENCES public.chart_of_accounts(id);


--
-- Name: bank_reconciliations bank_reconciliations_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id);


--
-- Name: bank_reconciliations bank_reconciliations_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: bank_reconciliations bank_reconciliations_reconciled_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.bank_reconciliations
    ADD CONSTRAINT bank_reconciliations_reconciled_by_fkey FOREIGN KEY (reconciled_by) REFERENCES public.users(id);


--
-- Name: cash_accounts cash_accounts_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_accounts
    ADD CONSTRAINT cash_accounts_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: cash_accounts cash_accounts_linked_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_accounts
    ADD CONSTRAINT cash_accounts_linked_account_id_fkey FOREIGN KEY (linked_account_id) REFERENCES public.chart_of_accounts(id);


--
-- Name: cash_accounts cash_accounts_responsible_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.cash_accounts
    ADD CONSTRAINT cash_accounts_responsible_user_id_fkey FOREIGN KEY (responsible_user_id) REFERENCES public.users(id);


--
-- Name: chart_of_accounts chart_of_accounts_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT chart_of_accounts_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: chart_of_accounts chart_of_accounts_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.chart_of_accounts
    ADD CONSTRAINT chart_of_accounts_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.chart_of_accounts(id);


--
-- Name: check_register check_register_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.check_register
    ADD CONSTRAINT check_register_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id);


--
-- Name: check_register check_register_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.check_register
    ADD CONSTRAINT check_register_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: check_register check_register_linked_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.check_register
    ADD CONSTRAINT check_register_linked_transaction_id_fkey FOREIGN KEY (linked_transaction_id) REFERENCES public.treasury_transactions(id);


--
-- Name: credit_debit_notes credit_debit_notes_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.credit_debit_notes
    ADD CONSTRAINT credit_debit_notes_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: credit_debit_notes credit_debit_notes_original_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.credit_debit_notes
    ADD CONSTRAINT credit_debit_notes_original_invoice_id_fkey FOREIGN KEY (original_invoice_id) REFERENCES public.invoices(id);


--
-- Name: dian_billing_ranges dian_billing_ranges_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.dian_billing_ranges
    ADD CONSTRAINT dian_billing_ranges_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: fiscal_periods fiscal_periods_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.fiscal_periods
    ADD CONSTRAINT fiscal_periods_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: inventory_movements inventory_movements_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: inventory_movements inventory_movements_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: invoice_items invoice_items_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: invoice_items invoice_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_items
    ADD CONSTRAINT invoice_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: invoice_resolutions invoice_resolutions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoice_resolutions
    ADD CONSTRAINT invoice_resolutions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: invoices invoices_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: invoices invoices_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.invoices
    ADD CONSTRAINT invoices_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: journal_entries journal_entries_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entries
    ADD CONSTRAINT journal_entries_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: journal_entry_lines journal_entry_lines_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT journal_entry_lines_account_id_fkey FOREIGN KEY (account_id) REFERENCES public.chart_of_accounts(id);


--
-- Name: journal_entry_lines journal_entry_lines_journal_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.journal_entry_lines
    ADD CONSTRAINT journal_entry_lines_journal_entry_id_fkey FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id);


--
-- Name: partners partners_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.partners
    ADD CONSTRAINT partners_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: product_price_history product_price_history_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_price_history
    ADD CONSTRAINT product_price_history_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: product_price_history product_price_history_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.product_price_history
    ADD CONSTRAINT product_price_history_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: products products_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: products products_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.partners(id);


--
-- Name: purchase_items purchase_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: purchase_items purchase_items_purchase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_items
    ADD CONSTRAINT purchase_items_purchase_id_fkey FOREIGN KEY (purchase_id) REFERENCES public.purchases(id);


--
-- Name: purchase_payments purchase_payments_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_payments
    ADD CONSTRAINT purchase_payments_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: purchase_payments purchase_payments_purchase_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchase_payments
    ADD CONSTRAINT purchase_payments_purchase_id_fkey FOREIGN KEY (purchase_id) REFERENCES public.purchases(id);


--
-- Name: purchases purchases_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: purchases purchases_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: purchases purchases_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.purchases
    ADD CONSTRAINT purchases_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: reconciliation_lines reconciliation_lines_reconciliation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.reconciliation_lines
    ADD CONSTRAINT reconciliation_lines_reconciliation_id_fkey FOREIGN KEY (reconciliation_id) REFERENCES public.bank_reconciliations(id);


--
-- Name: reconciliation_lines reconciliation_lines_treasury_transaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.reconciliation_lines
    ADD CONSTRAINT reconciliation_lines_treasury_transaction_id_fkey FOREIGN KEY (treasury_transaction_id) REFERENCES public.treasury_transactions(id);


--
-- Name: repair_items repair_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_items
    ADD CONSTRAINT repair_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: repair_items repair_items_repair_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_items
    ADD CONSTRAINT repair_items_repair_order_id_fkey FOREIGN KEY (repair_order_id) REFERENCES public.repair_orders(id);


--
-- Name: repair_orders repair_orders_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_orders
    ADD CONSTRAINT repair_orders_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: repair_orders repair_orders_invoice_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_orders
    ADD CONSTRAINT repair_orders_invoice_id_fkey FOREIGN KEY (invoice_id) REFERENCES public.invoices(id);


--
-- Name: repair_orders repair_orders_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_orders
    ADD CONSTRAINT repair_orders_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: repair_orders repair_orders_technician_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.repair_orders
    ADD CONSTRAINT repair_orders_technician_id_fkey FOREIGN KEY (technician_id) REFERENCES public.users(id);


--
-- Name: technicians technicians_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.technicians
    ADD CONSTRAINT technicians_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: treasury_transactions treasury_transactions_bank_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions
    ADD CONSTRAINT treasury_transactions_bank_account_id_fkey FOREIGN KEY (bank_account_id) REFERENCES public.bank_accounts(id);


--
-- Name: treasury_transactions treasury_transactions_cash_account_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions
    ADD CONSTRAINT treasury_transactions_cash_account_id_fkey FOREIGN KEY (cash_account_id) REFERENCES public.cash_accounts(id);


--
-- Name: treasury_transactions treasury_transactions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions
    ADD CONSTRAINT treasury_transactions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: treasury_transactions treasury_transactions_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions
    ADD CONSTRAINT treasury_transactions_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: treasury_transactions treasury_transactions_journal_entry_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.treasury_transactions
    ADD CONSTRAINT treasury_transactions_journal_entry_id_fkey FOREIGN KEY (journal_entry_id) REFERENCES public.journal_entries(id);


--
-- Name: user_permissions user_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id);


--
-- Name: user_permissions user_permissions_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.user_permissions
    ADD CONSTRAINT user_permissions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: wallet_transactions wallet_transactions_wallet_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallet_transactions
    ADD CONSTRAINT wallet_transactions_wallet_id_fkey FOREIGN KEY (wallet_id) REFERENCES public.wallets(id);


--
-- Name: wallets wallets_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: wallets wallets_partner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_partner_id_fkey FOREIGN KEY (partner_id) REFERENCES public.partners(id);


--
-- Name: wallets wallets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.wallets
    ADD CONSTRAINT wallets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: warranties warranties_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warranties
    ADD CONSTRAINT warranties_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: warranties warranties_repair_item_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warranties
    ADD CONSTRAINT warranties_repair_item_id_fkey FOREIGN KEY (repair_item_id) REFERENCES public.repair_items(id);


--
-- Name: warranties warranties_repair_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.warranties
    ADD CONSTRAINT warranties_repair_order_id_fkey FOREIGN KEY (repair_order_id) REFERENCES public.repair_orders(id);


--
-- PostgreSQL database dump complete
--

\unrestrict FA2Wj0urvbWfyB8oAA1Fe3e8CiPAaGcl8XD6nphPzV8b8LiWuU49QDtqSAo6pRN

