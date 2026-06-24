from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func as sql_func
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from datetime import date, time

from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql import company as company_model
from app.models.sql.fiscal_period import FiscalPeriod
from app.models.sql.invoicing import Invoice, InvoiceItem
from app.models.sql.purchases import Purchase
from app.models.sql.partners import Partner
from app.schemas import accounting as co_schema


class AccountingService:
    def __init__(self, db: Session):
        self.db = db

    # Chart of Accounts methods
    def create_chart_of_accounts(
        self, coa: co_schema.ChartOfAccountsCreate, company_id: int
    ) -> ChartOfAccounts:
        db_coa = ChartOfAccounts(**coa.model_dump(), company_id=company_id)
        self.db.add(db_coa)
        self.db.commit()
        self.db.refresh(db_coa)
        return db_coa

    def get_chart_of_accounts(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChartOfAccounts]:
        return (
            self.db.query(ChartOfAccounts)
            .filter(ChartOfAccounts.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_chart_of_account_by_id(
        self, coa_id: int, company_id: int
    ) -> Optional[ChartOfAccounts]:
        return (
            self.db.query(ChartOfAccounts)
            .filter(
                and_(
                    ChartOfAccounts.id == coa_id,
                    ChartOfAccounts.company_id == company_id,
                )
            )
            .first()
        )

    def update_chart_of_accounts(
        self, coa_id: int, coa: co_schema.ChartOfAccountsCreate, company_id: int
    ) -> Optional[ChartOfAccounts]:
        db_coa = self.get_chart_of_account_by_id(coa_id, company_id)
        if db_coa:
            for key, value in coa.model_dump().items():
                setattr(db_coa, key, value)
            self.db.commit()
            self.db.refresh(db_coa)
        return db_coa

    def delete_chart_of_accounts(self, coa_id: int, company_id: int) -> bool:
        db_coa = self.get_chart_of_account_by_id(coa_id, company_id)
        if db_coa:
            self.db.delete(db_coa)
            self.db.commit()
            return True
        return False

    # Journal Entry methods
    def create_journal_entry(
        self, je: co_schema.JournalEntryCreate, company_id: int
    ) -> JournalEntry:
        db_je = JournalEntry(**je.model_dump(), company_id=company_id)
        self.db.add(db_je)
        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    def create_journal_entry_with_lines(
        self, je_with_lines: co_schema.JournalEntryWithLinesCreate, company_id: int
    ) -> JournalEntry:
        # Validate balance before creating any records
        total_debits = sum(line.debit_amount for line in je_with_lines.lines)
        total_credits = sum(line.credit_amount for line in je_with_lines.lines)
        if total_debits != total_credits:
            raise ValueError(
                f"Journal entry must be balanced (debits={total_debits} != credits={total_credits})"
            )

        # Create the journal entry
        # Verify entry date falls within an open fiscal period
        fp = (
            self.db.query(FiscalPeriod)
            .filter(
                FiscalPeriod.company_id == company_id,
                FiscalPeriod.start_date <= je_with_lines.entry_date,
                FiscalPeriod.end_date >= je_with_lines.entry_date,
            )
            .first()
        )
        any_periods = self.db.query(FiscalPeriod).filter(FiscalPeriod.company_id == company_id).first()
        if any_periods is not None:
            if fp is None:
                raise ValueError("No fiscal period defined for the entry date")
            if fp.is_closed:
                raise ValueError("Fiscal period is closed for the entry date")
        elif fp is not None and fp.is_closed:
            raise ValueError("Fiscal period is closed for the entry date")
        db_je = JournalEntry(
            entry_date=je_with_lines.entry_date,
            description=je_with_lines.description,
            reference=je_with_lines.reference,
            company_id=company_id,
        )
        self.db.add(db_je)
        self.db.flush()  # To get the ID without committing

        # Create the journal entry lines
        for line in je_with_lines.lines:
            db_jel = JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=line.account_id,
                debit_amount=line.debit_amount,
                credit_amount=line.credit_amount,
                description=line.description,
            )
            self.db.add(db_jel)

        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    def get_journal_entries(
        self, company_id: int, skip: int = 0, limit: int = 100
    ) -> List[JournalEntry]:
        return (
            self.db.query(JournalEntry)
            .options(
                joinedload(JournalEntry.lines).joinedload(JournalEntryLine.account)
            )
            .filter(JournalEntry.company_id == company_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_journal_entry_by_id(
        self, je_id: int, company_id: int
    ) -> Optional[JournalEntry]:
        return (
            self.db.query(JournalEntry)
            .filter(
                and_(
                    JournalEntry.id == je_id,
                    JournalEntry.company_id == company_id,
                )
            )
            .first()
        )

    def get_journal_entry_with_lines(
        self, je_id: int, company_id: int
    ) -> Optional[JournalEntry]:
        je = (
            self.db.query(JournalEntry)
            .options(
                joinedload(JournalEntry.lines).joinedload(JournalEntryLine.account)
            )
            .filter(
                and_(
                    JournalEntry.id == je_id,
                    JournalEntry.company_id == company_id,
                )
            )
            .first()
        )
        return je

    def reverse_journal_entry(
        self, je_id: int, company_id: int, description: Optional[str] = None, commit: bool = True
    ) -> JournalEntry:
        """
        Creates a reversing entry for an existing journal entry.
        Swaps debits and credits of the original lines.
        """
        original_je = self.get_journal_entry_by_id(je_id, company_id)
        if not original_je:
            raise ValueError("Original journal entry not found")

        # Eager load the lines if not already loaded
        self.db.refresh(original_je, attribute_names=["lines"])

        # Create the new journal entry
        reverse_date = datetime.now(timezone.utc)
        reverse_je = JournalEntry(
            entry_date=reverse_date,
            description=description or f"Reversión de asiento: {original_je.description}",
            reference=f"REV-{original_je.reference or original_je.id}",
            company_id=company_id,
            is_posted=True,  # Reversing entries are usually posted immediately
        )
        self.db.add(reverse_je)
        self.db.flush()

        for line in original_je.lines:
            reverse_line = JournalEntryLine(
                journal_entry_id=reverse_je.id,
                account_id=line.account_id,
                debit_amount=line.credit_amount,  # Original credit becomes debit
                credit_amount=line.debit_amount,  # Original debit becomes credit
                description=f"Reversión: {line.description}",
            )
            self.db.add(reverse_line)

        # Verify reversal date falls within an open fiscal period
        fp = (
            self.db.query(FiscalPeriod)
            .filter(
                FiscalPeriod.company_id == company_id,
                FiscalPeriod.start_date <= reverse_date,
                FiscalPeriod.end_date >= reverse_date,
            )
            .first()
        )
        any_periods = self.db.query(FiscalPeriod).filter(FiscalPeriod.company_id == company_id).first()
        if any_periods is not None:
            if fp is None:
                raise ValueError("No fiscal period defined for the reversal date")
            if fp.is_closed:
                raise ValueError("Cannot reverse entry: the fiscal period is closed")

        if commit:
            self.db.commit()
            self.db.refresh(reverse_je)
        return reverse_je

    def get_journal_entry_lines_detail(
        self, je_id: int, company_id: int
    ) -> Optional[Dict[str, Any]]:
        je = (
            self.db.query(JournalEntry)
            .options(joinedload(JournalEntry.lines).joinedload(JournalEntryLine.account))
            .filter(
                and_(
                    JournalEntry.id == je_id,
                    JournalEntry.company_id == company_id,
                )
            )
            .first()
        )
        if not je:
            return None

        lines_detail = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        for line in je.lines:
            lines_detail.append(
                {
                    "id": line.id,
                    "account_id": line.account_id,
                    "account_code": line.account.code if line.account else "",
                    "account_name": line.account.name if line.account else "",
                    "debit_amount": line.debit_amount,
                    "credit_amount": line.credit_amount,
                    "description": line.description,
                }
            )
            total_debit += line.debit_amount
            total_credit += line.credit_amount

        return {
            "entry_id": je.id,
            "entry_date": je.entry_date,
            "description": je.description,
            "reference": je.reference,
            "is_posted": je.is_posted,
            "lines": lines_detail,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "is_balanced": total_debit == total_credit,
        }

    def post_journal_entry(self, je_id: int, company_id: int) -> Dict[str, Any]:
        db_je = self.db.query(JournalEntry).filter(JournalEntry.id == je_id, JournalEntry.company_id == company_id).with_for_update().first()
        if not db_je:
            raise ValueError("Journal entry not found")
        if db_je.is_posted:
            raise ValueError("Journal entry is already posted and cannot be posted again")

        # Verify entry date falls within an open fiscal period
        fp = (
            self.db.query(FiscalPeriod)
            .filter(
                FiscalPeriod.company_id == company_id,
                FiscalPeriod.start_date <= db_je.entry_date,
                FiscalPeriod.end_date >= db_je.entry_date,
            )
            .first()
        )
        # If company has any fiscal periods defined, require entry date to fall within an OPEN period
        any_periods = self.db.query(FiscalPeriod).filter(FiscalPeriod.company_id == company_id).first()
        if any_periods is not None:
            if fp is None:
                raise ValueError("No fiscal period defined for the entry date")
            if fp.is_closed:
                raise ValueError("Fiscal period is closed for the entry date")
        elif fp is not None and fp.is_closed:
            raise ValueError("Fiscal period is closed for the entry date")

        lines = (
            self.db.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == je_id)
            .all()
        )

        sum_debits = sum((line.debit_amount for line in lines), Decimal("0.00"))
        sum_credits = sum((line.credit_amount for line in lines), Decimal("0.00"))

        if sum_debits != sum_credits:
            raise ValueError("Journal entry must be balanced (debits = credits)")

        db_je.is_posted = True

        from app.models.sql.accounting.bank_account import BankAccount
        from app.models.sql.accounting.cash_account import CashAccount
        from app.models.sql.accounting.treasury_transaction import TreasuryTransaction

        treasury_sync_count = 0

        for line in lines:
            if not line.account_id:
                continue

            line_coa = (
                self.db.query(ChartOfAccounts)
                .filter(ChartOfAccounts.id == line.account_id)
                .first()
            )
            if not line_coa:
                continue

            line_code = line_coa.code

            bank_acct = (
                self.db.query(BankAccount)
                .filter(
                    BankAccount.linked_account_id == line.account_id,
                    BankAccount.company_id == company_id,
                    BankAccount.is_active == True,
                )
                .with_for_update()
                .first()
            )

            if not bank_acct:
                # Try to find a bank account whose linked COA code matches the line code exactly
                all_bank_accts = (
                    self.db.query(BankAccount)
                    .filter(
                        BankAccount.company_id == company_id,
                        BankAccount.is_active == True,
                        BankAccount.linked_account_id != None,
                    )
                    .all()
                )
                for candidate in all_bank_accts:
                    if candidate.linked_account_id:
                        candidate_coa = (
                            self.db.query(ChartOfAccounts)
                            .filter(ChartOfAccounts.id == candidate.linked_account_id)
                            .first()
                        )
                        if candidate_coa:
                            c_code = candidate_coa.code
                            if line_code.startswith(c_code) or c_code.startswith(line_code):
                                bank_acct = candidate
                                break

            if bank_acct:
                net_change = line.debit_amount - line.credit_amount
                bank_acct.current_balance += net_change
                if net_change != Decimal("0.00"):
                    tx_type = "DEPOSIT" if net_change > 0 else "WITHDRAWAL"
                    tx = TreasuryTransaction(
                        company_id=company_id,
                        account_type="BANK",
                        bank_account_id=bank_acct.id,
                        cash_account_id=None,
                        transaction_type=tx_type,
                        amount=abs(net_change),
                        description=line.description or db_je.description,
                        reference=db_je.reference or f"JE-{je_id}",
                        journal_entry_id=db_je.id,
                        balance_after=bank_acct.current_balance,
                    )
                    self.db.add(tx)
                    treasury_sync_count += 1
                continue

            cash_acct = (
                self.db.query(CashAccount)
                .filter(
                    CashAccount.linked_account_id == line.account_id,
                    CashAccount.company_id == company_id,
                    CashAccount.is_active == True,
                )
                .with_for_update()
                .first()
            )

            if not cash_acct:
                # Attempt to find a cash account with a linked COA that matches the line code exactly
                all_cash_accts = (
                    self.db.query(CashAccount)
                    .filter(
                        CashAccount.company_id == company_id,
                        CashAccount.is_active == True,
                        CashAccount.linked_account_id != None,
                    )
                    .all()
                )
                for candidate in all_cash_accts:
                    if candidate.linked_account_id:
                        candidate_coa = (
                            self.db.query(ChartOfAccounts)
                            .filter(ChartOfAccounts.id == candidate.linked_account_id)
                            .first()
                        )
                        if candidate_coa:
                            c_code = candidate_coa.code
                            if line_code.startswith(c_code) or c_code.startswith(line_code):
                                cash_acct = candidate
                                break
                if not cash_acct:
                    continue

            if cash_acct:
                net_change = line.debit_amount - line.credit_amount
                cash_acct.current_balance += net_change
                if net_change != Decimal("0.00"):
                    tx_type = "DEPOSIT" if net_change > 0 else "WITHDRAWAL"
                    tx = TreasuryTransaction(
                        company_id=company_id,
                        account_type="CASH",
                        bank_account_id=None,
                        cash_account_id=cash_acct.id,
                        transaction_type=tx_type,
                        amount=abs(net_change),
                        description=line.description or db_je.description,
                        reference=db_je.reference or f"JE-{je_id}",
                        journal_entry_id=db_je.id,
                        balance_after=cash_acct.current_balance,
                    )
                    self.db.add(tx)
                    treasury_sync_count += 1

        self.db.commit()
        self.db.refresh(db_je)

        warning = None
        if treasury_sync_count == 0:
            warning = (
                "Asiento publicado, pero ninguna línea afecta cuentas de tesorería. "
                "Verifique que las cuentas bancarias/caja tengan configurado el campo "
                "'Cuenta contable vinculada' (linked_account_id) en el módulo de Tesorería."
            )

        return {
            "id": db_je.id,
            "company_id": db_je.company_id,
            "entry_date": db_je.entry_date,
            "description": db_je.description,
            "reference": db_je.reference,
            "is_posted": db_je.is_posted,
            "created_at": db_je.created_at,
            "updated_at": db_je.updated_at,
            "treasury_sync_count": treasury_sync_count,
            "warning": warning,
        }

    def get_trial_balance(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generates Trial Balance matching sum of debits and credits
        """
        accounts_query = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
        )
        
        accounts = accounts_query.order_by(ChartOfAccounts.code).all()

        date_filter = [
            JournalEntry.company_id == company_id,
            JournalEntry.is_posted == True
        ]
        
        if date_from:
            date_filter.append(JournalEntry.entry_date >= date_from)
        if date_to:
            end_of_day = date_to.replace(hour=23, minute=59, second=59)
            date_filter.append(JournalEntry.entry_date <= end_of_day)

        result_accounts = []
        total_debit_balance = Decimal("0.00")
        total_credit_balance = Decimal("0.00")

        for account in accounts:
            lines = (
                self.db.query(JournalEntryLine)
                .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
                .filter(JournalEntryLine.account_id == account.id)
                .filter(and_(*date_filter))
                .all()
            )
            
            debits = sum([l.debit_amount for l in lines]) if lines else Decimal("0.00")
            credits = sum([l.credit_amount for l in lines]) if lines else Decimal("0.00")

            if account.account_type in ("ASSET", "EXPENSE", "COST"):
                net_balance = debits - credits
            else:
                net_balance = credits - debits
                
            debit_balance = debits
            credit_balance = credits
            
            # Optionally, you can only include accounts with movements or a non-zero balance
            if debits > 0 or credits > 0 or net_balance != 0:
                result_accounts.append({
                    "account_id": account.id,
                    "account_code": account.code,
                    "account_name": account.name,
                    "account_type": account.account_type,
                    "debit_balance": debit_balance,
                    "credit_balance": credit_balance,
                    "net_balance": net_balance,
                })
                
                total_debit_balance += debit_balance
                total_credit_balance += credit_balance
                
        is_balanced = total_debit_balance == total_credit_balance
        difference = total_debit_balance - total_credit_balance
        
        # Determine period string
        period_str = ""
        if date_from and date_to:
            period_str = f"{date_from.strftime('%Y-%m-%d')} to {date_to.strftime('%Y-%m-%d')}"
        elif date_from:
            period_str = f"From {date_from.strftime('%Y-%m-%d')}"
        elif date_to:
            period_str = f"Up to {date_to.strftime('%Y-%m-%d')}"
        else:
            period_str = "All time"

        return {
            "company_id": company_id,
            "period": period_str,
            "generated_at": datetime.now(timezone.utc),
            "accounts": result_accounts,
            "total_debit_balance": total_debit_balance,
            "total_credit_balance": total_credit_balance,
            "is_balanced": is_balanced,
            "difference": difference,
        }

    def get_libro_mayor(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        account_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Libro Mayor generalizado según normativa colombiana.
        Muestra movimientos y saldos por cuenta contable con:
        - Saldo inicial
        - Débitos del período
        - Créditos del período
        - Saldo final

        Cumple con: Decreto 2420/2015, Art. 1.6.1.4.1 ET
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        accounts_query = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.is_active == True,
        )

        if account_code:
            accounts_query = accounts_query.filter(ChartOfAccounts.code == account_code)

        accounts = accounts_query.order_by(ChartOfAccounts.code).all()

        date_filter = []
        if date_from:
            date_filter.append(JournalEntry.entry_date >= date_from)
        if date_to:
            end_of_day = date_to.replace(hour=23, minute=59, second=59)
            date_filter.append(JournalEntry.entry_date <= end_of_day)

        result_accounts = []
        grand_total_debits = Decimal("0.00")
        grand_total_credits = Decimal("0.00")

        for account in accounts:
            lines_query = (
                self.db.query(JournalEntryLine, JournalEntry)
                .join(
                    JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id
                )
                .filter(
                    JournalEntryLine.account_id == account.id,
                    JournalEntry.company_id == company_id,
                    JournalEntry.is_posted == True,
                )
            )

            if date_filter:
                lines_query = lines_query.filter(and_(*date_filter))

            lines_query = lines_query.order_by(JournalEntry.entry_date, JournalEntry.id)

            raw_lines = lines_query.all()

            saldo_inicial = Decimal("0.00")
            if date_from:
                initial_lines = (
                    self.db.query(JournalEntryLine, JournalEntry)
                    .join(
                        JournalEntry,
                        JournalEntryLine.journal_entry_id == JournalEntry.id,
                    )
                    .filter(
                        JournalEntryLine.account_id == account.id,
                        JournalEntry.company_id == company_id,
                        JournalEntry.is_posted == True,
                        JournalEntry.entry_date < date_from,
                    )
                    .all()
                )
                for jel, je in initial_lines:
                    if account.account_type in ("ASSET", "EXPENSE", "COST"):
                        saldo_inicial += jel.debit_amount - jel.credit_amount
                    else:
                        saldo_inicial += jel.credit_amount - jel.debit_amount

            total_debits = Decimal("0.00")
            total_credits = Decimal("0.00")
            account_lines = []
            running_balance = saldo_inicial

            for jel, je in raw_lines:
                total_debits += jel.debit_amount
                total_credits += jel.credit_amount

                if account.account_type in ("ASSET", "EXPENSE", "COST"):
                    running_balance += jel.debit_amount - jel.credit_amount
                else:
                    running_balance += jel.credit_amount - jel.debit_amount

                account_lines.append(
                    {
                        "entry_date": je.entry_date,
                        "reference": je.reference,
                        "description": jel.description,
                        "debit": jel.debit_amount,
                        "credit": jel.credit_amount,
                        "balance": running_balance,
                    }
                )

            if account.account_type in ("ASSET", "EXPENSE", "COST"):
                saldo_final = saldo_inicial + total_debits - total_credits
            else:
                saldo_final = saldo_inicial + total_credits - total_debits

            grand_total_debits += total_debits
            grand_total_credits += total_credits

            if raw_lines or saldo_inicial != Decimal("0.00"):
                result_accounts.append(
                    {
                        "account_code": account.code,
                        "account_name": account.name,
                        "account_type": account.account_type,
                        "initial_balance": saldo_inicial,
                        "total_debits": total_debits,
                        "total_credits": total_credits,
                        "final_balance": saldo_final,
                        "lines": account_lines,
                    }
                )

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "accounts": result_accounts,
            "grand_total_debits": grand_total_debits,
            "grand_total_credits": grand_total_credits,
        }

    def _parse_tax_rate(self, rate_value) -> Decimal:
        """Normalize tax rate to decimal (handles both percentage and decimal forms)"""
        rate = Decimal(str(rate_value))
        if rate > 1:
            rate = rate / Decimal("100")
        return rate

    def _is_approx_equal(
        self, a: Decimal, b: Decimal, tolerance: str = "0.001"
    ) -> bool:
        """Compare decimals with tolerance to avoid floating point issues"""
        return abs(a - b) < Decimal(tolerance)

    def _get_invoice_tax_breakdown(self, invoice: Invoice) -> Dict[str, Decimal]:
        """
        Desglosa impuestos de una factura por tasa de IVA.
        Clasifica según tarifas colombianas: 19% (general), 5% (reducida), 0% (exento), excluido.
        Retorna: base_iva_19, iva_19, base_iva_5, iva_5, base_no_iva, total_iva
        """
        base_iva_19 = Decimal("0.00")
        iva_19 = Decimal("0.00")
        base_iva_5 = Decimal("0.00")
        iva_5 = Decimal("0.00")
        base_no_iva = Decimal("0.00")

        if hasattr(invoice, "items") and invoice.items:
            for item in invoice.items:
                item_tax_amount = item.tax_amount if item.tax_amount is not None else Decimal("0.00")
                line_base = item.line_total - item_tax_amount
                if line_base < 0:
                    line_base = Decimal("0.00")

                tax_rate_val = item.tax_rate if item.tax_rate is not None else Decimal("0.00")
                tax_rate = self._parse_tax_rate(tax_rate_val)

                if self._is_approx_equal(tax_rate, Decimal("0.19")):
                    base_iva_19 += line_base
                    iva_19 += item_tax_amount
                elif self._is_approx_equal(tax_rate, Decimal("0.05")):
                    base_iva_5 += line_base
                    iva_5 += item_tax_amount
                else:
                    base_no_iva += item.line_total

        total_iva = iva_19 + iva_5

        return {
            "base_iva_19": base_iva_19,
            "iva_19": iva_19,
            "base_iva_5": base_iva_5,
            "iva_5": iva_5,
            "base_no_iva": base_no_iva,
            "total_iva": total_iva,
        }

    def get_libro_ventas(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Libro de Ventas según normativa colombiana (Art. 1.6.1.4.10 ET).
        Registra todas las facturas de venta con desglose de IVA, retenciones.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        date_filter = [Invoice.invoice_type == "SALE", Invoice.company_id == company_id]
        if date_from:
            date_filter.append(Invoice.issue_date >= date_from)
        if date_to:
            date_filter.append(Invoice.issue_date <= date_to)

        invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*date_filter))
            .all()
        )
        invoices = list({inv.id: inv for inv in invoices}.values())

        entries = []
        total_base_iva_19 = Decimal("0.00")
        total_iva_19 = Decimal("0.00")
        total_base_iva_5 = Decimal("0.00")
        total_iva_5 = Decimal("0.00")
        total_base_no_iva = Decimal("0.00")
        total_iva = Decimal("0.00")
        total_retencion_iva = Decimal("0.00")
        total_retencion_fuente = Decimal("0.00")
        total_facturas = Decimal("0.00")

        for inv in invoices:
            taxes = self._get_invoice_tax_breakdown(inv)

            retencion_fuente = Decimal("0.00")
            retencion_iva = Decimal("0.00")

            if inv.partner and inv.partner.responsibility_fiscal == "AGENTE RETENEDOR":
                if taxes["iva_19"] > 0 or taxes["iva_5"] > 0:
                    retencion_fuente = (
                        taxes["base_iva_19"] + taxes["base_iva_5"]
                    ) * Decimal("0.025")
                    retencion_iva = taxes["total_iva"] * Decimal("0.15")

            total_invoice = (
                taxes["base_iva_19"]
                + taxes["base_iva_5"]
                + taxes["base_no_iva"]
                + taxes["total_iva"]
                - retencion_fuente
                - retencion_iva
            )

            partner_name = inv.partner.name if inv.partner else "N/A"
            partner_nit = inv.partner.nit if inv.partner else None
            partner_resp = inv.partner.responsibility_fiscal if inv.partner else None

            entries.append(
                {
                    "invoice_id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "invoice_date": inv.issue_date,
                    "partner_nit": partner_nit,
                    "partner_name": partner_name,
                    "partner_responsibility": partner_resp,
                    "base_iva_19": taxes["base_iva_19"],
                    "iva_19": taxes["iva_19"],
                    "base_iva_5": taxes["base_iva_5"],
                    "iva_5": taxes["iva_5"],
                    "base_no_iva": taxes["base_no_iva"],
                    "total_iva": taxes["total_iva"],
                    "base_retencion": taxes["base_iva_19"] + taxes["base_iva_5"],
                    "retencion_iva": retencion_iva,
                    "retencion_fuente": retencion_fuente,
                    "total_invoice": total_invoice,
                    "estado_dian": inv.estado_dian,
                }
            )

            total_base_iva_19 += taxes["base_iva_19"]
            total_iva_19 += taxes["iva_19"]
            total_base_iva_5 += taxes["base_iva_5"]
            total_iva_5 += taxes["iva_5"]
            total_base_no_iva += taxes["base_no_iva"]
            total_iva += taxes["total_iva"]
            total_retencion_iva += retencion_iva
            total_retencion_fuente += retencion_fuente
            total_facturas += total_invoice

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "entries": entries,
            "totals": {
                "total_base_iva_19": total_base_iva_19,
                "total_iva_19": total_iva_19,
                "total_base_iva_5": total_base_iva_5,
                "total_iva_5": total_iva_5,
                "total_base_no_iva": total_base_no_iva,
                "total_iva": total_iva,
                "total_retencion_iva": total_retencion_iva,
                "total_retencion_fuente": total_retencion_fuente,
                "total_facturas": total_facturas,
                "num_facturas": len(entries),
            },
        }

    def get_libro_compras(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Libro de Compras según normativa colombiana (Art. 1.6.1.4.10 ET).
        Registra todas las facturas de compra con desglose de IVA soportado, retenciones.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        date_filter = [
            Invoice.invoice_type == "PURCHASE",
            Invoice.company_id == company_id,
        ]
        if date_from:
            date_filter.append(sql_func.date(Invoice.issue_date) >= date_from.date())
        if date_to:
            date_filter.append(sql_func.date(Invoice.issue_date) <= date_to.date())

        invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*date_filter))
            .all()
        )
        invoices = list({inv.id: inv for inv in invoices}.values())

        p_date_filter = [
            Purchase.company_id == company_id,
        ]
        if date_from:
            p_date_filter.append(sql_func.date(Purchase.purchase_date) >= date_from.date())
        if date_to:
            p_date_filter.append(sql_func.date(Purchase.purchase_date) <= date_to.date())

        dedicated_purchases = (
            self.db.query(Purchase)
            .options(joinedload(Purchase.partner), joinedload(Purchase.items))
            .filter(and_(*p_date_filter))
            .all()
        )
        dedicated_purchases = list({pur.id: pur for pur in dedicated_purchases}.values())

        je_date_filter = [
            JournalEntry.company_id == company_id,
            JournalEntry.reference.like("SI-%"),
            JournalEntry.is_posted == True
        ]
        if date_from:
            je_date_filter.append(sql_func.date(JournalEntry.entry_date) >= date_from.date())
        if date_to:
            je_date_filter.append(sql_func.date(JournalEntry.entry_date) <= date_to.date())
            
        initial_stock_jes = (
            self.db.query(JournalEntry)
            .options(joinedload(JournalEntry.lines))
            .filter(and_(*je_date_filter))
            .all()
        )
        initial_stock_jes = list({je.id: je for je in initial_stock_jes}.values())

        all_purchases = invoices + dedicated_purchases
        entries = []
        total_base_iva_19 = Decimal("0.00")
        total_iva_19 = Decimal("0.00")
        total_base_iva_5 = Decimal("0.00")
        total_iva_5 = Decimal("0.00")
        total_base_no_iva = Decimal("0.00")
        total_iva = Decimal("0.00")
        total_retencion_iva = Decimal("0.00")
        total_retencion_fuente = Decimal("0.00")
        total_facturas = Decimal("0.00")

        for inv in all_purchases:
            taxes = self._get_invoice_tax_breakdown(inv)

            retencion_fuente = Decimal("0.00")
            retencion_iva = Decimal("0.00")

            if company.regimen in ("COMUN", "ESPECIAL"):
                if taxes["iva_19"] > 0 or taxes["iva_5"] > 0:
                    retencion_fuente = (
                        taxes["base_iva_19"] + taxes["base_iva_5"]
                    ) * Decimal("0.025")
                    retencion_iva = taxes["total_iva"] * Decimal("0.15")

            total_invoice = (
                taxes["base_iva_19"]
                + taxes["base_iva_5"]
                + taxes["base_no_iva"]
                + taxes["total_iva"]
                - retencion_fuente
                - retencion_iva
            )

            partner_name = inv.partner.name if inv.partner else "N/A"
            partner_nit = inv.partner.nit if inv.partner else None
            partner_resp = inv.partner.responsibility_fiscal if inv.partner else None

            inv_number = getattr(inv, "invoice_number", getattr(inv, "purchase_number", "N/A"))
            inv_date = getattr(inv, "issue_date", getattr(inv, "purchase_date", None))
            estado_dian = getattr(inv, "estado_dian", "NO_APLICA")
            
            source_prefix = "INV" if hasattr(inv, "invoice_number") else "PUR"
            unique_id = f"{source_prefix}-{inv.id}"

            entries.append(
                {
                    "invoice_id": unique_id,
                    "invoice_number": inv_number,
                    "invoice_date": inv_date,
                    "partner_nit": partner_nit,
                    "partner_name": partner_name,
                    "partner_responsibility": partner_resp,
                    "base_iva_19": taxes["base_iva_19"],
                    "iva_19": taxes["iva_19"],
                    "base_iva_5": taxes["base_iva_5"],
                    "iva_5": taxes["iva_5"],
                    "base_no_iva": taxes["base_no_iva"],
                    "total_iva": taxes["total_iva"],
                    "base_retencion": taxes["base_iva_19"] + taxes["base_iva_5"],
                    "retencion_iva": retencion_iva,
                    "retencion_fuente": retencion_fuente,
                    "total_invoice": total_invoice,
                    "estado_dian": estado_dian,
                }
            )

            total_base_iva_19 += taxes["base_iva_19"]
            total_iva_19 += taxes["iva_19"]
            total_base_iva_5 += taxes["base_iva_5"]
            total_iva_5 += taxes["iva_5"]
            total_base_no_iva += taxes["base_no_iva"]
            total_iva += taxes["total_iva"]
            total_retencion_iva += retencion_iva
            total_retencion_fuente += retencion_fuente
            total_facturas += total_invoice

        for je in initial_stock_jes:
            total_amount = Decimal("0.00")
            for line in je.lines:
                if line.debit_amount > 0:
                    total_amount += line.debit_amount
            
            # Initial stock entries are usually purchases without IVA broken down (unless we expand it later)
            entries.append(
                {
                    "invoice_id": f"je_{je.id}",
                    "invoice_number": je.reference,
                    "invoice_date": je.entry_date,
                    "partner_nit": "N/A",
                    "partner_name": "Sin Proveedor (Stock Inicial)",
                    "partner_responsibility": "NO RESPONSABLE",
                    "base_iva_19": Decimal("0.00"),
                    "iva_19": Decimal("0.00"),
                    "base_iva_5": Decimal("0.00"),
                    "iva_5": Decimal("0.00"),
                    "base_no_iva": total_amount,
                    "total_iva": Decimal("0.00"),
                    "base_retencion": Decimal("0.00"),
                    "retencion_iva": Decimal("0.00"),
                    "retencion_fuente": Decimal("0.00"),
                    "total_invoice": total_amount,
                    "estado_dian": "NO_APLICA",
                }
            )
            total_base_no_iva += total_amount
            total_facturas += total_amount

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "entries": entries,
            "totals": {
                "total_base_iva_19": total_base_iva_19,
                "total_iva_19": total_iva_19,
                "total_base_iva_5": total_base_iva_5,
                "total_iva_5": total_iva_5,
                "total_base_no_iva": total_base_no_iva,
                "total_iva": total_iva,
                "total_retencion_iva": total_retencion_iva,
                "total_retencion_fuente": total_retencion_fuente,
                "total_facturas": total_facturas,
                "num_facturas": len(entries),
            },
        }

    def get_declaracion_iva(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera la Declaración de IVA según formulario 300 DIAN.
        Calcula IVA generado (ventas) menos IVA soportado (compras).
        Art. 437, 468, 486 ET.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        if company.regimen in ("SIMPLE", "NO_RESPONSABLE"):
            return {
                "company_id": company_id,
                "company_name": company.name,
                "company_nit": company.nit,
                "company_dv": company.dv,
                "regimen": company.regimen,
                "period": self._format_period(date_from, date_to),
                "date_from": date_from,
                "date_to": date_to,
                "iva_generado": [],
                "total_iva_generado": Decimal("0.00"),
                "iva_soportado": [],
                "total_iva_soportado": Decimal("0.00"),
                "iva_a_pagar": Decimal("0.00"),
                "iva_a_favor": Decimal("0.00"),
                "es_a_pagar": False,
                "note": "Régimen Simple / No Responsable: No declara IVA por separado",
            }

        sales_book = self.get_libro_ventas(company_id, date_from, date_to)
        purchases_book = self.get_libro_compras(company_id, date_from, date_to)

        iva_generado = [
            {
                "concept": "IVA 19% generado (ventas)",
                "base": sales_book["totals"].get("total_base_iva_19", Decimal("0.00")),
                "tax_amount": sales_book["totals"].get("total_iva_19", Decimal("0.00")),
            },
            {
                "concept": "IVA 5% generado (ventas)",
                "base": sales_book["totals"].get("total_base_iva_5", Decimal("0.00")),
                "tax_amount": sales_book["totals"].get("total_iva_5", Decimal("0.00")),
            },
        ]
        total_iva_generado = sales_book["totals"].get("total_iva", Decimal("0.00"))

        iva_soportado = [
            {
                "concept": "IVA 19% soportado (compras)",
                "base": purchases_book["totals"].get(
                    "total_base_iva_19", Decimal("0.00")
                ),
                "tax_amount": purchases_book["totals"].get(
                    "total_iva_19", Decimal("0.00")
                ),
            },
            {
                "concept": "IVA 5% soportado (compras)",
                "base": purchases_book["totals"].get(
                    "total_base_iva_5", Decimal("0.00")
                ),
                "tax_amount": purchases_book["totals"].get(
                    "total_iva_5", Decimal("0.00")
                ),
            },
        ]
        total_iva_soportado = purchases_book["totals"].get("total_iva", Decimal("0.00"))

        diferencia = total_iva_generado - total_iva_soportado
        iva_a_pagar = diferencia if diferencia > 0 else Decimal("0.00")
        iva_a_favor = abs(diferencia) if diferencia < 0 else Decimal("0.00")

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "company_dv": company.dv,
            "regimen": company.regimen,
            "period": self._format_period(date_from, date_to),
            "date_from": date_from,
            "date_to": date_to,
            "iva_generado": iva_generado,
            "total_iva_generado": total_iva_generado,
            "iva_soportado": iva_soportado,
            "total_iva_soportado": total_iva_soportado,
            "iva_a_pagar": iva_a_pagar,
            "iva_a_favor": iva_a_favor,
            "es_a_pagar": diferencia > 0,
        }

    def get_reporte_retenciones(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Reporte de Retenciones en la fuente y en el IVA.
        Incluye Retefuente (2.5% servicios, 10% bienes) y ReteIVA (15%).
        Art. 368, 401 ET.
        Valida umbral de 27 UVT diarias para Retefuente (Art. 368 ET).
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        from app.core.config import settings

        uvt_daily_threshold = Decimal(str(settings.UVT_VALUE * 27))

        date_filter_sales = [
            Invoice.invoice_type == "SALE",
            Invoice.company_id == company_id,
        ]
        date_filter_purchases = [
            Invoice.invoice_type == "PURCHASE",
            Invoice.company_id == company_id,
        ]
        if date_from:
            date_filter_sales.append(Invoice.issue_date >= date_from)
            date_filter_purchases.append(Invoice.issue_date >= date_from)
        if date_to:
            date_filter_sales.append(Invoice.issue_date <= date_to)
            date_filter_purchases.append(Invoice.issue_date <= date_to)

        sales_invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*date_filter_sales))
            .order_by(Invoice.issue_date)
            .all()
        )
        sales_invoices = list({inv.id: inv for inv in sales_invoices}.values())

        purchase_invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*date_filter_purchases))
            .order_by(Invoice.issue_date)
            .all()
        )
        purchase_invoices = list({inv.id: inv for inv in purchase_invoices}.values())

        entries = []
        total_retefuente = Decimal("0.00")
        total_reteiva = Decimal("0.00")
        total_retefuente_bienes = Decimal("0.00")
        total_retefuente_servicios = Decimal("0.00")

        for inv in sales_invoices + purchase_invoices:
            taxes = self._get_invoice_tax_breakdown(inv)
            base_gravable = taxes["base_iva_19"] + taxes["base_iva_5"]

            if base_gravable <= 0 and taxes["total_iva"] <= 0:
                continue

            is_purchase = inv.invoice_type == "PURCHASE"
            partner_name = inv.partner.name if inv.partner else "N/A"
            partner_nit = inv.partner.nit if inv.partner else None

            if is_purchase and company.regimen in ("COMUN", "ESPECIAL"):
                exceeds_uvt = base_gravable > uvt_daily_threshold

                if base_gravable > 0 and exceeds_uvt:
                    retefuente_bienes = base_gravable * Decimal("0.10")
                    total_retefuente_bienes += retefuente_bienes
                    entries.append(
                        {
                            "invoice_id": inv.id,
                            "invoice_number": inv.invoice_number,
                            "invoice_date": inv.issue_date,
                            "partner_nit": partner_nit,
                            "partner_name": partner_name,
                            "concept": "Retefuente bienes 10%",
                            "base_retencion": base_gravable,
                            "tarifa": Decimal("0.10"),
                            "valor_retencion": retefuente_bienes,
                            "invoice_type": "COMPRA",
                        }
                    )
                    total_retefuente += retefuente_bienes

                if base_gravable > 0 and not exceeds_uvt:
                    retefuente = base_gravable * Decimal("0.025")
                    total_retefuente_servicios += retefuente
                    entries.append(
                        {
                            "invoice_id": inv.id,
                            "invoice_number": inv.invoice_number,
                            "invoice_date": inv.issue_date,
                            "partner_nit": partner_nit,
                            "partner_name": partner_name,
                            "concept": "Retefuente servicios 2.5%",
                            "base_retencion": base_gravable,
                            "tarifa": Decimal("0.025"),
                            "valor_retencion": retefuente,
                            "invoice_type": "COMPRA",
                        }
                    )
                    total_retefuente += retefuente

                if taxes["total_iva"] > 0:
                    reteiva = taxes["total_iva"] * Decimal("0.15")
                    entries.append(
                        {
                            "invoice_id": inv.id,
                            "invoice_number": inv.invoice_number,
                            "invoice_date": inv.issue_date,
                            "partner_nit": partner_nit,
                            "partner_name": partner_name,
                            "concept": "Retención en el IVA 15%",
                            "base_retencion": taxes["total_iva"],
                            "tarifa": Decimal("0.15"),
                            "valor_retencion": reteiva,
                            "invoice_type": "COMPRA",
                        }
                    )
                    total_reteiva += reteiva

            elif (
                not is_purchase
                and inv.partner
                and inv.partner.responsibility_fiscal == "AGENTE RETENEDOR"
            ):
                if base_gravable > 0:
                    retefuente = base_gravable * Decimal("0.025")
                    entries.append(
                        {
                            "invoice_id": inv.id,
                            "invoice_number": inv.invoice_number,
                            "invoice_date": inv.issue_date,
                            "partner_nit": partner_nit,
                            "partner_name": partner_name,
                            "concept": "Retención en la fuente aplicada por agente retenedor 2.5%",
                            "base_retencion": base_gravable,
                            "tarifa": Decimal("0.025"),
                            "valor_retencion": retefuente,
                            "invoice_type": "VENTA",
                        }
                    )
                    total_retefuente += retefuente

                if taxes["total_iva"] > 0:
                    reteiva = taxes["total_iva"] * Decimal("0.15")
                    entries.append(
                        {
                            "invoice_id": inv.id,
                            "invoice_number": inv.invoice_number,
                            "invoice_date": inv.issue_date,
                            "partner_nit": partner_nit,
                            "partner_name": partner_name,
                            "concept": "Retención en el IVA aplicada por agente retenedor 15%",
                            "base_retencion": taxes["total_iva"],
                            "tarifa": Decimal("0.15"),
                            "valor_retencion": reteiva,
                            "invoice_type": "VENTA",
                        }
                    )
                    total_reteiva += reteiva

        entries.sort(key=lambda x: x["invoice_date"])

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "uvt_value": settings.UVT_VALUE,
            "uvt_daily_threshold_27": float(uvt_daily_threshold),
            "entries": entries,
            "totals": {
                "total_retefuente": total_retefuente,
                "total_retefuente_bienes": total_retefuente_bienes,
                "total_retefuente_servicios": total_retefuente_servicios,
                "total_reteiva": total_reteiva,
                "total_retenciones": total_retefuente + total_reteiva,
                "num_retenciones": len(entries),
            },
        }

    def get_reporte_egresos(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Reporte de Egresos (Compras y Gastos).
        Incluye compras de inventario y gastos operacionales.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        # 1. Obtener compras desde el modelo Invoice (PURCHASE)
        inv_filter = [Invoice.invoice_type == "PURCHASE", Invoice.company_id == company_id]
        if date_from:
            inv_filter.append(Invoice.issue_date >= date_from)
        if date_to:
            inv_filter.append(Invoice.issue_date <= date_to)

        invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*inv_filter))
            .all()
        )
        invoices = list({inv.id: inv for inv in invoices}.values())

        # 2. Obtener compras desde el modelo Purchase
        pur_filter = [Purchase.company_id == company_id]
        if date_from:
            pur_filter.append(Purchase.purchase_date >= date_from)
        if date_to:
            pur_filter.append(Purchase.purchase_date <= date_to)

        purchases = (
            self.db.query(Purchase)
            .options(joinedload(Purchase.partner), joinedload(Purchase.items))
            .filter(and_(*pur_filter))
            .all()
        )
        purchases = list({pur.id: pur for pur in purchases}.values())

        entries = []
        total_compras = Decimal("0.00")
        total_iva_descontable = Decimal("0.00")
        total_retenciones = Decimal("0.00")

        # Procesar Facturas de Compra
        for inv in invoices:
            taxes = self._get_invoice_tax_breakdown(inv)
            base = taxes["base_iva_19"] + taxes["base_iva_5"] + taxes["base_no_iva"]
            partner_name = inv.partner.name if inv.partner else "N/A"
            
            entries.append({
                "source": "Factura de Compra",
                "id": inv.id,
                "number": inv.invoice_number,
                "date": inv.issue_date,
                "partner_name": partner_name,
                "base": base,
                "tax_amount": taxes["total_iva"],
                "total": inv.total_amount
            })
            total_compras += base
            total_iva_descontable += taxes["total_iva"]

        # Procesar Compras Directas
        for pur in purchases:
            taxes = self._get_invoice_tax_breakdown(pur)
            base = taxes["base_iva_19"] + taxes["base_iva_5"] + taxes["base_no_iva"]
            partner_name = pur.partner.name if pur.partner else "N/A"

            entries.append({
                "source": "Orden de Compra / Gasto",
                "id": pur.id,
                "number": pur.purchase_number,
                "date": pur.purchase_date,
                "partner_name": partner_name,
                "base": base,
                "tax_amount": taxes["total_iva"],
                "total": pur.total_amount
            })
            total_compras += base
            total_iva_descontable += taxes["total_iva"]

        # 3. Obtener egresos desde Asientos Contables manuales (JournalEntries)
        # Buscamos asientos publicados que afecten cuentas de gastos (que empiecen por 5)
        je_filter = [JournalEntry.is_posted == True, JournalEntry.company_id == company_id]
        if date_from:
            je_filter.append(JournalEntry.entry_date >= date_from)
        if date_to:
            je_filter.append(JournalEntry.entry_date <= date_to)

        journal_entries = (
            self.db.query(JournalEntry)
            .options(joinedload(JournalEntry.lines).joinedload(JournalEntryLine.account))
            .filter(and_(*je_filter))
            .all()
        )
        journal_entries = list({je.id: je for je in journal_entries}.values())

        # Procesar Asientos Contables (solo las líneas de gasto)
        for je in journal_entries:
            # Si el asiento viene de una factura o compra, lo ignoramos para no duplicar
            if je.reference and (je.reference.startswith('INV-') or je.reference.startswith('PUR-')):
                continue
                
            for line in je.lines:
                # Obtenemos la cuenta de forma segura
                acc = line.account
                if not acc:
                    # Intento de recuperación manual si el join falló
                    acc = self.db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
                
                if acc and acc.code.startswith('5') and line.debit_amount > 0:
                    entries.append({
                        "source": "Asiento Contable",
                        "id": je.id,
                        "number": f"AS-{je.id}",
                        "date": je.entry_date,
                        "partner_name": je.description or "Gasto General",
                        "base": line.debit_amount,
                        "tax_amount": Decimal("0.00"),
                        "total": line.debit_amount
                    })
                    total_compras += line.debit_amount

        # Ordenar por fecha
        entries.sort(key=lambda x: x["date"])

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "entries": entries,
            "totals": {
                "total_compras_netas": total_compras,
                "total_iva_descontable": total_iva_descontable,
                "total_egresos": total_compras + total_iva_descontable,
                "num_registros": len(entries),
            },
        }

    def get_reporte_ingresos(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Reporte de Ingresos para declaración de renta.
        Clasifica ingresos operacionales y no operacionales.
        Art. 287, 631 ET.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        date_filter = [Invoice.invoice_type == "SALE", Invoice.company_id == company_id]
        if date_from:
            date_filter.append(Invoice.issue_date >= date_from)
        if date_to:
            date_filter.append(Invoice.issue_date <= date_to)

        invoices = (
            self.db.query(Invoice)
            .options(joinedload(Invoice.partner), joinedload(Invoice.items))
            .filter(and_(*date_filter))
            .order_by(Invoice.issue_date)
            .all()
        )
        invoices = list({inv.id: inv for inv in invoices}.values())

        entries = []
        total_operacional = Decimal("0.00")
        total_no_operacional = Decimal("0.00")
        total_iva_generado = Decimal("0.00")
        total_devoluciones = Decimal("0.00")

        for inv in invoices:
            if inv.status == "CANCELLED":
                total_devoluciones += inv.total_amount
                continue

            taxes = self._get_invoice_tax_breakdown(inv)
            base = taxes["base_iva_19"] + taxes["base_iva_5"] + taxes["base_no_iva"]
            partner_name = inv.partner.name if inv.partner else "N/A"

            entries.append(
                {
                    "source": "Ingresos operacionales - Servicios",
                    "invoice_id": inv.id,
                    "invoice_number": inv.invoice_number,
                    "date": inv.issue_date,
                    "partner_name": partner_name,
                    "base": base,
                    "tax_amount": taxes["total_iva"],
                    "total": inv.total_amount,
                }
            )
            total_operacional += base
            total_iva_generado += taxes["total_iva"]

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "entries": entries,
            "totals": {
                "total_ingresos_operacionales": total_operacional,
                "total_ingresos_no_operacionales": total_no_operacional,
                "total_iva_generado": total_iva_generado,
                "total_devoluciones": total_devoluciones,
                "ingresos_netos": total_operacional - total_devoluciones,
                "num_facturas": len(entries),
            },
        }

    def get_reporte_patrimonio(
        self,
        company_id: int,
        cut_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Genera el Reporte de Patrimonio (Activos - Pasivos = Patrimonio).
        Basado en los saldos del Libro Mayor al corte, incluyendo la utilidad del ejercicio.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return {"error": "Company not found"}

        date_to = cut_date or datetime.now(timezone.utc)

        mayor_data = self.get_libro_mayor(company_id, date_to=date_to)

        activos = []
        total_activos = Decimal("0.00")
        pasivos = []
        total_pasivos = Decimal("0.00")
        patrimonio_cuentas = []
        total_patrimonio_cuentas = Decimal("0.00")
        
        total_ingresos = Decimal("0.00")
        total_gastos = Decimal("0.00")

        for acc in mayor_data.get("accounts", []):
            balance = acc["final_balance"]
            if balance == Decimal("0.00"):
                continue

            acc_info = {
                "account_code": acc["account_code"],
                "account_name": acc["account_name"],
                "balance": balance,
            }

            if acc["account_type"] == "ASSET":
                activos.append(acc_info)
                total_activos += balance
            elif acc["account_type"] == "LIABILITY":
                pasivos.append(acc_info)
                total_pasivos += balance
            elif acc["account_type"] == "EQUITY":
                patrimonio_cuentas.append(acc_info)
                total_patrimonio_cuentas += balance
            elif acc["account_type"] == "REVENUE":
                total_ingresos += balance
            elif acc["account_type"] == "EXPENSE":
                total_gastos += balance

        # La Utilidad del Ejercicio es Ingresos - Gastos.
        # get_libro_mayor ya devuelve balances positivos para sus naturalezas (Cr para ingresos, Dr para gastos)
        utilidad_ejercicio = total_ingresos - total_gastos
        total_patrimonio = total_patrimonio_cuentas + utilidad_ejercicio

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "cut_date": date_to,
            "activos": activos,
            "total_activos": total_activos,
            "pasivos": pasivos,
            "total_pasivos": total_pasivos,
            "patrimonio_desglose": {
                "cuentas_patrimonio": patrimonio_cuentas,
                "total_cuentas_patrimonio": total_patrimonio_cuentas,
                "utilidad_ejercicio": utilidad_ejercicio,
                "ingresos_totales": total_ingresos,
                "gastos_totales": total_gastos
            },
            "total_patrimonio": total_patrimonio,
            "patrimonio_calculado_a_p": total_activos - total_pasivos
        }

    def _format_period(
        self, date_from: Optional[datetime], date_to: Optional[datetime]
    ) -> str:
        """Format period for DIAN declaration"""
        if date_from and date_to:
            return f"{date_from.strftime('%Y-%m')} a {date_to.strftime('%Y-%m')}"
        elif date_to:
            return date_to.strftime("%Y-%m")
        return "Bimestre actual"

    def create_default_chart_of_accounts(
        self, company_id: int
    ) -> List[ChartOfAccounts]:
        """
        Create a default chart of accounts for a new company based on Colombian accounting standards.
        Includes basic accounts for assets, liabilities, equity, revenue, and expenses.
        """
        default_accounts = [
            # Assets
            {
                "code": "1000",
                "name": "ACTIVO",
                "description": "Total de activos",
                "account_type": "ASSET",
            },
            {
                "code": "1100",
                "name": "ACTIVO CORRIENTE",
                "description": "Activos convertibles en efectivo dentro de un año",
                "account_type": "ASSET",
                "parent_id": None,
            },  # Will set after creation
            {
                "code": "1110",
                "name": "Efectivo y equivalentes",
                "description": "Dinero en efectivo y equivalents",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "111001",
                "name": "Caja principal",
                "description": "Dinero en caja principal",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111002",
                "name": "Caja menor",
                "description": "Fondo para gastos menores",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111003",
                "name": "Caja registro #1",
                "description": "Caja de punto de venta 1",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111004",
                "name": "Caja registro #2",
                "description": "Caja de punto de venta 2",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111010",
                "name": "Bancos - Cuenta corriente",
                "description": "Cuentas corrientes bancarias",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111011",
                "name": "Bancos - Cuenta de ahorros",
                "description": "Cuentas de ahorro bancarias",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111012",
                "name": "Bancos - Cta. moneda extranjera",
                "description": "Cuentas bancarias en moneda extranjera",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111020",
                "name": "Cuentas por cobrar a terceros",
                "description": "Derechos de cobro a terceros",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111030",
                "name": "Cheques en transito",
                "description": "Cheques emitidos no cobrados",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "111040",
                "name": "Depositos a termino",
                "description": "CDTs y depositos a plazo fijo",
                "account_type": "ASSET",
                "parent_id": 1110,
            },
            {
                "code": "1120",
                "name": "Inversiones temporales",
                "description": "Inversiones a corto plazo",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1130",
                "name": "Cuentas por cobrar",
                "description": "Derechos de cobro a clientes",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1140",
                "name": "Inventarios",
                "description": "Mercancías para venta",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1150",
                "name": "Gastos anticipados",
                "description": "Gastos pagados por anticipado",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1200",
                "name": "ACTIVO NO CORRIENTE",
                "description": "Activos a largo plazo",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1210",
                "name": "Propiedad, planta y equipo",
                "description": "Activos fijos",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1220",
                "name": "Inversiones permanentes",
                "description": "Inversiones a largo plazo",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1230",
                "name": "Intangibles",
                "description": "Activos intangibles",
                "account_type": "ASSET",
                "parent_id": None,
            },
            {
                "code": "1240",
                "name": "Activos diferidos",
                "description": "Gastos diferidos a largo plazo",
                "account_type": "ASSET",
                "parent_id": None,
            },
            # Liabilities
            {
                "code": "2000",
                "name": "PASIVO",
                "description": "Total de pasivos",
                "account_type": "LIABILITY",
            },
            {
                "code": "2100",
                "name": "PASIVO CORRIENTE",
                "description": "Obligaciones a corto plazo",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2110",
                "name": "Cuentas por pagar",
                "description": "Obligaciones generales",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2205",
                "name": "Proveedores",
                "description": "Cuentas por pagar a proveedores",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2120",
                "name": "Documentos por pagar",
                "description": "Letras y pagarés",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2130",
                "name": "Obligaciones fiscales",
                "description": "Impuestos por pagar",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2140",
                "name": "Préstamos a corto plazo",
                "description": "Creditos vencibles en año",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2150",
                "name": "Ingresos recibidos por anticipado",
                "description": "Anticipos de clientes",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2200",
                "name": "PASIVO NO CORRIENTE",
                "description": "Obligaciones a largo plazo",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
            {
                "code": "2210",
                "name": "Préstamos a largo plazo",
                "description": "Creditos vencibles después de un año",
                "account_type": "LIABILITY",
                "parent_id": None,
            },
        {
            "code": "2220",
            "name": "Bonos y obligaciones",
            "description": "Títulos de deuda",
            "account_type": "LIABILITY",
            "parent_id": None,
        },
        {
            "code": "2408",
            "name": "IVA descontable (soportado)",
            "description": "Impuesto sobre las ventas descontable en compras",
            "account_type": "LIABILITY",
            "parent_id": None,
        },
        # Equity
            {
                "code": "3000",
                "name": "PATRIMONIO",
                "description": "Patrimonio de los propietarios",
                "account_type": "EQUITY",
            },
            {
                "code": "3100",
                "name": "Capital social",
                "description": "Aportes de los socios",
                "account_type": "EQUITY",
                "parent_id": None,
            },
            {
                "code": "3200",
                "name": "Reservas",
                "description": "Utilidades retenidas",
                "account_type": "EQUITY",
                "parent_id": None,
            },
            {
                "code": "3300",
                "name": "Utilidades del ejercicio",
                "description": "Ganancia o pérdida del periodo",
                "account_type": "EQUITY",
                "parent_id": None,
            },
            # Revenue
            {
                "code": "4000",
                "name": "INGRESOS",
                "description": "Total de ingresos",
                "account_type": "REVENUE",
            },
            {
                "code": "4100",
                "name": "Ingresos por ventas",
                "description": "Ventas de productos y servicios",
                "account_type": "REVENUE",
                "parent_id": None,
            },
            {
                "code": "4200",
                "name": "Ingresos financieros",
                "description": "Intereses y ganancias cambiarias",
                "account_type": "REVENUE",
                "parent_id": None,
            },
            {
                "code": "4300",
                "name": "Otros ingresos",
                "description": "Ingresos diversos",
                "account_type": "REVENUE",
                "parent_id": None,
            },
            # Expenses
            {
                "code": "5000",
                "name": "GASTOS",
                "description": "Total de gastos",
                "account_type": "EXPENSE",
            },
        {
            "code": "5100",
            "name": "Costo de ventas",
            "description": "Costo directo de productos vendidos",
            "account_type": "COST",
            "parent_id": None,
        },
            {
                "code": "5200",
                "name": "Gastos de administración",
                "description": "Gastos gerenciales",
                "account_type": "EXPENSE",
                "parent_id": None,
            },
            {
                "code": "5300",
                "name": "Gastos de ventas",
                "description": "Gastos comerciales",
                "account_type": "EXPENSE",
                "parent_id": None,
            },
            {
                "code": "5400",
                "name": "Gastos financieros",
                "description": "Intereses y comisiones",
                "account_type": "EXPENSE",
                "parent_id": None,
            },
            {
                "code": "5500",
                "name": "Gastos por diferencial de cambio",
                "description": "Pérdidas cambiarias",
                "account_type": "EXPENSE",
                "parent_id": None,
            },
        {
            "code": "5600",
            "name": "Otros gastos",
            "description": "Gastos diversos",
            "account_type": "EXPENSE",
            "parent_id": None,
        },
        {
            "code": "6135",
            "name": "Costo de ventas",
            "description": "Costo directo de mercancías vendidas (PUC 6135)",
            "account_type": "COST",
            "parent_id": None,
        },
        ]

        created_accounts = []
        account_map = {}

        existing_accounts = {
            acc.code: acc
            for acc in self.db.query(ChartOfAccounts)
            .filter(ChartOfAccounts.company_id == company_id)
            .all()
        }

        for acc_data in default_accounts:
            parent_id = acc_data.pop("parent_id", None)

            if acc_data["code"] in existing_accounts:
                existing = existing_accounts[acc_data["code"]]
                account_map[acc_data["code"]] = existing.id
                created_accounts.append(existing)
                if parent_id is not None:
                    acc_data["parent_id"] = parent_id
                continue

            coa_create = co_schema.ChartOfAccountsCreate(**acc_data)
            db_coa = ChartOfAccounts(**coa_create.model_dump(), company_id=company_id)
            self.db.add(db_coa)
            self.db.flush()
            account_map[acc_data["code"]] = db_coa.id
            created_accounts.append(db_coa)

            if parent_id is not None:
                acc_data["parent_id"] = parent_id

        # Second pass: set parent relationships
        for acc_data in default_accounts:
            parent_id = acc_data.get("parent_id")
            if parent_id is not None:
                child_code = acc_data["code"]
                for coa in created_accounts:
                    if coa.code == child_code:
                        coa.parent_id = account_map.get(str(parent_id))
                        break

        # Deactivate IVA soportado (2408) for SIMPLE/NO_RESPONSABLE regimes
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if company and company.regimen in ("SIMPLE", "NO_RESPONSABLE"):
            iva_soportado = self._get_account_by_code(company_id, "2408", allow_inactive=True)
            if iva_soportado and iva_soportado.is_active:
                iva_soportado.is_active = False

        self.db.commit()

        for coa in created_accounts:
            self.db.refresh(coa)

        return created_accounts

    def create_opening_entry(
        self,
        company_id: int,
        initial_capital: Decimal = Decimal("0.00"),
        initial_cash: Decimal = Decimal("0.00"),
        initial_bank: Decimal = Decimal("0.00"),
    ) -> Optional[JournalEntry]:
        """
        Create opening journal entry for a new company.
        According to Colombian law (Decreto 2420/2015), the opening entry records:
        - Assets: Cash, Bank accounts, Receivables, Inventory
        - Liabilities: Accounts payable, Loans
        - Equity: Capital stock, Retained earnings

        Args:
            company_id: Company ID
            initial_capital: Initial capital contribution
            initial_cash: Initial cash balance
            initial_bank: Initial bank balance
        """


        effective_account = self._get_account_by_code(company_id, "1110")
        cash_account = self._get_account_by_code(company_id, "111001")
        bank_account = self._get_account_by_code(company_id, "111010")
        capital_account = self._get_account_by_code(company_id, "3100")

        if not capital_account:
            raise ValueError("Capital social account (3100) not found in chart of accounts")

        current_year = datetime.now(timezone.utc).year
        reference = f"APERTURA-{current_year}"
        description = f"Asiento de apertura - Constitución de la empresa - Año {current_year}"

        db_je = JournalEntry(
            entry_date=datetime.now(timezone.utc),
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        total_debits = Decimal("0.00")
        total_credits = Decimal("0.00")

        if initial_cash > 0 and cash_account:
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=cash_account.id,
                    debit_amount=initial_cash,
                    credit_amount=Decimal("0.00"),
                    description=f"Saldo inicial caja",
                )
            )
            total_debits += initial_cash

        if initial_bank > 0 and bank_account:
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=bank_account.id,
                    debit_amount=initial_bank,
                    credit_amount=Decimal("0.00"),
                    description=f"Saldo inicial bancos",
                )
            )
            total_debits += initial_bank

        if initial_capital > 0:
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=capital_account.id,
                    debit_amount=Decimal("0.00"),
                    credit_amount=initial_capital,
                    description=f"Aporte de capital social",
                )
            )
            total_credits += initial_capital

        if total_debits == 0 and total_credits == 0:
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=capital_account.id,
                    debit_amount=Decimal("0.00"),
                    credit_amount=Decimal("0.00"),
                    description=f"Apertura de libros contables",
                )
            )

        # Explicit pre-validation for clear error message
        if total_debits != total_credits:
            self.db.rollback()
            raise ValueError(
                f"Opening entry is unbalanced: debits ({total_debits}) != credits ({total_credits}). "
                f"initial_cash ({initial_cash}) + initial_bank ({initial_bank}) must equal initial_capital ({initial_capital})"
            )

        self.db.flush()
        self._validate_journal_entry_balance(db_je.id)
        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    # Automatic journal entry creation methods
    def _get_account_by_code(
        self, company_id: int, code: str, allow_inactive: bool = False
    ) -> Optional[ChartOfAccounts]:
        query = self.db.query(ChartOfAccounts).filter(
            ChartOfAccounts.company_id == company_id,
            ChartOfAccounts.code == code,
        )
        if not allow_inactive:
            query = query.filter(ChartOfAccounts.is_active == True)
        return query.first()

    def create_journal_entry_from_invoice(
        self,
        invoice_id: int,
        company_id: int,
        total_amount: Decimal,
        subtotal: Decimal,
        tax_amount: Decimal,
        partner_id: int,
        is_warranty: bool = False,
        source_type: str = "REPAIR",
        total_cost: Decimal = Decimal("0.00"),
        is_paid: bool = False,
        payment_method: Optional[str] = None,
        wallet_amount_applied: Decimal = Decimal("0.00"),
        commit: bool = True,
    ) -> Optional[JournalEntry]:
        """
        Create automatic journal entry from an invoice.

        For COMUN/ESPECIAL regimes:
          Debit: Cuentas por cobrar (1130) - Total
          Credit: Ingresos por ventas (4100) - Subtotal
          Credit: Obligaciones fiscales / IVA (2130) - Tax

        For SIMPLE regime:
          Debit: Cuentas por cobrar (1130) - Total
          Credit: Ingresos por ventas (4100) - Total (no tax discrimination)

        For warranty repairs:
          Debit: Costo de ventas (5100) - Parts cost
          Credit: Inventarios (1140) - Parts cost
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return None

        is_simple_regime = company.regimen in ("SIMPLE", "NO_RESPONSABLE")

        if is_warranty:
            return self._create_warranty_journal_entry(
                invoice_id, company_id, total_amount, subtotal
            )

        # Determine accounts
        accounts_receivable = self._get_account_by_code(company_id, "1130")
        sales_revenue = self._get_account_by_code(company_id, "4100")
        tax_liability = self._get_account_by_code(company_id, "2130")

        if not accounts_receivable or not sales_revenue:
            raise ValueError("Required chart of accounts not found")

        # Create journal entry
        entry_date = datetime.now(timezone.utc)
        description = f"Factura por {source_type} - Orden #{invoice_id}"
        reference = f"INV-{invoice_id:06d}"

        db_je = JournalEntry(
            entry_date=entry_date,
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        # Debit: Accounts Receivable
        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=accounts_receivable.id,
                debit_amount=total_amount,
                credit_amount=Decimal("0.00"),
                description=f"Cuentas por cobrar - Factura {reference}",
            )
        )

        if is_simple_regime:
            # Simple regime: no tax discrimination
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=sales_revenue.id,
                    debit_amount=Decimal("0.00"),
                    credit_amount=total_amount,
                    description=f"Ingresos por servicios - Régimen Simple",
                )
            )
        else:
            # Common regime: separate revenue and tax
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=sales_revenue.id,
                    debit_amount=Decimal("0.00"),
                    credit_amount=subtotal,
                    description=f"Ingresos por servicios - Factura {reference}",
                )
            )

            if tax_amount > 0 and tax_liability:
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=db_je.id,
                        account_id=tax_liability.id,
                        debit_amount=Decimal("0.00"),
                        credit_amount=tax_amount,
                        description=f"IVA generado - Factura {reference}",
                    )
                )

        # If invoice is paid or wallet applied, create lines moving amount from Accounts Receivable to Cash/Bank/Wallet
        if is_paid or wallet_amount_applied > Decimal("0.00"):
            cash_account = self._get_account_by_code(company_id, "111001")
            bank_account = self._get_account_by_code(company_id, "111010")
            wallet_account = self._get_account_by_code(company_id, "2150") # Anticipos de clientes
            
            remaining_recaudo = total_amount

            # 1. Aplicar monedero si existe
            if wallet_amount_applied > Decimal("0.00") and wallet_account:
                amount_to_apply = min(wallet_amount_applied, remaining_recaudo)
                # Credit Accounts Receivable
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=db_je.id,
                        account_id=accounts_receivable.id,
                        debit_amount=Decimal("0.00"),
                        credit_amount=amount_to_apply,
                        description=f"Recaudo con monedero - Factura {reference}",
                    )
                )
                # Debit Wallet Liability
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=db_je.id,
                        account_id=wallet_account.id,
                        debit_amount=amount_to_apply,
                        credit_amount=Decimal("0.00"),
                        description=f"Aplicación de anticipo - Monedero",
                    )
                )
                remaining_recaudo -= amount_to_apply

            # 2. Aplicar el resto según payment_method
            if remaining_recaudo > Decimal("0.00") and is_paid:
                payment_account = accounts_receivable # Fallback
                if payment_method == "CASH" and cash_account:
                    payment_account = cash_account
                elif payment_method in ("BANK_TRANSFER", "CARD", "TRANSFER") and bank_account:
                    payment_account = bank_account
                elif payment_method == "WALLET" and wallet_account:
                    payment_account = wallet_account

                if payment_account and payment_account.id != accounts_receivable.id:
                    # Credit Accounts Receivable
                    self.db.add(
                        JournalEntryLine(
                            journal_entry_id=db_je.id,
                            account_id=accounts_receivable.id,
                            debit_amount=Decimal("0.00"),
                            credit_amount=remaining_recaudo,
                            description=f"Recaudo - Factura {reference}",
                        )
                    )
                    # Debit Cash/Bank/Wallet
                    self.db.add(
                        JournalEntryLine(
                            journal_entry_id=db_je.id,
                            account_id=payment_account.id,
                            debit_amount=remaining_recaudo,
                            credit_amount=Decimal("0.00"),
                            description=f"Ingreso de dinero - {payment_method}",
                        )
                    )

        # COGS and Inventory reduction if total_cost > 0
        if total_cost > Decimal("0.00"):
            cost_of_sales = self._get_account_by_code(company_id, "6135")
            inventory_account = self._get_account_by_code(company_id, "1140")
            if cost_of_sales and inventory_account:
                # Debit: Cost of Sales
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=db_je.id,
                        account_id=cost_of_sales.id,
                        debit_amount=total_cost,
                        credit_amount=Decimal("0.00"),
                        description=f"Costo de ventas - Factura {reference}",
                    )
                )
                # Credit: Inventory
                self.db.add(
                    JournalEntryLine(
                        journal_entry_id=db_je.id,
                        account_id=inventory_account.id,
                        debit_amount=Decimal("0.00"),
                        credit_amount=total_cost,
                        description=f"Salida de inventario - Factura {reference}",
                    )
                )

        self.db.flush()
        self._validate_journal_entry_balance(db_je.id)
        if commit:
            self.db.commit()
            self.db.refresh(db_je)
        return db_je

    def _validate_journal_entry_balance(self, je_id: int) -> None:
        lines = (
            self.db.query(JournalEntryLine)
            .filter(JournalEntryLine.journal_entry_id == je_id)
            .all()
        )
        total_debits = sum(l.debit_amount for l in lines)
        total_credits = sum(l.credit_amount for l in lines)
        if total_debits != total_credits:
            self.db.rollback()
            raise ValueError(
                f"Journal entry #{je_id} is unbalanced "
                f"(debits={total_debits} != credits={total_credits})"
            )

    def _create_warranty_journal_entry(
        self,
        invoice_id: int,
        company_id: int,
        parts_cost: Decimal,
        labor_cost: Decimal,
    ) -> Optional[JournalEntry]:
        """
        Create journal entry for warranty repair.
        Records costs without revenue recognition.
        """
        cost_of_sales = self._get_account_by_code(company_id, "5100")
        inventory = self._get_account_by_code(company_id, "1140")

        if not cost_of_sales or not inventory:
            return None

        entry_date = datetime.now(timezone.utc)
        description = f"Garantía aplicada - Orden #{invoice_id}"
        reference = f"WRN-{invoice_id:06d}"

        db_je = JournalEntry(
            entry_date=entry_date,
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        # Debit: Cost of Sales (warranty expense)
        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=cost_of_sales.id,
                debit_amount=parts_cost,
                credit_amount=Decimal("0.00"),
                description=f"Costo garantía - Repuestos",
            )
        )

        # Credit: Inventory
        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=inventory.id,
                debit_amount=Decimal("0.00"),
                credit_amount=parts_cost,
                description=f"Salida de inventario por garantía",
            )
        )

        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    def create_inventory_journal_entry(
        self,
        company_id: int,
        product_id: int,
        quantity: int,
        unit_cost: Decimal,
        description: str,
        reference: str,
    ) -> Optional[JournalEntry]:
        """
        Create journal entry when inventory is used in repairs.
        Debit: Cost of Sales (5100)
        Credit: Inventory (1140)
        """
        cost_of_sales = self._get_account_by_code(company_id, "5100")
        inventory = self._get_account_by_code(company_id, "1140")

        if not cost_of_sales or not inventory:
            return None

        total_cost = quantity * unit_cost
        entry_date = datetime.now(timezone.utc)

        db_je = JournalEntry(
            entry_date=entry_date,
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=cost_of_sales.id,
                debit_amount=total_cost,
                credit_amount=Decimal("0.00"),
                description=f"Costo de repuestos - {description}",
            )
        )

        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=inventory.id,
                debit_amount=Decimal("0.00"),
                credit_amount=total_cost,
                description=f"Descuento de inventario - {description}",
            )
        )

        self.db.flush()
        self._validate_journal_entry_balance(db_je.id)
        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    def get_estado_resultados(
        self,
        company_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Estado de Resultados: Ingresos - Costos - Gastos = Utilidad Neta
        Basado en saldos del Libro Mayor.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            raise ValueError("Company not found")

        now = datetime.now(timezone.utc)
        date_from = date_from or datetime(now.year, 1, 1, tzinfo=timezone.utc)
        date_to = date_to or now

        ingresos = self._get_account_balance_by_type(
            company_id, "REVENUE", date_from, date_to
        )
        costos = self._get_account_balance_by_type(
            company_id, "COST", date_from, date_to
        )
        gastos = self._get_account_balance_by_type(
            company_id, "EXPENSE", date_from, date_to
        )

        total_ingresos = sum(a["balance"] for a in ingresos)
        total_costos = sum(a["balance"] for a in costos)
        total_gastos = sum(a["balance"] for a in gastos)
        utilidad_bruta = total_ingresos - total_costos
        utilidad_neta = utilidad_bruta - total_gastos

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "date_from": date_from,
            "date_to": date_to,
            "ingresos": ingresos,
            "total_ingresos": total_ingresos,
            "costos": costos,
            "total_costos": total_costos,
            "gastos": gastos,
            "total_gastos": total_gastos,
            "utilidad_bruta": utilidad_bruta,
            "utilidad_neta": utilidad_neta,
        }

    def get_balance_general(
        self, company_id: int, cut_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Balance General: Activos = Pasivos + Patrimonio
        Basado en saldos del Libro Mayor al corte.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            raise ValueError("Company not found")

        cut_date = cut_date or datetime.now(timezone.utc)

        activos = self._get_account_balance_by_type(company_id, "ASSET", None, cut_date)
        pasivos = self._get_account_balance_by_type(
            company_id, "LIABILITY", None, cut_date
        )
        patrimonio = self._get_account_balance_by_type(
            company_id, "EQUITY", None, cut_date
        )

        total_activos = sum(a["balance"] for a in activos)
        total_pasivos = sum(a["balance"] for a in pasivos)
        total_patrimonio = sum(a["balance"] for a in patrimonio)

        return {
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "cut_date": cut_date,
            "activos": activos,
            "total_activos": total_activos,
            "pasivos": pasivos,
            "total_pasivos": total_pasivos,
            "patrimonio": patrimonio,
            "total_patrimonio": total_patrimonio,
            "ecuacion_verificada": abs(
                total_activos - (total_pasivos + total_patrimonio)
            )
            < Decimal("0.01"),
        }

    def _get_account_balance_by_type(
        self,
        company_id: int,
        account_type: str,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get balances for all accounts of a given type.
        For ASSET/EXPENSE/COST: debit - credit = positive balance
        For LIABILITY/EQUITY/REVENUE: credit - debit = positive balance
        """
        nature_map = {
            "ASSET": "deudora",
            "EXPENSE": "deudora",
            "COST": "deudora",
            "LIABILITY": "acreedora",
            "EQUITY": "acreedora",
            "REVENUE": "acreedora",
        }
        nature = nature_map.get(account_type, "deudora")

        query = (
            self.db.query(
                ChartOfAccounts.code,
                ChartOfAccounts.name,
                sql_func.coalesce(
                    sql_func.sum(JournalEntryLine.debit_amount), Decimal("0.00")
                ).label("total_debit"),
                sql_func.coalesce(
                    sql_func.sum(JournalEntryLine.credit_amount), Decimal("0.00")
                ).label("total_credit"),
            )
            .join(JournalEntryLine, ChartOfAccounts.id == JournalEntryLine.account_id)
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .filter(
                ChartOfAccounts.company_id == company_id,
                ChartOfAccounts.account_type == account_type,
                JournalEntry.is_posted == True,
            )
        )

        if date_from:
            if isinstance(date_from, date) and not isinstance(date_from, datetime):
                date_from = datetime.combine(date_from, time.min, tzinfo=timezone.utc)
            query = query.filter(JournalEntry.entry_date >= date_from)
        if date_to:
            if isinstance(date_to, date) and not isinstance(date_to, datetime):
                date_to = datetime.combine(date_to, time.max, tzinfo=timezone.utc)
            else:
                date_to = date_to.replace(hour=23, minute=59, second=59)
            query = query.filter(JournalEntry.entry_date <= date_to)

        query = query.group_by(
            ChartOfAccounts.id, ChartOfAccounts.code, ChartOfAccounts.name
        )

        results = query.all()
        accounts = []
        for row in results:
            if nature == "deudora":
                balance = row.total_debit - row.total_credit
            else:
                balance = row.total_credit - row.total_debit
            if balance != 0:
                accounts.append(
                    {
                        "account_code": row.code,
                        "account_name": row.name,
                        "balance": balance,
                    }
                )
        return accounts

    def create_journal_entry_from_purchase(
        self,
        purchase_id: int,
        company_id: int,
        total_amount: Decimal,
        subtotal: Decimal,
        tax_amount: Decimal,
        partner_id: int,
        payment_method: str,
    ) -> Optional[JournalEntry]:
        """
        Create automatic journal entry from a purchase.

        For COMUN/ESPECIAL regimes:
          Debit: Inventarios (1140) - Subtotal
          Debit: IVA soportado (2408) - Tax
          Credit: Cuentas por pagar (2205) / Efectivo / Bancos - Total

        For SIMPLE regime:
          Debit: Inventarios (1140) - Total (no tax discrimination)
          Credit: Cuentas por pagar / Efectivo / Bancos - Total (no tax)
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            return None

        is_simple_regime = company.regimen in ("SIMPLE", "NO_RESPONSABLE")

        inventory = self._get_account_by_code(company_id, "1140")
        tax_receivable = self._get_account_by_code(company_id, "2408")
        accounts_payable = self._get_account_by_code(company_id, "2205")
        cash = self._get_account_by_code(company_id, "111001")
        bank = self._get_account_by_code(company_id, "111010")

        if not inventory or not accounts_payable:
            raise ValueError("Required chart of accounts not found for purchases")

        entry_date = datetime.now(timezone.utc)
        description = f"Compra a proveedor - Factura #{purchase_id}"
        reference = f"CP-{purchase_id:06d}"

        db_je = JournalEntry(
            entry_date=entry_date,
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        # Debit: Inventory
        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=inventory.id,
                debit_amount=subtotal if not is_simple_regime else total_amount,
                credit_amount=Decimal("0.00"),
                description=f"Inventarios - Compra {reference}",
            )
        )

        # Debit: IVA soportado (only for non-SIMPLE regimes)
        if not is_simple_regime and tax_amount > 0 and tax_receivable:
            self.db.add(
                JournalEntryLine(
                    journal_entry_id=db_je.id,
                    account_id=tax_receivable.id,
                    debit_amount=tax_amount,
                    credit_amount=Decimal("0.00"),
                    description=f"IVA soportado - Compra {reference}",
                )
            )

        # Credit: Choose account based on payment method
        credit_account = None
        if payment_method in ("CASH",):
            credit_account = cash
        elif payment_method in ("BANK_TRANSFER", "CHECK", "CREDIT_CARD"):
            credit_account = bank
        else:  # CREDIT, PARTIAL_CREDIT
            credit_account = accounts_payable

        if not credit_account:
            credit_account = accounts_payable

        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=credit_account.id,
                debit_amount=Decimal("0.00"),
                credit_amount=total_amount,
                description=f"Pago a proveedor - Compra {reference}",
            )
        )

        self.db.flush()
        self._validate_journal_entry_balance(db_je.id)
        self.db.commit()
        self.db.refresh(db_je)
        return db_je

    def get_formulario_350(self, company_id: int, year: int) -> Dict[str, Any]:
        """
        Genera datos para el Formulario 350 - Declaración de Renta Persona Jurídica.
        Incluye: ingresos ordinarios, extraordinarios, costos, deducciones,
        renta líquida, tarifa y impuesto de renta.
        """
        company = (
            self.db.query(company_model.Company)
            .filter(company_model.Company.id == company_id)
            .first()
        )
        if not company:
            raise ValueError("Company not found")

        date_from = datetime(year, 1, 1, tzinfo=timezone.utc)
        date_to = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)

        ingresos = self._get_account_balance_by_type(
            company_id, "REVENUE", date_from, date_to
        )
        costos = self._get_account_balance_by_type(
            company_id, "COST", date_from, date_to
        )
        gastos = self._get_account_balance_by_type(
            company_id, "EXPENSE", date_from, date_to
        )

        total_ingresos = sum(a["balance"] for a in ingresos)
        total_costos = sum(a["balance"] for a in costos)
        total_gastos = sum(a["balance"] for a in gastos)
        renta_liquida = total_ingresos - total_costos - total_gastos

        tarifa = Decimal("0.35") if company.regimen == "COMUN" else Decimal("0.0")
        if company.regimen in ("SIMPLE", "NO_RESPONSABLE"):
            tarifa = Decimal("0.0")

        impuesto_renta = max(Decimal("0.00"), renta_liquida * tarifa)

        return {
            "formulario": "350",
            "periodo_gravable": year,
            "company_id": company_id,
            "company_name": company.name,
            "company_nit": company.nit,
            "regimen": company.regimen,
            "ingresos_ordinarios": total_ingresos,
            "costos": total_costos,
            "deducciones": total_gastos,
            "renta_liquida": renta_liquida,
            "tarifa_aplicable": float(tarifa),
            "impuesto_renta": impuesto_renta,
            "detalle_ingresos": ingresos,
            "detalle_costos": costos,
            "detalle_gastos": gastos,
        }

    def create_journal_entry_for_initial_stock(
        self,
        product_id: int,
        product_name: str,
        company_id: int,
        total_amount: Decimal,
        payment_method: str,
    ) -> Optional[JournalEntry]:
        """
        Create automatic journal entry for initial stock of a product.
        Debit: Inventarios (1140)
        Credit: Caja/Banco/Cuentas por pagar (2205)
        """
        inventory = self._get_account_by_code(company_id, "1140")
        accounts_payable = self._get_account_by_code(company_id, "2205")
        cash = self._get_account_by_code(company_id, "111001")
        bank = self._get_account_by_code(company_id, "111010")

        if not inventory:
            raise ValueError("Required inventory account (1140) not found")

        entry_date = datetime.now(timezone.utc)
        description = f"Stock inicial producto - {product_name} (ID: {product_id})"
        reference = f"SI-{product_id:06d}"

        db_je = JournalEntry(
            entry_date=entry_date,
            description=description,
            reference=reference,
            company_id=company_id,
            is_posted=True,
        )
        self.db.add(db_je)
        self.db.flush()

        # Debit: Inventory
        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=inventory.id,
                debit_amount=total_amount,
                credit_amount=Decimal("0.00"),
                description=f"Inventarios - Stock inicial {product_name}",
            )
        )

        # Credit: Choose account based on payment method
        credit_account = None
        if payment_method in ("CASH",):
            credit_account = cash
        elif payment_method in ("BANK_TRANSFER", "CHECK", "CREDIT_CARD"):
            credit_account = bank
        else:  # CREDIT, PARTIAL_CREDIT
            credit_account = accounts_payable

        if not credit_account:
            credit_account = accounts_payable or inventory # Fallback

        self.db.add(
            JournalEntryLine(
                journal_entry_id=db_je.id,
                account_id=credit_account.id,
                debit_amount=Decimal("0.00"),
                credit_amount=total_amount,
                description=f"Pago stock inicial - {payment_method}",
            )
        )

        self.db.flush()
        self._validate_journal_entry_balance(db_je.id)
        self.db.commit()
        self.db.refresh(db_je)
        return db_je
