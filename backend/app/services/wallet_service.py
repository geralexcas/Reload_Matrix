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

    def get_wallet_by_id(self, wallet_id: int, company_id: int, lock: bool = False) -> Optional[Wallet]:
        query = self.db.query(Wallet).filter(
            Wallet.id == wallet_id,
            Wallet.company_id == company_id,
        )
        if lock:
            query = query.with_for_update()
        return query.first()

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
        self, wallet_id: int, amount: Decimal, description: str, company_id: int, user_id: Optional[int] = None,
        account_type: Optional[str] = None, account_id: Optional[int] = None, commit: bool = True
    ) -> WalletTransaction:
        if amount <= 0:
            raise ValueError("El monto del depósito debe ser mayor a cero")

        wallet = self.get_wallet_by_id(wallet_id, company_id, lock=True)
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

        # Si se especifica cuenta de tesorería, registrar el ingreso
        if account_type and account_id:
            from app.services.treasury_service import TreasuryService
            from app.models.sql.accounting.journal_entry import JournalEntry
            from app.models.sql.accounting.journal_entry_line import JournalEntryLine
            from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
            from datetime import datetime, timezone
            
            self.db.flush() # Ensure tx gets an ID
            
            # Obtener cuenta de Anticipos (2150)
            wallet_account = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.code == "2150"
            ).first()

            treasury_service = TreasuryService(self.db)
            
            # Determinar cuenta destino (Caja o Banco)
            payment_account_id = None
            if account_type == "BANK":
                bank = treasury_service.get_bank_account_by_id(account_id, company_id)
                if bank:
                    payment_account_id = bank.linked_account_id
            elif account_type == "CASH":
                cash = treasury_service.get_cash_account_by_id(account_id, company_id)
                if cash:
                    payment_account_id = cash.linked_account_id

            # Crear Asiento Contable
            je = None
            if wallet_account and payment_account_id:
                je = JournalEntry(
                    entry_date=datetime.now(timezone.utc),
                    description=description or f"Ingreso a monedero",
                    reference=f"WAL-{wallet_id}-{tx.id}",
                    company_id=company_id,
                    is_posted=True,
                )
                self.db.add(je)
                self.db.flush()

                # Débito a Caja/Banco
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=je.id,
                        account_id=payment_account_id,
                        debit_amount=amount,
                        credit_amount=Decimal("0.00"),
                        description=f"Ingreso de dinero - Monedero",
                    )
                )
                # Crédito a Anticipos (Pasivo)
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=je.id,
                        account_id=wallet_account.id,
                        debit_amount=Decimal("0.00"),
                        credit_amount=amount,
                        description=f"Anticipo de cliente",
                    )
                )
                self.db.flush()

            # Registrar transacción en tesorería saltando su propio asiento
            t_tx = treasury_service.deposit(
                account_type=account_type,
                account_id=account_id,
                amount=amount,
                description=description or f"Ingreso a monedero",
                reference=f"WAL-{wallet_id}-{tx.id}",
                company_id=company_id,
                user_id=user_id,
                skip_journal_entry=True,
                commit=commit,
            )
            
            if je and t_tx:
                t_tx.journal_entry_id = je.id

        if commit:
            self.db.commit()
            self.db.refresh(wallet)
        return tx

    def withdraw(
        self, wallet_id: int, amount: Decimal, description: str, company_id: int, user_id: Optional[int] = None,
        account_type: Optional[str] = None, account_id: Optional[int] = None, commit: bool = True
    ) -> WalletTransaction:
        if amount <= 0:
            raise ValueError("El monto del retiro debe ser mayor a cero")

        wallet = self.get_wallet_by_id(wallet_id, company_id, lock=True)
        if not wallet:
            raise ValueError("Wallet not found")

        if wallet.balance < amount:
            raise ValueError(f"Saldo insuficiente en el monedero. Disponible: ${wallet.balance:,.2f}, Solicitado: ${amount:,.2f}")

        wallet.balance -= amount
        tx = WalletTransaction(
            wallet_id=wallet_id,
            transaction_type="WITHDRAWAL",
            amount=amount,
            description=description,
            balance_after=wallet.balance,
        )
        self.db.add(tx)

        # Si se especifica cuenta de tesorería, registrar la salida de dinero
        if account_type and account_id:
            from app.services.treasury_service import TreasuryService
            from app.models.sql.accounting.journal_entry import JournalEntry
            from app.models.sql.accounting.journal_entry_line import JournalEntryLine
            from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
            from datetime import datetime, timezone
            
            self.db.flush() # Ensure tx gets an ID
            
            # Obtener cuenta de Anticipos (2150)
            wallet_account = self.db.query(ChartOfAccounts).filter(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.code == "2150"
            ).first()

            treasury_service = TreasuryService(self.db)
            
            # Determinar cuenta origen (Caja o Banco)
            payment_account_id = None
            if account_type == "BANK":
                bank = treasury_service.get_bank_account_by_id(account_id, company_id)
                if bank:
                    payment_account_id = bank.linked_account_id
            elif account_type == "CASH":
                cash = treasury_service.get_cash_account_by_id(account_id, company_id)
                if cash:
                    payment_account_id = cash.linked_account_id

            # Crear Asiento Contable
            je = None
            if wallet_account and payment_account_id:
                je = JournalEntry(
                    entry_date=datetime.now(timezone.utc),
                    description=description or f"Retiro de monedero",
                    reference=f"WAL-{wallet_id}-{tx.id}",
                    company_id=company_id,
                    is_posted=True,
                )
                self.db.add(je)
                self.db.flush()

                # Débito a Anticipos (Disminuye el pasivo)
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=je.id,
                        account_id=wallet_account.id,
                        debit_amount=amount,
                        credit_amount=Decimal("0.00"),
                        description=f"Retiro de anticipo - Monedero",
                    )
                )
                # Crédito a Caja/Banco (Disminuye el activo)
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=je.id,
                        account_id=payment_account_id,
                        debit_amount=Decimal("0.00"),
                        credit_amount=amount,
                        description=f"Salida de dinero",
                    )
                )
                self.db.flush()

            # Registrar transacción en tesorería saltando su propio asiento
            t_tx = treasury_service.withdraw(
                account_type=account_type,
                account_id=account_id,
                amount=amount,
                description=description or f"Retiro de monedero",
                reference=f"WAL-{wallet_id}-{tx.id}",
                company_id=company_id,
                user_id=user_id,
                skip_journal_entry=True,
                commit=commit,
            )
            
            if je and t_tx:
                t_tx.journal_entry_id = je.id

        if commit:
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
        wallet = self.get_wallet_by_id(wallet_id, company_id, lock=True)
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
        wallet = self.get_wallet_by_id(wallet_id, company_id, lock=True)
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
