"""
Script de reparación de tesorería (repair_treasury.py)
-------------------------------------------------------
Encuentra asientos contables publicados que afectan cuentas de banco/caja
y que NO tienen transacción de tesorería registrada. Los repara actualizando
el current_balance y creando los registros TreasuryTransaction faltantes.

Uso dentro del contenedor Docker:
  docker exec reload_matrix-backend-1 python /app/app/repair_treasury.py

O pasando empresa específica:
  docker exec reload_matrix-backend-1 python /app/app/repair_treasury.py --company_id 1 --dry_run
"""

import argparse
import sys
import os
from decimal import Decimal

# Añadir el directorio raíz al path
sys.path.insert(0, "/app")

from app.core.database import SessionLocal
from app.models.sql.accounting.journal_entry import JournalEntry
from app.models.sql.accounting.journal_entry_line import JournalEntryLine
from app.models.sql.accounting.chart_of_accounts import ChartOfAccounts
from app.models.sql.accounting.bank_account import BankAccount
from app.models.sql.accounting.cash_account import CashAccount
from app.models.sql.accounting.treasury_transaction import TreasuryTransaction
from app.models.sql import company as company_model


def get_treasury_account(db, line_account_id, company_id):
    """
    Dado un account_id de una línea de asiento, devuelve la cuenta de tesorería
    vinculada (BankAccount o CashAccount) y su tipo ('BANK'/'CASH').
    Busca primero por ID exacto, luego por prefijo de código.
    """
    line_coa = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line_account_id).first()
    if not line_coa:
        return None, None

    line_code = line_coa.code

    # Pass 1: exact match - BankAccount
    bank = db.query(BankAccount).filter(
        BankAccount.linked_account_id == line_account_id,
        BankAccount.company_id == company_id,
        BankAccount.is_active == True,
    ).first()
    if bank:
        return bank, "BANK"

    # Pass 2: prefix match - BankAccount
    all_banks = db.query(BankAccount).filter(
        BankAccount.company_id == company_id,
        BankAccount.is_active == True,
        BankAccount.linked_account_id != None,
    ).all()
    for candidate in all_banks:
        coa = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == candidate.linked_account_id).first()
        if coa:
            c_code = coa.code
            if line_code.startswith(c_code) or c_code.startswith(line_code):
                return candidate, "BANK"

    # Pass 1: exact match - CashAccount
    cash = db.query(CashAccount).filter(
        CashAccount.linked_account_id == line_account_id,
        CashAccount.company_id == company_id,
        CashAccount.is_active == True,
    ).first()
    if cash:
        return cash, "CASH"

    # Pass 2: prefix match - CashAccount
    all_cash = db.query(CashAccount).filter(
        CashAccount.company_id == company_id,
        CashAccount.is_active == True,
        CashAccount.linked_account_id != None,
    ).all()
    for candidate in all_cash:
        coa = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == candidate.linked_account_id).first()
        if coa:
            c_code = coa.code
            if line_code.startswith(c_code) or c_code.startswith(line_code):
                return candidate, "CASH"

    return None, None


