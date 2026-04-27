from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal

from app.models.sql.wallet import Wallet, WalletTransaction
from app.models.sql import company as company_model
from app.schemas import wallet as wallet_schema


class WalletService:
    def __init__(self, db: Session):
        self.db = db

    def create_wallet(
        self, wallet: wallet_schema.WalletCreate, company_id: int
    ) -> Wallet:
        db_company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not db_company:
            raise ValueError("Company not found")

        db_wallet = Wallet(**wallet.model_dump(), company_id=company_id)
        self.db.add(db_wallet)
        self.db.commit()
        self.db.refresh(db_wallet)
        return db_wallet

    def get_wallets(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[Wallet]:
        from sqlalchemy.orm import joinedload
        return (
            self.db.query(Wallet)
            .options(joinedload(Wallet.partner))
            .filter(Wallet.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_wallet_by_id(self, wallet_id: int, company_id: int) -> Optional[Wallet]:
        return (
            self.db.query(Wallet)
            .filter(
                Wallet.id == wallet_id,
                Wallet.company_id == company_id,
            )
            .first()
        )

    def get_wallet_by_partner(
        self, partner_id: int, company_id: int
    ) -> Optional[Wallet]:
        return (
            self.db.query(Wallet)
            .filter(
                Wallet.partner_id == partner_id,
                Wallet.company_id == company_id,
                Wallet.is_active == True,
            )
            .first()
        )

    def deposit(
        self, wallet_id: int, amount: Decimal, description: str, company_id: int
    ) -> WalletTransaction:
        wallet = self.get_wallet_by_id(wallet_id, company_id)
        if not wallet:
            raise ValueError("Wallet not found")

        wallet.balance += amount
        tx = WalletTransaction(
            wallet_id=wallet_id,
            transaction_type="DEPOSIT",
            amount=amount,
            description=description,
            balance_after=wallet.balance,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(wallet)
        return tx

    def withdraw(
        self, wallet_id: int, amount: Decimal, description: str, company_id: int
    ) -> WalletTransaction:
        wallet = self.get_wallet_by_id(wallet_id, company_id)
        if not wallet:
            raise ValueError("Wallet not found")

        if wallet.balance < amount:
            raise ValueError("Insufficient balance")

        wallet.balance -= amount
        tx = WalletTransaction(
            wallet_id=wallet_id,
            transaction_type="WITHDRAWAL",
            amount=amount,
            description=description,
            balance_after=wallet.balance,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(wallet)
        return tx

    def get_transactions(
        self, wallet_id: int, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[WalletTransaction]:
        wallet = self.get_wallet_by_id(wallet_id, company_id)
        if not wallet:
            raise ValueError("Wallet not found")

        return (
            self.db.query(WalletTransaction)
            .filter(WalletTransaction.wallet_id == wallet_id)
            .order_by(WalletTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_loyalty_points(
        self, wallet_id: int, points: Decimal, company_id: int, description: str = ""
    ) -> Wallet:
        """
        Agrega puntos de lealtad al monedero.
        Regla: 1 punto por cada $10,000 COP gastados (configurable).
        """
        wallet = self.get_wallet_by_id(wallet_id, company_id)
        if not wallet:
            raise ValueError("Wallet not found")

        wallet.loyalty_points = (wallet.loyalty_points or Decimal("0.00")) + points
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def redeem_loyalty_points(
        self, wallet_id: int, points: Decimal, company_id: int
    ) -> Wallet:
        """
        Canjea puntos de lealtad por saldo.
        Regla: 100 puntos = $1,000 COP (configurable).
        """
        wallet = self.get_wallet_by_id(wallet_id, company_id)
        if not wallet:
            raise ValueError("Wallet not found")

        current_points = wallet.loyalty_points or Decimal("0.00")
        if current_points < points:
            raise ValueError("Insufficient loyalty points")

        wallet.loyalty_points = current_points - points
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get_loyalty_summary(self, wallet_id: int, company_id: int) -> dict:
        """
        Retorna resumen de puntos de lealtad.
        """
        wallet = self.get_wallet_by_id(wallet_id, company_id)
        if not wallet:
            raise ValueError("Wallet not found")

        points = wallet.loyalty_points or Decimal("0.00")
        cop_value = points * Decimal("10")  # 1 punto = $10 COP

        return {
            "wallet_id": wallet_id,
            "loyalty_points": float(points),
            "cop_equivalent": float(cop_value),
            "conversion_rate": "1 punto = $10 COP",
        }
