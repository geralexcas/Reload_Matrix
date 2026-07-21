import pytest
from decimal import Decimal

from app.services.wallet_service import WalletService
from app.models.sql.wallet import Wallet


class TestWalletAmountValidation:
    def _create_wallet(self, db_session, test_company):
        service = WalletService(db_session)
        wallet = Wallet(
            balance=Decimal("100000.00"),
            currency="COP",
            is_active=True,
            company_id=test_company.id,
        )
        db_session.add(wallet)
        db_session.commit()
        db_session.refresh(wallet)
        return wallet

    def test_deposit_negative_amount_raises(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.deposit(wallet.id, Decimal("-500"), "desc", test_company.id)

    def test_deposit_zero_amount_raises(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.deposit(wallet.id, Decimal("0"), "desc", test_company.id)

    def test_withdraw_negative_amount_raises(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.withdraw(wallet.id, Decimal("-500"), "desc", test_company.id)

    def test_withdraw_zero_amount_raises(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        with pytest.raises(ValueError, match="mayor a cero"):
            service.withdraw(wallet.id, Decimal("0"), "desc", test_company.id)

    def test_deposit_success(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        tx = service.deposit(wallet.id, Decimal("50000"), "test", test_company.id, commit=True)
        assert tx.amount == Decimal("50000")
        db_session.refresh(wallet)
        assert wallet.balance == Decimal("150000.00")

    def test_withdraw_success(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        tx = service.withdraw(wallet.id, Decimal("30000"), "test", test_company.id, commit=True)
        assert tx.amount == Decimal("30000")
        db_session.refresh(wallet)
        assert wallet.balance == Decimal("70000.00")

    def test_withdraw_insufficient_balance(self, db_session, test_company):
        wallet = self._create_wallet(db_session, test_company)
        service = WalletService(db_session)
        with pytest.raises(ValueError, match="Saldo insuficiente"):
            service.withdraw(wallet.id, Decimal("200000"), "test", test_company.id)