def repair_treasury(company_id: int, dry_run: bool = False, skip_refs: list = None):
    db = SessionLocal()
    skip_refs = skip_refs or []
    try:
        print(f"\n{'='*60}")
        print(f"REPARACIÓN DE TESORERÍA - Empresa ID: {company_id}")
        print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'APLICANDO CAMBIOS'}")
        if skip_refs:
            print(f"Omitiendo referencias: {skip_refs}")
        print(f"{'='*60}\n")

        # Obtener estado actual de las cuentas de tesorería
        banks = db.query(BankAccount).filter(
            BankAccount.company_id == company_id,
            BankAccount.is_active == True,
        ).all()
        cash_accounts = db.query(CashAccount).filter(
            CashAccount.company_id == company_id,
            CashAccount.is_active == True,
        ).all()

        print("📊 Saldos actuales en Tesorería:")
        for b in banks:
            print(f"  🏦 {b.name} ({b.bank_name}): ${b.current_balance:,.2f}")
        for c in cash_accounts:
            print(f"  💵 {c.name}: ${c.current_balance:,.2f}")
        print()

        # Simulación de saldos para dry-run (por ID de cuenta de tesorería)
        simulated_bank_balances = {b.id: b.current_balance for b in banks}
        simulated_cash_balances = {c.id: c.current_balance for c in cash_accounts}

        # IDs de asientos que ya tienen transacción de tesorería
        existing_tx_je_ids = set(
            row[0]
            for row in db.query(TreasuryTransaction.journal_entry_id)
            .filter(
                TreasuryTransaction.company_id == company_id,
                TreasuryTransaction.journal_entry_id != None,
            )
            .all()
        )
        print(f"✅ Asientos ya con transacción de tesorería: {sorted(existing_tx_je_ids)}\n")

        # Obtener todos los asientos PUBLICADOS de la empresa
        posted_entries = db.query(JournalEntry).filter(
            JournalEntry.company_id == company_id,
            JournalEntry.is_posted == True,
        ).order_by(JournalEntry.entry_date.asc(), JournalEntry.id.asc()).all()

        print(f"📋 Asientos publicados encontrados: {len(posted_entries)}\n")

        repaired = 0
        skipped = 0

        for je in posted_entries:
            # Omitir si el usuario especificó referencias a saltar
            if skip_refs and je.reference and any(je.reference.startswith(r) for r in skip_refs):
                print(f"  ⏩ JE #{je.id} ({je.reference}) → OMITIDO por filtro de referencia")
                continue

            lines = db.query(JournalEntryLine).filter(
                JournalEntryLine.journal_entry_id == je.id
            ).all()

            for line in lines:
                if not line.account_id:
                    continue

                treasury_acct, acct_type = get_treasury_account(db, line.account_id, company_id)
                if not treasury_acct:
                    continue

                already_exists = je.id in existing_tx_je_ids
                net_change = line.debit_amount - line.credit_amount

                if net_change == Decimal("0.00"):
                    continue

                acct_name = treasury_acct.name
                line_coa = db.query(ChartOfAccounts).filter(ChartOfAccounts.id == line.account_id).first()
                code = line_coa.code if line_coa else '?'

                if already_exists:
                    print(f"  ⏭  JE #{je.id} ({je.description[:40]}) → {acct_type} '{acct_name}' [CUENTA {code}] → YA PROCESADO")
                    skipped += 1
                    continue

                tx_type = "DEPOSIT" if net_change > 0 else "WITHDRAWAL"

                if dry_run:
                    # Simulate cumulative balance
                    if acct_type == "BANK":
                        bal_before = simulated_bank_balances.get(treasury_acct.id, treasury_acct.current_balance)
                        simulated_bank_balances[treasury_acct.id] = bal_before + net_change
                        bal_after = simulated_bank_balances[treasury_acct.id]
                    else:
                        bal_before = simulated_cash_balances.get(treasury_acct.id, treasury_acct.current_balance)
                        simulated_cash_balances[treasury_acct.id] = bal_before + net_change
                        bal_after = simulated_cash_balances[treasury_acct.id]
                    print(f"  🔧 JE #{je.id} '{je.description[:35]}' → {acct_type} '{acct_name}' [{code}] | ${abs(net_change):,.2f} {tx_type} | ${bal_before:,.2f} → ${bal_after:,.2f} [DRY]")
                else:
                    bal_before = treasury_acct.current_balance
                    treasury_acct.current_balance += net_change
                    bal_after = treasury_acct.current_balance

                    tx = TreasuryTransaction(
                        company_id=company_id,
                        account_type=acct_type,
                        bank_account_id=treasury_acct.id if acct_type == "BANK" else None,
                        cash_account_id=treasury_acct.id if acct_type == "CASH" else None,
                        transaction_type=tx_type,
                        amount=abs(net_change),
                        description=line.description or je.description,
                        reference=je.reference or f"REPAIR-JE-{je.id}",
                        journal_entry_id=je.id,
                        balance_after=bal_after,
                    )
                    db.add(tx)
                    existing_tx_je_ids.add(je.id)
                    print(f"  ✅ JE #{je.id} '{je.description[:35]}' → {acct_type} '{acct_name}' [{code}] | ${abs(net_change):,.2f} {tx_type} | ${bal_before:,.2f} → ${bal_after:,.2f}")

                repaired += 1

        if not dry_run and repaired > 0:
            db.commit()
            print(f"\n✅ COMMIT realizado. Se repararon {repaired} transacciones.")
        elif dry_run:
            print(f"\n📋 DRY-RUN completado. Se repararían {repaired} transacciones.")
            print("     → Ejecutar sin --dry_run para aplicar los cambios reales.")
        else:
            print(f"\n✅ No se encontraron asientos pendientes de reparar.")

        # Mostrar estado final
        print("\n📊 Saldos FINALES en Tesorería:")
        db.expire_all()
        for b in db.query(BankAccount).filter(BankAccount.company_id == company_id, BankAccount.is_active == True).all():
            print(f"  🏦 {b.name} ({b.bank_name}): ${b.current_balance:,.2f}")
        for c in db.query(CashAccount).filter(CashAccount.company_id == company_id, CashAccount.is_active == True).all():
            print(f"  💵 {c.name}: ${c.current_balance:,.2f}")

        print(f"\n{'='*60}\n")
        return repaired

    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reparar transacciones de tesorería faltantes")
    parser.add_argument("--company_id", type=int, default=1, help="ID de la empresa (default: 1)")
    parser.add_argument("--dry_run", action="store_true", help="Simular sin aplicar cambios")
    parser.add_argument("--skip_refs", nargs="*", default=[], help="Prefijos de referencia a omitir (ej: INV CP)")
    args = parser.parse_args()

    repair_treasury(company_id=args.company_id, dry_run=args.dry_run, skip_refs=args.skip_refs)

