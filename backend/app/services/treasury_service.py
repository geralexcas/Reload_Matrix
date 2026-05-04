from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func as sql_func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone
from decimal import Decimal

from app.models.sql.accounting.bank_account import BankAccount
from app.models.sql.accounting.cash_account import CashAccount
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from app.models.sql.accounting.check_register import CheckRegister
from app.models.sql.accounting.bank_reconciliation import BankReconciliation
from app.models.sql.accounting.reconciliation_line import ReconciliationLine
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql import company as company_model
from app.schemas import treasury as treasury_schema


class TreasuryService:
    def __init__(self, db: Session):
        self.db = db

    def _get_account_by_code(
        self, company_id: int, code: str
    ) -> Optional[ChartOfAccounts]:
        return (
            self.db.query(ChartOfAccounts)
            .filter(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.code == code,
            )
            .first()
        )

    def _create_journal_entry(
        self,
        company_id: int,
        description: str,
        reference: str,
        lines: List[Tuple[int, Decimal, Decimal, str]],
    ) -> JournalEntry:
        db_je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        for account_id, debit, credit, line_desc in lines:
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=account_id,
                    debit_amount=debit,
                    credit_amount=credit,
                    description=line_desc,
                )
            )

        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    # ──────────────────────────────────────────────
    # Bank Accounts
    # ──────────────────────────────────────────────

    def create_bank_account(
        self, data: treasury_schema.BankAccountCreate, company_id: int
    ) -> BankAccount:
        db_company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not db_company:
            raise ValueError("Company not found")

        db_ba = BankAccount(
            **data.model_dump(),
            company_id=company_id,
            current_balance=data.initial_balance,
        )
        self.db.add(db_ba)
        self.db.flush()

        if data.initial_balance > 0 and data.linked_account_id:
            self._create_journal_entry(
                company_id=company_id,
                description=f"Saldo inicial - {data.bank_name} {data.account_number}",
                reference=f"BA-OPEN-{db_ba.id:06d}",
                lines=[
                    (
                        data.linked_account_id,
                        data.initial_balance,
                        Decimal("0.00"),
                        f"Saldo inicial cuenta bancaria",
                    ),
                    (
                        data.linked_account_id,
                        Decimal("0.00"),
                        data.initial_balance,
                        f"Contra partida saldo inicial",
                    ),
                ],
            )

        self.db.commit()
        self.db.refresh(db_ba)
        return db_ba

    def get_bank_accounts(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[BankAccount]:
        return (
            self.db.query(BankAccount)
            .filter(
                BankAccount.company_id == company_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_bank_account_by_id(
        self, bank_id: int, company_id: int
    ) -> Optional[BankAccount]:
        return (
            self.db.query(BankAccount)
            .filter(
                BankAccount.id == bank_id,
                BankAccount.company_id == company_id,
            )
            .first()
        )

    def update_bank_account(
        self, bank_id: int, data: treasury_schema.BankAccountUpdate, company_id: int
    ) -> Optional[BankAccount]:
        db_ba = self.get_bank_account_by_id(bank_id, company_id)
        if not db_ba:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(db_ba, key, value)
        self.db.commit()
        self.db.refresh(db_ba)
        return db_ba

    def deactivate_bank_account(self, bank_id: int, company_id: int) -> bool:
        db_ba = self.get_bank_account_by_id(bank_id, company_id)
        if not db_ba:
            return False
        if db_ba.current_balance != Decimal("0.00"):
            raise ValueError("Cannot deactivate account with non-zero balance")
        db_ba.is_active = False
        self.db.commit()
        return True

    def get_bank_account_transactions(
        self, bank_id: int, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[TreasuryTransaction]:
        return (
            self.db.query(TreasuryTransaction)
            .filter(
                TreasuryTransaction.company_id == company_id,
                TreasuryTransaction.bank_account_id == bank_id,
            )
            .order_by(TreasuryTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ──────────────────────────────────────────────
    # Cash Accounts
    # ──────────────────────────────────────────────

    def create_cash_account(
        self, data: treasury_schema.CashAccountCreate, company_id: int
    ) -> CashAccount:
        db_company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not db_company:
            raise ValueError("Company not found")

        db_ca = CashAccount(
            **data.model_dump(),
            company_id=company_id,
            current_balance=data.initial_balance,
        )
        self.db.add(db_ca)
        self.db.commit()
        self.db.refresh(db_ca)
        return db_ca

    def get_cash_accounts(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[CashAccount]:
        return (
            self.db.query(CashAccount)
            .filter(
                CashAccount.company_id == company_id,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_cash_account_by_id(
        self, cash_id: int, company_id: int
    ) -> Optional[CashAccount]:
        return (
            self.db.query(CashAccount)
            .filter(
                CashAccount.id == cash_id,
                CashAccount.company_id == company_id,
            )
            .first()
        )

    def update_cash_account(
        self, cash_id: int, data: treasury_schema.CashAccountUpdate, company_id: int
    ) -> Optional[CashAccount]:
        db_ca = self.get_cash_account_by_id(cash_id, company_id)
        if not db_ca:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(db_ca, key, value)
        self.db.commit()
        self.db.refresh(db_ca)
        return db_ca

    def deactivate_cash_account(self, cash_id: int, company_id: int) -> bool:
        db_ca = self.get_cash_account_by_id(cash_id, company_id)
        if not db_ca:
            return False
        if db_ca.current_balance != Decimal("0.00"):
            raise ValueError("Cannot deactivate account with non-zero balance")
        db_ca.is_active = False
        self.db.commit()
        return True

    def get_cash_account_transactions(
        self, cash_id: int, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[TreasuryTransaction]:
        return (
            self.db.query(TreasuryTransaction)
            .filter(
                TreasuryTransaction.company_id == company_id,
                TreasuryTransaction.cash_account_id == cash_id,
            )
            .order_by(TreasuryTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ──────────────────────────────────────────────
    # Deposits
    # ──────────────────────────────────────────────

    def deposit(
        self,
        account_type: str,
        account_id: int,
        amount: Decimal,
        description: str,
        reference: str,
        company_id: int,
        user_id: Optional[int] = None,
        skip_journal_entry: bool = False,
    ) -> TreasuryTransaction:
        je = None

        if account_type == "BANK":
            account = self.get_bank_account_by_id(account_id, company_id)
            if not account:
                raise ValueError("Bank account not found")

            account.current_balance += amount
            balance_after = account.current_balance

            if account.linked_account_id and not skip_journal_entry:
                cash_account = self._get_account_by_code(company_id, "111001")
                linked_acct_id = account.linked_account_id
                contra_id = cash_account.id if cash_account else linked_acct_id

                je = self._create_journal_entry(
                    company_id=company_id,
                    description=description or f"Deposito a {account.bank_name}",
                    reference=reference,
                    lines=[
                        (
                            linked_acct_id,
                            amount,
                            Decimal("0.00"),
                            f"Deposito - {account.name}",
                        ),
                        (
                            contra_id,
                            Decimal("0.00"),
                            amount,
                            f"Contra partida deposito",
                        ),
                    ],
                )

        elif account_type == "CASH":
            account = self.get_cash_account_by_id(account_id, company_id)
            if not account:
                raise ValueError("Cash account not found")

            account.current_balance += amount
            balance_after = account.current_balance

            if account.linked_account_id and not skip_journal_entry:
                # Si no se salta el asiento, debemos encontrar la cuenta de contrapartida adecuada
                # Por defecto usaremos una cuenta puente o evitar doble registro
                je = self._create_journal_entry(
                    company_id=company_id,
                    description=description or f"Ingreso a {account.name}",
                    reference=reference,
                    lines=[
                        (
                            account.linked_account_id,
                            amount,
                            Decimal("0.00"),
                            f"Ingreso caja - {account.name}",
                        ),
                        (
                            account.linked_account_id,
                            Decimal("0.00"),
                            amount,
                            f"Contra partida",
                        ),
                    ],
                )
        else:
            raise ValueError("Invalid account type")

        self.db.commit()
        self.db.refresh(account)

        tx = TreasuryTransaction(
            company_id=company_id,
            account_type=account_type,
            bank_account_id=account_id if account_type == "BANK" else None,
            cash_account_id=account_id if account_type == "CASH" else None,
            transaction_type="DEPOSIT",
            amount=amount,
            description=description,
            reference=reference,
            journal_entry_id=je.id if je else None,
            balance_after=balance_after,
            created_by=user_id,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    # ──────────────────────────────────────────────
    # Withdrawals
    # ──────────────────────────────────────────────

    def withdraw(
        self,
        account_type: str,
        account_id: int,
        amount: Decimal,
        description: str,
        reference: str,
        company_id: int,
        user_id: Optional[int] = None,
        skip_journal_entry: bool = False,
    ) -> TreasuryTransaction:
        if account_type == "BANK":
            account = self.get_bank_account_by_id(account_id, company_id)
            if not account:
                raise ValueError("Bank account not found")
        elif account_type == "CASH":
            account = self.get_cash_account_by_id(account_id, company_id)
            if not account:
                raise ValueError("Cash account not found")
        else:
            raise ValueError("Invalid account type")

        if account.current_balance < amount:
            raise ValueError("Insufficient balance")

        account.current_balance -= amount
        balance_after = account.current_balance

        je = None
        if account.linked_account_id and not skip_journal_entry:
            expense_account = self._get_account_by_code(company_id, "5400")
            contra_id = (
                expense_account.id if expense_account else account.linked_account_id
            )

            je = self._create_journal_entry(
                company_id=company_id,
                description=description
                or f"Retiro de {account.name if hasattr(account, 'name') else 'cuenta'}",
                reference=reference,
                lines=[
                    (
                        contra_id,
                        amount,
                        Decimal("0.00"),
                        f"Retiro - {description or 'N/A'}",
                    ),
                    (
                        account.linked_account_id,
                        Decimal("0.00"),
                        amount,
                        f"Salida de {account_type}",
                    ),
                ],
            )

        self.db.commit()
        self.db.refresh(account)

        tx = TreasuryTransaction(
            company_id=company_id,
            account_type=account_type,
            bank_account_id=account_id if account_type == "BANK" else None,
            cash_account_id=account_id if account_type == "CASH" else None,
            transaction_type="WITHDRAWAL",
            amount=amount,
            description=description,
            reference=reference,
            journal_entry_id=je.id if je else None,
            balance_after=balance_after,
            created_by=user_id,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    # ──────────────────────────────────────────────
    # Transfers
    # ──────────────────────────────────────────────

    def transfer(
        self,
        from_account_type: str,
        from_account_id: int,
        to_account_type: str,
        to_account_id: int,
        amount: Decimal,
        description: str,
        reference: str,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> List[TreasuryTransaction]:
        if from_account_type == "BANK":
            from_account = self.get_bank_account_by_id(from_account_id, company_id)
            if not from_account:
                raise ValueError("Source bank account not found")
        elif from_account_type == "CASH":
            from_account = self.get_cash_account_by_id(from_account_id, company_id)
            if not from_account:
                raise ValueError("Source cash account not found")
        else:
            raise ValueError("Invalid source account type")

        if to_account_type == "BANK":
            to_account = self.get_bank_account_by_id(to_account_id, company_id)
            if not to_account:
                raise ValueError("Destination bank account not found")
        elif to_account_type == "CASH":
            to_account = self.get_cash_account_by_id(to_account_id, company_id)
            if not to_account:
                raise ValueError("Destination cash account not found")
        else:
            raise ValueError("Invalid destination account type")

        if from_account.current_balance < amount:
            raise ValueError("Insufficient balance in source account")

        from_account.current_balance -= amount
        to_account.current_balance += amount
        balance_from = from_account.current_balance
        balance_to = to_account.current_balance

        je = None
        if from_account.linked_account_id and to_account.linked_account_id:
            je = self._create_journal_entry(
                company_id=company_id,
                description=description
                or f"Transferencia {from_account_type} -> {to_account_type}",
                reference=reference,
                lines=[
                    (
                        to_account.linked_account_id,
                        amount,
                        Decimal("0.00"),
                        f"Transferencia a {to_account.name}",
                    ),
                    (
                        from_account.linked_account_id,
                        Decimal("0.00"),
                        amount,
                        f"Transferencia desde {from_account.name}",
                    ),
                ],
            )

        self.db.commit()
        self.db.refresh(from_account)
        self.db.refresh(to_account)

        tx_out = TreasuryTransaction(
            company_id=company_id,
            account_type=from_account_type,
            bank_account_id=from_account_id if from_account_type == "BANK" else None,
            cash_account_id=from_account_id if from_account_type == "CASH" else None,
            transaction_type="TRANSFER_OUT",
            amount=amount,
            description=description,
            reference=reference,
            journal_entry_id=je.id if je else None,
            balance_after=balance_from,
            created_by=user_id,
        )
        self.db.add(tx_out)
        self.db.flush()

        tx_in = TreasuryTransaction(
            company_id=company_id,
            account_type=to_account_type,
            bank_account_id=to_account_id if to_account_type == "BANK" else None,
            cash_account_id=to_account_id if to_account_type == "CASH" else None,
            transaction_type="TRANSFER_IN",
            amount=amount,
            description=description,
            reference=reference,
            journal_entry_id=je.id if je else None,
            balance_after=balance_to,
            created_by=user_id,
        )
        self.db.add(tx_in)
        self.db.commit()
        self.db.refresh(tx_out)
        self.db.refresh(tx_in)
        return [tx_out, tx_in]

    # ──────────────────────────────────────────────
    # Bank Fees & Interest
    # ──────────────────────────────────────────────

    def record_bank_fee(
        self,
        bank_account_id: int,
        amount: Decimal,
        description: str,
        reference: str,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> TreasuryTransaction:
        account = self.get_bank_account_by_id(bank_account_id, company_id)
        if not account:
            raise ValueError("Bank account not found")
        if account.current_balance < amount:
            raise ValueError("Insufficient balance")

        account.current_balance -= amount
        balance_after = account.current_balance

        je = None
        fee_account = self._get_account_by_code(company_id, "5400")
        if fee_account and account.linked_account_id:
            je = self._create_journal_entry(
                company_id=company_id,
                description=description or f"Comision bancaria - {account.bank_name}",
                reference=reference,
                lines=[
                    (fee_account.id, amount, Decimal("0.00"), f"Comision bancaria"),
                    (
                        account.linked_account_id,
                        Decimal("0.00"),
                        amount,
                        f"Comision - {account.name}",
                    ),
                ],
            )

        self.db.commit()
        self.db.refresh(account)

        tx = TreasuryTransaction(
            company_id=company_id,
            account_type="BANK",
            bank_account_id=bank_account_id,
            cash_account_id=None,
            transaction_type="FEE",
            amount=amount,
            description=description,
            reference=reference,
            journal_entry_id=je.id if je else None,
            balance_after=balance_after,
            created_by=user_id,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    def record_bank_interest(
        self,
        bank_account_id: int,
        amount: Decimal,
        description: str,
        reference: str,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> TreasuryTransaction:
        account = self.get_bank_account_by_id(bank_account_id, company_id)
        if not account:
            raise ValueError("Bank account not found")

        account.current_balance += amount
        balance_after = account.current_balance

        je = None
        interest_account = self._get_account_by_code(company_id, "4200")
        if interest_account and account.linked_account_id:
            je = self._create_journal_entry(
                company_id=company_id,
                description=description or f"Intereses ganados - {account.bank_name}",
                reference=reference,
                lines=[
                    (
                        account.linked_account_id,
                        amount,
                        Decimal("0.00"),
                        f"Intereses ganados",
                    ),
                    (
                        interest_account.id,
                        Decimal("0.00"),
                        amount,
                        f"Intereses - {account.name}",
                    ),
                ],
            )

        self.db.commit()
        self.db.refresh(account)

        tx = TreasuryTransaction(
            company_id=company_id,
            account_type="BANK",
            bank_account_id=bank_account_id,
            cash_account_id=None,
            transaction_type="INTEREST",
            amount=amount,
            description=description,
            reference=reference,
            journal_entry_id=je.id if je else None,
            balance_after=balance_after,
            created_by=user_id,
        )
        self.db.add(tx)
        self.db.commit()
        self.db.refresh(tx)
        return tx

    # ──────────────────────────────────────────────
    # Check Register
    # ──────────────────────────────────────────────

    def issue_check(
        self,
        data: treasury_schema.CheckRegisterCreate,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> CheckRegister:
        account = self.get_bank_account_by_id(data.bank_account_id, company_id)
        if not account:
            raise ValueError("Bank account not found")
        if account.current_balance < data.amount:
            raise ValueError("Insufficient balance to issue check")

        account.current_balance -= data.amount
        balance_after = account.current_balance

        je = None
        if account.linked_account_id:
            payable_account = self._get_account_by_code(company_id, "2110")
            contra_id = (
                payable_account.id if payable_account else account.linked_account_id
            )
            je = self._create_journal_entry(
                company_id=company_id,
                description=f"Cheque #{data.check_number} a {data.payee}",
                reference=f"CHK-{data.check_number}",
                lines=[
                    (
                        contra_id,
                        data.amount,
                        Decimal("0.00"),
                        f"Cheque #{data.check_number} - {data.payee}",
                    ),
                    (
                        account.linked_account_id,
                        Decimal("0.00"),
                        data.amount,
                        f"Cheque emitido - {account.name}",
                    ),
                ],
            )

        self.db.commit()
        self.db.refresh(account)

        tx = TreasuryTransaction(
            company_id=company_id,
            account_type="BANK",
            bank_account_id=data.bank_account_id,
            cash_account_id=None,
            transaction_type="CHECK_ISSUED",
            amount=data.amount,
            description=f"Cheque #{data.check_number} a {data.payee}",
            reference=f"CHK-{data.check_number}",
            journal_entry_id=je.id if je else None,
            balance_after=balance_after,
            created_by=user_id,
        )
        self.db.add(tx)
        self.db.flush()

        check = CheckRegister(
            company_id=company_id,
            bank_account_id=data.bank_account_id,
            check_number=data.check_number,
            payee=data.payee,
            amount=data.amount,
            issue_date=data.issue_date,
            status="ISSUED",
            notes=data.notes,
            linked_transaction_id=tx.id,
        )
        self.db.add(check)
        self.db.commit()
        self.db.refresh(check)
        return check

    def update_check_status(
        self,
        check_id: int,
        new_status: str,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> Optional[CheckRegister]:
        check = (
            self.db.query(CheckRegister)
            .filter(
                CheckRegister.id == check_id,
                CheckRegister.company_id == company_id,
            )
            .first()
        )
        if not check:
            return None

        valid_transitions = {
            "ISSUED": ["DELIVERED", "VOIDED"],
            "DELIVERED": ["CLEARED", "BOUNCED", "VOIDED"],
            "CLEARED": [],
            "BOUNCED": [],
            "VOIDED": [],
        }

        if new_status not in valid_transitions.get(check.status, []):
            raise ValueError(f"Cannot transition from {check.status} to {new_status}")

        old_status = check.status
        check.status = new_status

        if new_status in ("CLEARED", "BOUNCED"):
            check.cleared_date = datetime.now(timezone.utc)

        if new_status == "BOUNCED" and old_status != "BOUNCED":
            account = self.get_bank_account_by_id(check.bank_account_id, company_id)
            if account:
                account.current_balance += check.amount
                self.db.commit()
                self.db.refresh(account)

                je = None
                if account.linked_account_id:
                    payable_account = self._get_account_by_code(company_id, "2110")
                    contra_id = (
                        payable_account.id
                        if payable_account
                        else account.linked_account_id
                    )
                    je = self._create_journal_entry(
                        company_id=company_id,
                        description=f"Cheque #{check.check_number} devuelto",
                        reference=f"CHK-BOUNCE-{check.check_number}",
                        lines=[
                            (
                                account.linked_account_id,
                                check.amount,
                                Decimal("0.00"),
                                f"Cheque devuelto - reverso",
                            ),
                            (
                                contra_id,
                                Decimal("0.00"),
                                check.amount,
                                f"Cheque #{check.check_number} devuelto",
                            ),
                        ],
                    )

                tx = TreasuryTransaction(
                    company_id=company_id,
                    account_type="BANK",
                    bank_account_id=check.bank_account_id,
                    cash_account_id=None,
                    transaction_type="CHECK_BOUNCED",
                    amount=check.amount,
                    description=f"Cheque #{check.check_number} devuelto",
                    reference=f"CHK-BOUNCE-{check.check_number}",
                    journal_entry_id=je.id if je else None,
                    balance_after=account.current_balance,
                    created_by=user_id,
                )
                self.db.add(tx)

        elif new_status == "VOIDED" and old_status not in ("CLEARED", "VOIDED"):
            account = self.get_bank_account_by_id(check.bank_account_id, company_id)
            if account:
                account.current_balance += check.amount
                self.db.commit()
                self.db.refresh(account)

                je = None
                if account.linked_account_id:
                    payable_account = self._get_account_by_code(company_id, "2110")
                    contra_id = (
                        payable_account.id
                        if payable_account
                        else account.linked_account_id
                    )
                    je = self._create_journal_entry(
                        company_id=company_id,
                        description=f"Cheque #{check.check_number} anulado",
                        reference=f"CHK-VOID-{check.check_number}",
                        lines=[
                            (
                                account.linked_account_id,
                                check.amount,
                                Decimal("0.00"),
                                f"Cheque anulado - reverso",
                            ),
                            (
                                contra_id,
                                Decimal("0.00"),
                                check.amount,
                                f"Cheque #{check.check_number} anulado",
                            ),
                        ],
                    )

                tx = TreasuryTransaction(
                    company_id=company_id,
                    account_type="BANK",
                    bank_account_id=check.bank_account_id,
                    cash_account_id=None,
                    transaction_type="CHECK_ISSUED",
                    amount=check.amount,
                    description=f"Cheque #{check.check_number} anulado",
                    reference=f"CHK-VOID-{check.check_number}",
                    journal_entry_id=je.id if je else None,
                    balance_after=account.current_balance,
                    created_by=user_id,
                )
                self.db.add(tx)

        self.db.commit()
        self.db.refresh(check)
        return check

    def get_checks(
        self,
        company_id: int,
        bank_account_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[CheckRegister]:
        query = self.db.query(CheckRegister).filter(
            CheckRegister.company_id == company_id
        )
        if bank_account_id:
            query = query.filter(CheckRegister.bank_account_id == bank_account_id)
        if status:
            query = query.filter(CheckRegister.status == status)
        return (
            query.order_by(CheckRegister.issue_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ──────────────────────────────────────────────
    # Summary & Reports
    # ──────────────────────────────────────────────

    def get_treasury_summary(self, company_id: int) -> Dict[str, Any]:
        bank_accounts = (
            self.db.query(BankAccount)
            .filter(
                BankAccount.company_id == company_id,
                BankAccount.is_active == True,
            )
            .all()
        )
        cash_accounts = (
            self.db.query(CashAccount)
            .filter(
                CashAccount.company_id == company_id,
                CashAccount.is_active == True,
            )
            .all()
        )

        bank_list = []
        total_banks = Decimal("0.00")
        for ba in bank_accounts:
            bank_list.append(
                treasury_schema.TreasurySummaryAccount(
                    id=ba.id,
                    name=ba.name,
                    type="BANK",
                    bank_name=ba.bank_name,
                    account_number=ba.account_number,
                    account_type_detail=ba.account_type,
                    balance=ba.current_balance,
                    currency=ba.currency,
                )
            )
            total_banks += ba.current_balance

        cash_list = []
        total_cash = Decimal("0.00")
        for ca in cash_accounts:
            cash_list.append(
                treasury_schema.TreasurySummaryAccount(
                    id=ca.id,
                    name=ca.name,
                    type="CASH",
                    bank_name=None,
                    account_number=None,
                    account_type_detail=ca.account_type,
                    balance=ca.current_balance,
                    currency=ca.currency,
                )
            )
            total_cash += ca.current_balance

        return {
            "company_id": company_id,
            "total_banks": total_banks,
            "total_cash": total_cash,
            "total_treasury": total_banks + total_cash,
            "bank_accounts": bank_list,
            "cash_accounts": cash_list,
        }

    def get_cash_flow(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        query = self.db.query(TreasuryTransaction).filter(
            TreasuryTransaction.company_id == company_id,
        )
        if date_from:
            query = query.filter(TreasuryTransaction.created_at >= date_from)
        if date_to:
            end_of_day = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(TreasuryTransaction.created_at <= end_of_day)

        transactions = query.order_by(TreasuryTransaction.created_at).all()

        inflow_types = ("DEPOSIT", "TRANSFER_IN", "INTEREST", "CHECK_CLEARED")
        outflow_types = (
            "WITHDRAWAL",
            "TRANSFER_OUT",
            "FEE",
            "CHECK_ISSUED",
            "CHECK_BOUNCED",
        )

        entries = []
        total_inflows = Decimal("0.00")
        total_outflows = Decimal("0.00")

        for tx in transactions:
            account_name = ""
            if tx.bank_account_id:
                ba = self.get_bank_account_by_id(tx.bank_account_id, company_id)
                account_name = ba.name if ba else f"Bank #{tx.bank_account_id}"
            elif tx.cash_account_id:
                ca = self.get_cash_account_by_id(tx.cash_account_id, company_id)
                account_name = ca.name if ca else f"Cash #{tx.cash_account_id}"

            entry = treasury_schema.CashFlowEntry(
                date=tx.created_at,
                account_type=tx.account_type,
                account_name=account_name,
                transaction_type=tx.transaction_type,
                amount=tx.amount,
                description=tx.description,
                reference=tx.reference,
            )
            entries.append(entry)

            if tx.transaction_type in inflow_types:
                total_inflows += tx.amount
            elif tx.transaction_type in outflow_types:
                total_outflows += tx.amount

        return {
            "company_id": company_id,
            "date_from": date_from,
            "date_to": date_to,
            "total_inflows": total_inflows,
            "total_outflows": total_outflows,
            "net_flow": total_inflows - total_outflows,
            "entries": entries,
        }

    def get_treasury_transactions(
        self,
        company_id: int,
        account_type: Optional[str] = None,
        transaction_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TreasuryTransaction]:
        query = self.db.query(TreasuryTransaction).filter(
            TreasuryTransaction.company_id == company_id
        )
        if account_type:
            query = query.filter(TreasuryTransaction.account_type == account_type)
        if transaction_type:
            query = query.filter(
                TreasuryTransaction.transaction_type == transaction_type
            )
        if date_from:
            query = query.filter(TreasuryTransaction.created_at >= date_from)
        if date_to:
            end_of_day = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(TreasuryTransaction.created_at <= end_of_day)

        return (
            query.order_by(TreasuryTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    # ──────────────────────────────────────────────
    # Bank Reconciliation
    # ──────────────────────────────────────────────

    def create_reconciliation(
        self,
        data: treasury_schema.BankReconciliationCreate,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> BankReconciliation:
        account = self.get_bank_account_by_id(data.bank_account_id, company_id)
        if not account:
            raise ValueError("Bank account not found")

        recon = BankReconciliation(
            company_id=company_id,
            bank_account_id=data.bank_account_id,
            statement_date=data.statement_date,
            statement_balance=data.statement_balance,
            system_balance=account.current_balance,
            reconciled_by=user_id,
            notes=data.notes,
        )
        self.db.add(recon)
        self.db.commit()
        self.db.refresh(recon)
        return recon

    def match_transaction(
        self,
        reconciliation_id: int,
        data: treasury_schema.MatchTransactionRequest,
        company_id: int,
    ) -> ReconciliationLine:
        recon = (
            self.db.query(BankReconciliation)
            .filter(
                BankReconciliation.id == reconciliation_id,
                BankReconciliation.company_id == company_id,
            )
            .first()
        )
        if not recon:
            raise ValueError("Reconciliation not found")
        if recon.status == "COMPLETED":
            raise ValueError("Cannot modify completed reconciliation")

        tx = (
            self.db.query(TreasuryTransaction)
            .filter(
                TreasuryTransaction.id == data.treasury_transaction_id,
                TreasuryTransaction.company_id == company_id,
            )
            .first()
        )
        if not tx:
            raise ValueError("Transaction not found")

        line = ReconciliationLine(
            reconciliation_id=reconciliation_id,
            treasury_transaction_id=data.treasury_transaction_id,
            is_matched=True,
            amount=tx.amount,
            description=data.description or tx.description,
            statement_date=data.statement_date,
            system_date=tx.created_at,
            difference=Decimal("0.00"),
        )
        self.db.add(line)
        self.db.commit()
        self.db.refresh(line)
        return line

    def add_outstanding_item(
        self,
        reconciliation_id: int,
        data: treasury_schema.AddOutstandingItemRequest,
        company_id: int,
    ) -> ReconciliationLine:
        recon = (
            self.db.query(BankReconciliation)
            .filter(
                BankReconciliation.id == reconciliation_id,
                BankReconciliation.company_id == company_id,
            )
            .first()
        )
        if not recon:
            raise ValueError("Reconciliation not found")
        if recon.status == "COMPLETED":
            raise ValueError("Cannot modify completed reconciliation")

        if data.item_type == "OUTSTANDING_DEPOSIT":
            recon.outstanding_deposits += data.amount
        elif data.item_type == "OUTSTANDING_CHECK":
            recon.outstanding_checks += data.amount

        line = ReconciliationLine(
            reconciliation_id=reconciliation_id,
            treasury_transaction_id=None,
            is_matched=False,
            amount=data.amount,
            description=data.description,
            difference=data.amount,
        )
        self.db.add(line)
        self.db.commit()
        self.db.refresh(line)
        return line

    def complete_reconciliation(
        self,
        reconciliation_id: int,
        company_id: int,
        user_id: Optional[int] = None,
    ) -> BankReconciliation:
        recon = (
            self.db.query(BankReconciliation)
            .filter(
                BankReconciliation.id == reconciliation_id,
                BankReconciliation.company_id == company_id,
            )
            .first()
        )
        if not recon:
            raise ValueError("Reconciliation not found")

        adjusted = (
            recon.statement_balance
            + recon.outstanding_deposits
            - recon.outstanding_checks
        )
        recon.adjusted_balance = adjusted
        recon.is_balanced = abs(adjusted - recon.system_balance) < Decimal("0.01")
        recon.status = "COMPLETED"
        recon.reconciled_by = user_id
        recon.reconciled_at = datetime.now(timezone.utc)

        if recon.bank_fees_not_recorded > 0 or recon.interest_not_recorded > 0:
            account = self.get_bank_account_by_id(recon.bank_account_id, company_id)
            if account and account.linked_account_id:
                lines = []
                if recon.bank_fees_not_recorded > 0:
                    fee_acct = self._get_account_by_code(company_id, "5400")
                    if fee_acct:
                        lines.append(
                            (
                                fee_acct.id,
                                recon.bank_fees_not_recorded,
                                Decimal("0.00"),
                                "Comision no registrada",
                            )
                        )
                        lines.append(
                            (
                                account.linked_account_id,
                                Decimal("0.00"),
                                recon.bank_fees_not_recorded,
                                "Ajuste comision",
                            )
                        )
                if recon.interest_not_recorded > 0:
                    int_acct = self._get_account_by_code(company_id, "4200")
                    if int_acct:
                        lines.append(
                            (
                                account.linked_account_id,
                                recon.interest_not_recorded,
                                Decimal("0.00"),
                                "Interes no registrado",
                            )
                        )
                        lines.append(
                            (
                                int_acct.id,
                                Decimal("0.00"),
                                recon.interest_not_recorded,
                                "Ajuste interes",
                            )
                        )

                if lines:
                    self._create_journal_entry(
                        company_id=company_id,
                        description=f"Ajustes conciliacion - Recon #{recon.id}",
                        reference=f"RECON-ADJ-{recon.id:06d}",
                        lines=lines,
                    )

        self.db.commit()
        self.db.refresh(recon)
        return recon

    def get_reconciliation_by_id(
        self, recon_id: int, company_id: int
    ) -> Optional[BankReconciliation]:
        return (
            self.db.query(BankReconciliation)
            .options(joinedload(BankReconciliation.lines))
            .filter(
                BankReconciliation.id == recon_id,
                BankReconciliation.company_id == company_id,
            )
            .first()
        )

    def get_reconciliations(
        self,
        company_id: int,
        bank_account_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BankReconciliation]:
        query = self.db.query(BankReconciliation).filter(
            BankReconciliation.company_id == company_id
        )
        if bank_account_id:
            query = query.filter(BankReconciliation.bank_account_id == bank_account_id)
        return (
            query.order_by(BankReconciliation.statement_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
