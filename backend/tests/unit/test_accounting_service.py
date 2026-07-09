import pytest
from decimal import Decimal
from datetime import date, datetime, timezone
from app.services.accounting_service import AccountingService
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
from app.models.sql.company import Company


REQUIRED_ACCOUNT_CODES = [
    "1110", "111001", "111010", "1130", "1140",
    "2205", "2130", "2150", "2408",
    "3100", "4100", "5100", "6135",
    "5400", "4200", "2110",
]


@pytest.fixture
def company_simple(db_session):
    company = Company(
        name="Empresa Simple Test",
        nit="900999001",
        dv="1",
        legal_representative="Test Simple",
        address="Calle 1",
        phone="3001111111",
        email="simple@test.com",
        regimen="SIMPLE",
        fecha_inicio_actividades=date(2024, 1, 1),
        is_active=True,
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


@pytest.fixture
def company_comun(db_session):
    company = Company(
        name="Empresa Comun Test",
        nit="900999002",
        dv="2",
        legal_representative="Test Común",
        address="Calle 2",
        phone="3002222222",
        email="comun@test.com",
        regimen="COMUN",
        fecha_inicio_actividades=date(2024, 1, 1),
        is_active=True,
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company


class TestCreateDefaultChartOfAccounts:

    def test_creates_all_required_accounts(self, db_session, test_company):
        service = AccountingService(db_session)
        accounts = service.create_default_chart_of_accounts(test_company.id)

        created_codes = {a.code for a in accounts}
        for code in REQUIRED_ACCOUNT_CODES:
            assert code in created_codes, f"Cuenta {code} no fue creada"

    def test_idempotent_no_error_on_second_call(self, db_session, test_company):
        service = AccountingService(db_session)

        accounts1 = service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        accounts2 = service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        count1 = len(accounts1)
        count2 = len(accounts2)
        assert count1 == count2, f"Segunda llamada retorno {count2} cuentas vs {count1}"

        total_in_db = (
            db_session.query(ChartOfAccounts)
            .filter(ChartOfAccounts.company_id == test_company.id)
            .count()
        )
        assert total_in_db == count1, f"DB tiene {total_in_db} cuentas pero se esperaban {count1}"

    def test_no_duplicate_codes(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        from sqlalchemy import func as sql_func
        duplicates = (
            db_session.query(
                ChartOfAccounts.code,
                sql_func.count(ChartOfAccounts.id)
            )
            .filter(ChartOfAccounts.company_id == test_company.id)
            .group_by(ChartOfAccounts.code)
            .having(sql_func.count(ChartOfAccounts.id) > 1)
            .all()
        )
        assert len(duplicates) == 0, f"Cuentas duplicadas: {duplicates}"

    def test_iva_soportado_inactive_for_simple(self, db_session, company_simple):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(company_simple.id)
        db_session.commit()

        iva_soportado = service._get_account_by_code(company_simple.id, "2408", allow_inactive=True)
        assert iva_soportado is not None, "Cuenta 2408 no fue creada para empresa Simple"
        assert iva_soportado.is_active is False, "Cuenta 2408 deberia estar inactiva para Simple"

    def test_iva_soportado_active_for_comun(self, db_session, company_comun):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(company_comun.id)
        db_session.commit()

        iva_soportado = service._get_account_by_code(company_comun.id, "2408")
        assert iva_soportado is not None, "Cuenta 2408 no fue creada para empresa Común"
        assert iva_soportado.is_active is True, "Cuenta 2408 deberia estar activa para Común"

    def test_cost_accounts_are_cost_type(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        account_5100 = service._get_account_by_code(test_company.id, "5100")
        account_6135 = service._get_account_by_code(test_company.id, "6135")

        assert account_5100 is not None, "Cuenta 5100 no encontrada"
        assert account_6135 is not None, "Cuenta 6135 no encontrada"
        assert account_5100.account_type == "COST", f"Cuenta 5100 es tipo {account_5100.account_type}, esperaba COST"
        assert account_6135.account_type == "COST", f"Cuenta 6135 es tipo {account_6135.account_type}, esperaba COST"


class TestGetAccountByCode:

    def test_finds_all_required_accounts_after_creation(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        for code in REQUIRED_ACCOUNT_CODES:
            account = service._get_account_by_code(test_company.id, code)
            assert account is not None, f"_get_account_by_code no encontro cuenta {code}"
            assert account.code == code


class TestJournalEntryFromPurchase:

    def test_purchase_with_comun_regime(self, db_session, company_comun):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(company_comun.id)
        db_session.commit()

        from app.models.sql.partners import Partner
        partner = Partner(
            name="Proveedor Test",
            nit="123456789",
            dv="0",
            phone="3000000000",
            email="proveedor@test.com",
            address="Calle Test",
            partner_type="SUPPLIER",
            company_id=company_comun.id,
            is_active=True,
        )
        db_session.add(partner)
        db_session.commit()

        from app.models.sql.purchases import Purchase, PurchaseItem
        purchase = Purchase(
            purchase_number="TEST-PUR-001",
            partner_id=partner.id,
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("19000.00"),
            total_amount=Decimal("119000.00"),
            payment_method="CASH",
            status="ISSUED",
            company_id=company_comun.id,
        )
        db_session.add(purchase)
        db_session.flush()

        je = service.create_journal_entry_from_purchase(
            purchase_id=purchase.id,
            company_id=company_comun.id,
            total_amount=Decimal("119000.00"),
            subtotal=Decimal("100000.00"),
            tax_amount=Decimal("19000.00"),
            partner_id=partner.id,
            payment_method="CASH",
        )
        assert je is not None, "Journal entry no fue creado"
        assert je.company_id == company_comun.id

        from app.models.sql.accounting.journal_entry_line import JournalEntryLine
        lines = (
            db_session.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == je.id)
            .all()
        )
        assert len(lines) == 3, f"Se esperaban 3 lineas (inventario + IVA + caja), se obtuvieron {len(lines)}"

        iva_line = [l for l in lines if l.account_id == service._get_account_by_code(company_comun.id, "2408").id]
        assert len(iva_line) == 1, "No se registro linea de IVA soportado (2408) para empresa COMUN"
        assert iva_line[0].debit_amount == Decimal("19000.00")

    def test_purchase_with_simple_regime_no_iva(self, db_session, company_simple):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(company_simple.id)
        db_session.commit()

        from app.models.sql.partners import Partner
        partner = Partner(
            name="Proveedor Test Simple",
            nit="987654321",
            dv="0",
            phone="3000000001",
            email="proveedor_simple@test.com",
            address="Calle Test Simple",
            partner_type="SUPPLIER",
            company_id=company_simple.id,
            is_active=True,
        )
        db_session.add(partner)
        db_session.commit()

        from app.models.sql.purchases import Purchase
        purchase = Purchase(
            purchase_number="TEST-PUR-SIMPLE-001",
            partner_id=partner.id,
            subtotal=Decimal("119000.00"),
            tax_amount=Decimal("0.00"),
            total_amount=Decimal("119000.00"),
            payment_method="CASH",
            status="ISSUED",
            company_id=company_simple.id,
        )
        db_session.add(purchase)
        db_session.flush()

        je = service.create_journal_entry_from_purchase(
            purchase_id=purchase.id,
            company_id=company_simple.id,
            total_amount=Decimal("119000.00"),
            subtotal=Decimal("119000.00"),
            tax_amount=Decimal("0.00"),
            partner_id=partner.id,
            payment_method="CASH",
        )
        assert je is not None, "Journal entry no fue creado para Simple"

        from app.models.sql.accounting.journal_entry_line import JournalEntryLine
        lines = (
            db_session.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == je.id)
            .all()
        )

        iva_account = service._get_account_by_code(company_simple.id, "2408")
        iva_lines = [l for l in lines if l.account_id == iva_account.id] if iva_account else []
        assert len(iva_lines) == 0, "Simple no deberia registrar IVA soportado"

        inventory_account = service._get_account_by_code(company_simple.id, "1140")
        inventory_lines = [l for l in lines if l.account_id == inventory_account.id]
        assert len(inventory_lines) == 1
        assert inventory_lines[0].debit_amount == Decimal("119000.00"), "Simple debe registrar total (incluye IVA) en inventario"


class TestJournalEntryForInitialStock:

    def test_initial_stock_with_cash(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        je = service.create_journal_entry_for_initial_stock(
            product_id=1,
            product_name="Test Product",
            company_id=test_company.id,
            total_amount=Decimal("50000.00"),
            payment_method="CASH",
        )
        assert je is not None
        assert je.company_id == test_company.id

        from app.models.sql.accounting.journal_entry_line import JournalEntryLine
        lines = (
            db_session.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == je.id)
            .all()
        )
        assert len(lines) == 2

        inventory_account = service._get_account_by_code(test_company.id, "1140")
        cash_account = service._get_account_by_code(test_company.id, "111001")

        debit_lines = [l for l in lines if l.account_id == inventory_account.id and l.debit_amount > 0]
        credit_lines = [l for l in lines if l.account_id == cash_account.id and l.credit_amount > 0]

        assert len(debit_lines) == 1
        assert debit_lines[0].debit_amount == Decimal("50000.00")
        assert len(credit_lines) == 1
        assert credit_lines[0].credit_amount == Decimal("50000.00")


class TestGetJournalEntryWithLines:

    def test_returns_entry_with_lines_and_account_details(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        cash_account = service._get_account_by_code(test_company.id, "111001")
        expense_account = service._get_account_by_code(test_company.id, "5100")

        from app.models.sql.accounting.journal_entry import JournalEntry
        from app.models.sql.accounting.journal_entry_line import JournalEntryLine

        je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description="Test entry with lines",
            company_id=test_company.id,
            is_posted=False,
        )
        db_session.add(je)
        db_session.flush()

        line1 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=expense_account.id,
            debit_amount=Decimal("90000.00"),
            credit_amount=Decimal("0.00"),
            description="Gasto internet",
        )
        line2 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=cash_account.id,
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("90000.00"),
            description="Pago internet",
        )
        db_session.add_all([line1, line2])
        db_session.commit()

        result = service.get_journal_entry_with_lines(je.id, test_company.id)

        assert result is not None
        assert result.id == je.id
        assert len(result.lines) == 2
        for line in result.lines:
            assert line.account is not None
            assert line.account.code is not None
            assert line.account.name is not None

    def test_returns_none_for_nonexistent_entry(self, db_session, test_company):
        service = AccountingService(db_session)
        result = service.get_journal_entry_with_lines(9999, test_company.id)
        assert result is None


class TestPostJournalEntryTreasurySync:

    def test_post_creates_treasury_transaction_when_linked(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        cash_account = service._get_account_by_code(test_company.id, "111001")
        expense_account = service._get_account_by_code(test_company.id, "5100")

        from app.models.sql.accounting.cash_account import CashAccount
        from app.models.sql.accounting.journal_entry import JournalEntry
        from app.models.sql.accounting.journal_entry_line import JournalEntryLine

        cash_acct = CashAccount(
            company_id=test_company.id,
            name="Caja Principal",
            account_type="MAIN_CASH",
            current_balance=Decimal("500000.00"),
            initial_balance=Decimal("500000.00"),
            is_active=True,
            linked_account_id=cash_account.id,
        )
        db_session.add(cash_acct)
        db_session.commit()

        je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description="Pago internet",
            company_id=test_company.id,
            is_posted=False,
        )
        db_session.add(je)
        db_session.flush()

        line1 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=expense_account.id,
            debit_amount=Decimal("90000.00"),
            credit_amount=Decimal("0.00"),
            description="Gasto internet",
        )
        line2 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=cash_account.id,
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("90000.00"),
            description="Pago internet",
        )
        db_session.add_all([line1, line2])
        db_session.commit()

        result = service.post_journal_entry(je.id, test_company.id)

        assert result is not None
        assert result["is_posted"] is True
        assert result["treasury_sync_count"] >= 1
        assert result["warning"] is None

        from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
        txs = db_session.query(TreasuryTransaction).filter(
            TreasuryTransaction.journal_entry_id == je.id
        ).all()
        assert len(txs) >= 1

    def test_post_returns_warning_when_no_treasury_linked(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        cash_account = service._get_account_by_code(test_company.id, "111001")
        expense_account = service._get_account_by_code(test_company.id, "5100")

        from app.models.sql.accounting.journal_entry import JournalEntry
        from app.models.sql.accounting.journal_entry_line import JournalEntryLine

        je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description="Pago internet sin tesoreria",
            company_id=test_company.id,
            is_posted=False,
        )
        db_session.add(je)
        db_session.flush()

        line1 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=expense_account.id,
            debit_amount=Decimal("90000.00"),
            credit_amount=Decimal("0.00"),
            description="Gasto internet",
        )
        line2 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=cash_account.id,
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("90000.00"),
            description="Pago internet",
        )
        db_session.add_all([line1, line2])
        db_session.commit()

        result = service.post_journal_entry(je.id, test_company.id)

        assert result is not None
        assert result["is_posted"] is True
        assert result["treasury_sync_count"] == 0
        assert result["warning"] is not None
        assert "tesorería" in result["warning"].lower() or "tesorer" in result["warning"]

    def test_post_unbalanced_entry_raises_error(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        cash_account = service._get_account_by_code(test_company.id, "111001")

        from app.models.sql.accounting.journal_entry import JournalEntry
        from app.models.sql.accounting.journal_entry_line import JournalEntryLine

        je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description="Unbalanced entry",
            company_id=test_company.id,
            is_posted=False,
        )
        db_session.add(je)
        db_session.flush()

        line1 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=cash_account.id,
            debit_amount=Decimal("100.00"),
            credit_amount=Decimal("0.00"),
        )
        db_session.add(line1)
        db_session.commit()

        with pytest.raises(ValueError, match="balanced"):
            service.post_journal_entry(je.id, test_company.id)

    def test_post_already_posted_raises_error(self, db_session, test_company):
        service = AccountingService(db_session)
        service.create_default_chart_of_accounts(test_company.id)
        db_session.commit()

        cash_account = service._get_account_by_code(test_company.id, "111001")
        expense_account = service._get_account_by_code(test_company.id, "5100")

        from app.models.sql.accounting.journal_entry import JournalEntry
        from app.models.sql.accounting.journal_entry_line import JournalEntryLine

        je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description="Already posted",
            company_id=test_company.id,
            is_posted=True,
        )
        db_session.add(je)
        db_session.flush()

        line1 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=expense_account.id,
            debit_amount=Decimal("90000.00"),
            credit_amount=Decimal("0.00"),
        )
        line2 = JournalEntryLine(
            journal_entry_id=je.id,
            account_id=cash_account.id,
            debit_amount=Decimal("0.00"),
            credit_amount=Decimal("90000.00"),
        )
        db_session.add_all([line1, line2])
        db_session.commit()

        with pytest.raises(ValueError, match="already posted"):
            service.post_journal_entry(je.id, test_company.id)
