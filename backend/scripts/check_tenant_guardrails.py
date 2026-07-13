#!/usr/bin/env python3
"""Guardrails de aislamiento multi-tenant (CI check).

Banea patrones que bypassan el filtro ORM (app/core/tenant_context.py) y por
ende dependen unicamente de RLS para no filtrar:

1. Raw SQL (`text(...)`) en app/services/ o app/api/  — bypassa el ORM
   auto-filter.  RLS lo cubre, pero queremos que el bypass sea explicito y
   raro; si aparece, moverlo a una capa donde se setee app.tenant_id.
2. Bulk Query.update()/Query.delete() (`.query(Model).filter(...).update(`
   o `...delete()`) — bypassa el SELECT-auto-filter.  Los services usan
   select-then-modify; el bulk es una excepcion que debe justificarse.

Excepciones permitidas: main.py (healthcheck SELECT 1), alembic/ (migraciones).

Uso:
    python scripts/check_tenant_guardrails.py
Exit 0 = OK; exit 1 = violaciones encontradas (falla el CI).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCAN_DIRS = [ROOT / "app" / "services", ROOT / "app" / "api"]

RAW_SQL_RE = re.compile(r"\btext\s*\(")
# .query(...)...).update(  o  ...).delete()  despues de un .query( o .filter(
BULK_UPDATE_RE = re.compile(r"\.update\s*\(\s*\{")
BULK_DELETE_RE = re.compile(r"\.query\([^)]*\)\.delete\s*\(\s*\)")


def scan(path: Path):
    findings = []
    for src in SCAN_DIRS:
        if not src.exists():
            continue
        for py in src.rglob("*.py"):
            rel = py.relative_to(ROOT)
            text_lines = py.read_text(encoding="utf-8").splitlines()
            for i, line in enumerate(text_lines, 1):
                # Saltar comentarios
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                if RAW_SQL_RE.search(line):
                    findings.append(f"{rel}:{i}: raw SQL `text()` — usar ORM")
                if BULK_UPDATE_RE.search(line):
                    findings.append(f"{rel}:{i}: bulk `.update({{}})` — usar select-then-modify")
                if BULK_DELETE_RE.search(line):
                    findings.append(f"{rel}:{i}: bulk `.delete()` — usar select-then-modify")
    return findings


def main():
    findings = scan(ROOT)
    if findings:
        print("Guardrail violaciones (bypass del filtro multi-tenant):", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        print(
            "\nSi es legitimo: setear current_tenant_id antes (RLS cubre), "
            "o mover a un script fuera de services/api.",
            file=sys.stderr,
        )
        return 1
    print("OK: sin bypass del filtro multi-tenant en services/api.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
