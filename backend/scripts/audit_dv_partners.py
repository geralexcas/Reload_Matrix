"""
Auditoría NO destructiva: lista partners cuyo DV almacenado no coincide con
el DV calculado por el algoritmo DIAN correcto (Modulo 11, longitud variable).

No modifica NITs ni DVs de la base de datos; sólo reporta para que el
operador decida la acción correctiva manual (corregir el dato, contactar al
cliente, o aceptar el DV registrado por alguna otra regla).

Uso (dentro del contenedor backend):
    python scripts/audit_dv_partners.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import re
from app.core.database import SessionLocal
from app.models.sql.partners import Partner


WEIGHTS = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]


def calculate_dv(nit: str) -> str | None:
    """Calcula DV DIAN Modulo 11 (algoritmo unificado front/back)."""
    clean = re.sub(r"[-\s.]", "", nit or "")
    if not clean.isdigit() or len(clean) < 5:
        return None
    rev = clean[::-1]
    total = 0
    for i, digit in enumerate(rev):
        total += int(digit) * WEIGHTS[i % len(WEIGHTS)]
    rem = total % 11
    if rem == 0:
        return "0"
    if rem == 1:
        return "K"
    return str(11 - rem)


def main():
    db = SessionLocal()
    try:
        partners = db.query(Partner).all()
        if not partners:
            print("No hay partners en la base de datos.")
            return

        mismatches = []
        skipped = []
        for p in partners:
            dv_db = (p.dv or "").upper()
            if not p.nit or not dv_db:
                # Some partners legitimately have no DV (e.g. cédula)
                skipped.append(p)
                continue
            expected = calculate_dv(p.nit)
            if expected is None:
                skipped.append(p)
                continue
            if expected != dv_db:
                mismatches.append({
                    "id": p.id,
                    "company_id": p.company_id,
                    "name": p.name,
                    "nit_db": p.nit,
                    "dv_db": dv_db,
                    "dv_expected": expected,
                    "partner_type": p.partner_type,
                })

        print("=" * 70)
        print("AUDITORIA DE DIGITOS DE VERIFICACION (NO DESTRUCTIVA)")
        print("=" * 70)
        print(f"Total partners revisados: {len(partners)}")
        print(f"Partners saltados (sin DV/NIT): {len(skipped)}")
        print(f"Discrepancias encontradas:  {len(mismatches)}")
        print()

        if mismatches:
            print("-" * 70)
            print("PARTNERS CON DV POSIBLEMENTE INVALIDO:")
            print("-" * 70)
            for m in mismatches:
                print(f"  id={m['id']} company_id={m['company_id']} "
                      f"tipo={m['partner_type']}")
                print(f"    nombre: {m['name']}")
                print(f"    NIT DB:      {m['nit_db']}-{m['dv_db']}")
                print(f"    DV esperado: {m['dv_expected']}")
                print()
            print("Accion recomendada (manual, no automatica):")
            print("  1. Verificar el NIT original del cliente contra el RUT.")
            print("  2. Si el NIT es correcto y el DV esta mal, corregir el DV.")
            print("  3. Si el NIT ingresado en DB esta mal (digitos equivocados),")
            print("     corregir el NIT; el DV se recalcula desde el NIT.")
            print("  4. NO recalcular DV en cascada sin confirmar el dato origen:")
            print("     un NIT mal ingresado quedaria 'validado' contra si mismo.")
        else:
            print("OK: todos los partners con DV tienen el digito correcto.")

    finally:
        db.close()


if __name__ == "__main__":
    main()