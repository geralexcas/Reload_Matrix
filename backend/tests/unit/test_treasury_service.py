import pytest
from decimal import Decimal

from app.services.treasury_service import TreasuryService
from app.models.sql.accounting.bank_account import BankAccount
from app.models.sql.accounting.cash_account import CashAccount
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts


class TestTreasuryAmountValidation:
    def _create_bank_account(self, db_session, test_company, linked_account_id=None):
        ba = BankAccount(
            name="Banco Test",
            bank_name="Banco Nacional",
            account_number="001234567",
            account_type="CHECKING",
            currency="COP",
            initial_balance=Decimal("0.00"),
            current_balance=Decimal("0.00"),
            company_id=test_company.id,
            linked_account_id=linked_account_id,
        )
        db_session.add(ba)
        db_session.flush()
        return ba

    def _create_cash_account(self, db_session, test_company, linked_account_id=None):
        ca = CashAccount(
            name="Caja Principal",
            account_type="MAIN_CASH",
            currency="COP",
            initial_balance=Decimal("0.00"),
            current_balance=Decimal("0.00"),
            company_id=test_company.id,
            linked_account_id=linked_account_id,
        )
        db_session.add(ca)
        db_session.flush()
        return ca

    def _get_linked_account(self, db_session, test_company):
        acct = (
            db_session.query(ChartOfAccounts)
            .filter(
                ChartOfAccounts.company_id == test_company.id,
                ChartOfAccounts.code.like("11%"),
            )
            .first()
        )
        return acct.id if acct else None

    def test_deposit_negative_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.deposit(
                account_type="BANK",
                account_id=ba.id,
                amount=Decimal("-1000"),
                description="test",
                reference="REF-001",
                company_id=test_company.id,
            )

    def test_deposit_zero_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.deposit(
                account_type="BANK",
                account_id=ba.id,
                amount=Decimal("0"),
                description="test",
                reference="REF-002",
                company_id=test_company.id,
            )

    def test_withdraw_negative_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.withdraw(
                account_type="BANK",
                account_id=ba.id,
                amount=Decimal("-500"),
                description="test",
                reference="REF-003",
                company_id=test_company.id,
            )

    def test_transfer_negative_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba_from = self._create_bank_account(db_session, test_company, linked)
        ba_to = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.transfer(
                from_account_type="BANK",
                from_account_id=ba_from.id,
                to_account_type="BANK",
                to_account_id=ba_to.id,
                amount=Decimal("0"),
                description="test",
                reference="REF-004",
                company_id=test_company.id,
            )

    def test_transfer_zero_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba_from = self._create_bank_account(db_session, test_company, linked)
        ba_to = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.transfer(
                from_account_type="BANK",
                from_account_id=ba_from.id,
                to_account_type="BANK",
                to_account_id=ba_to.id,
                amount=Decimal("0"),
                description="test",
                reference="REF-005",
                company_id=test_company.id,
            )

    def test_deposit_success(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        contra = (
            db_session.query(ChartOfAccounts)
            .filter(
                ChartOfAccounts.company_id == test_company.id,
                ChartOfAccounts.code.like("31%"),
            )
            .first()
        )
        db_session.commit()
        service = TreasuryService(db_session)
        tx = service.deposit(
            account_type="BANK",
            account_id=ba.id,
            amount=Decimal("500000"),
            description="test deposit",
            reference="REF-DEP-001",
            company_id=test_company.id,
            contra_account_id=contra.id if contra else linked,
            skip_journal_entry=linked is None,
        )
        assert tx.amount == Decimal("500000")
        assert tx.transaction_type == "DEPOSIT"
        db_session.refresh(ba)
        assert ba.current_balance == Decimal("500000.00")

    def test_withdraw_success(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        contra = (
            db_session.query(ChartOfAccounts)
            .filter(
                ChartOfAccounts.company_id == test_company.id,
                ChartOfAccounts.code.like("31%"),
            )
            .first()
        )
        ba = self._create_bank_account(db_session, test_company, linked)
        ba.current_balance = Decimal("1000000")
        db_session.commit()
        service = TreasuryService(db_session)
        tx = service.withdraw(
            account_type="BANK",
            account_id=ba.id,
            amount=Decimal("200000"),
            description="test withdraw",
            reference="REF-WD-001",
            company_id=test_company.id,
            contra_account_id=contra.id if contra else linked,
            skip_journal_entry=linked is None,
        )
        assert tx.amount == Decimal("200000")
        assert tx.transaction_type == "WITHDRAWAL"
        db_session.refresh(ba)
        assert ba.current_balance == Decimal("800000.00")

    def test_transfer_success(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba_from = self._create_bank_account(db_session, test_company, linked)
        ba_to = self._create_bank_account(db_session, test_company, linked)
        ba_from.current_balance = Decimal("1000000")
        db_session.commit()
        service = TreasuryService(db_session)
        result = service.transfer(
            from_account_type="BANK",
            from_account_id=ba_from.id,
            to_account_type="BANK",
            to_account_id=ba_to.id,
            amount=Decimal("300000"),
            description="test transfer",
            reference="REF-TRF-001",
                company_id=test_company.id,
            )

    def test_record_bank_fee_negative_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        ba.current_balance = Decimal("500000")
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.record_bank_fee(
                bank_account_id=ba.id,
                amount=Decimal("-100"),
                description="test fee",
                reference="REF-FEE-001",
                company_id=test_company.id,
            )

    def test_record_bank_fee_zero_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        ba.current_balance = Decimal("500000")
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.record_bank_fee(
                bank_account_id=ba.id,
                amount=Decimal("0"),
                description="test fee",
                reference="REF-FEE-002",
                company_id=test_company.id,
            )

    def test_record_bank_interest_negative_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.record_bank_interest(
                bank_account_id=ba.id,
                amount=Decimal("-50"),
                description="test interest",
                reference="REF-INT-001",
                company_id=test_company.id,
            )

    def test_record_bank_interest_zero_amount_raises(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.record_bank_interest(
                bank_account_id=ba.id,
                amount=Decimal("0"),
                description="test interest",
                reference="REF-INT-002",
                company_id=test_company.id,
            )

    def test_withdraw_insufficient_balance(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba = self._create_bank_account(db_session, test_company, linked)
        ba.current_balance = Decimal("100000")
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="[Ii]nsufficient balance|saldo insuficiente"):
            service.withdraw(
                account_type="BANK",
                account_id=ba.id,
                amount=Decimal("500000"),
                description="test",
                reference="REF-WD-002",
                company_id=test_company.id,
            )

    def test_transfer_insufficient_balance(self, db_session, test_company, chart_of_accounts):
        linked = self._get_linked_account(db_session, test_company)
        ba_from = self._create_bank_account(db_session, test_company, linked)
        ba_to = self._create_bank_account(db_session, test_company, linked)
        ba_from.current_balance = Decimal("10000")
        db_session.commit()
        service = TreasuryService(db_session)
        with pytest.raises(ValueError, match="[Ii]nsufficient balance|saldo insuficiente"):
            service.transfer(
                from_account_type="BANK",
                from_account_id=ba_from.id,
                to_account_type="BANK",
                to_account_id=ba_to.id,
                amount=Decimal("50000"),
                description="test",
                reference="REF-TRF-002",
                company_id=test_company.id,
            )
