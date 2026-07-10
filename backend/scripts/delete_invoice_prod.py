"""DEPRECATED: Usar delete_ghost_asiento.py en su lugar.

Este script tenia dos bugs:
  1. Exigia que la factura existiera (abortaba sin limpiar el asiento huerfano).
  2. Buscaba reference == 'INV-00000007' (8 digitos) cuando el servicio genera
     f'INV-{id:06d}' = 'INV-000007' (6 digitos).

Ademas, con el trigger trg_prevent_invoice_delete activo (migracion
a4b5c6d7e8f9), el DELETE directo en invoices falla — este script ya no puede
borrar la factura, y esa es la intencion.

Redirige a delete_ghost_asiento.py que limpima solo el asiento huerfano sin
tocar la tabla invoices.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("DEPRECATED: delete_invoice_prod.py")
print("=" * 70)
print("Este script esta deprecado y sera eliminado.")
print("Usa: python scripts/delete_ghost_asiento.py --invoice-id <id> [--force]")
print("Ese script limpia el asiento huerfano sin tocar la tabla invoices")
print("(que ahora tiene un trigger que impide el borrado directo).")
print("=" * 70)

if "--force" not in sys.argv:
    print("\nPara proceder con el script correcto, ejecuta:")
    print("  python scripts/delete_ghost_asiento.py --invoice-id 7")
    sys.exit(0)

# --force: delegar al script correcto
import argparse
from delete_ghost_asiento import main
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:] if a != "--force"] + ["--force"]
main()