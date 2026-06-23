"""
Test de auditoria contable.
Ejecutar con: cd backend && pytest tests/test_contabilidad.py -v
"""
import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "backend/tests/test_contabilidad.py", "-v"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    sys.exit(result.returncode)
