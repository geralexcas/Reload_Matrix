#!/usr/bin/env python3
"""
Prueba Funcional completa — funcionalidad.md
"""
import requests
import json
from datetime import datetime, date

BASE = "http://localhost:8000/api/v1"
RESULTS = []
ERRORS = []


def log(phase, step, ok, detail=""):
    icon = "✅" if ok else "❌"
    print(f"{icon} [{phase}] {step}" + (f": {detail}" if detail else ""))
    RESULTS.append({"phase": phase, "step": step, "ok": ok, "detail": detail})
    if not ok:
        ERRORS.append({"phase": phase, "step": step, "detail": detail})


def ok_status(r):
    return r.status_code in (200, 201)


def get_token(username, password):
    r = requests.post(f"{BASE}/auth/token", data={"username": username, "password": password})
    return r.json()["access_token"] if r.status_code == 200 else None


def api(method, path, token, cid=None, json_data=None):
    h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    p = {"company_id": cid} if cid else {}
    return getattr(requests, method)(f"{BASE}{path}", headers=h, params=p, json=json_data)


def get_json(r):
    return r.json() if r.status_code < 400 else None


# ============================================================
# FASE 0: SETUP
# ============================================================
print("\n" + "=" * 70)
print("  FASE 0: SETUP")
print("=" * 70)

platform_token = get_token("admin@reloadmatrix.com", "Admin@123456")
log("Fase 0", "Login platform-admin", platform_token is not None)

evo_token = get_token("admin@evocomputo.com", "EvoAdmin@2026")
log("Fase 0", "Login evocomputo admin", evo_token is not None)

CID = 25
import time
TS = int(time.time()) % 100000  # unique suffix for numbers
print(f"  Company ID: {CID}  TS={TS}")


# ============================================================
# FASE 1: EMPRESA EVOCOMPUTO
# ============================================================
print("\n" + "=" * 70)
print("  FASE 1: EMPRESA EVOCOMPUTO")
print("=" * 70)

r = api("get", f"/companies/{CID}", platform_token)
log("Fase 1", "Empresa evocomputo existe", ok_status(r))


# ============================================================
# FASE 2: INVENTARIO Y TERCEROS
# ============================================================
print("\n" + "=" * 70)
print("  FASE 2: INVENTARIO Y TERCEROS")
print("=" * 70)

# --- Productos ---
r = api("post", "/inventory/", evo_token, CID, json_data={
    "sku": "EVO-001", "name": "Laptop HP Pavilion 15",
    "description": "Laptop HP 15.6, 8GB RAM, 256GB SSD",
    "category": "Laptops", "brand": "HP", "model": "Pavilion 15",
    "purchase_price": 1800000, "sale_price": 2500000, "stock_level": 10,
    "min_stock_level": 2, "max_stock_level": 50, "barcode": "7701234567890"
})
product_id = get_json(r).get("id") if ok_status(r) else None
log("Fase 2", "Crear producto Laptop HP", product_id is not None, f"id={product_id}")

r = api("post", "/inventory/", evo_token, CID, json_data={
    "sku": "EVO-002", "name": "Monitor LG 24 pulgadas",
    "description": "Monitor LED 24 Full HD",
    "category": "Monitores", "brand": "LG", "model": "24MP400",
    "purchase_price": 450000, "sale_price": 650000, "stock_level": 15,
    "min_stock_level": 3, "max_stock_level": 40,
})
product2_id = get_json(r).get("id") if ok_status(r) else None
log("Fase 2", "Crear producto Monitor LG", product2_id is not None, f"id={product2_id}")

# --- Terceros (sin NIT para evitar validación) ---
def create_partner(name, ptype, extra=None):
    data = {"name": name, "partner_type": ptype}
    if extra:
        data.update(extra)
    r = api("post", "/partners/", evo_token, CID, json_data=data)
    return get_json(r).get("id") if ok_status(r) else None

customer1_id = create_partner("Juan Perez Tecnologia", "CUSTOMER")
log("Fase 2", "Crear cliente Juan Perez", customer1_id is not None, f"id={customer1_id}")

customer2_id = create_partner("Maria Rodriguez SAS", "CUSTOMER")
log("Fase 2", "Crear cliente Maria Rodriguez", customer2_id is not None, f"id={customer2_id}")

supplier1_id = create_partner("Distribuidora Tech SA", "SUPPLIER")
log("Fase 2", "Crear proveedor Distribuidora Tech", supplier1_id is not None, f"id={supplier1_id}")

supplier2_id = create_partner("Importaciones Digitales Ltda", "SUPPLIER")
log("Fase 2", "Crear proveedor Importaciones Digitales", supplier2_id is not None, f"id={supplier2_id}")

supplier3_id = create_partner("Mayorista Computadores CO", "SUPPLIER")
log("Fase 2", "Crear proveedor Mayorista Computadores", supplier3_id is not None, f"id={supplier3_id}")


# ============================================================
# FASE 3: RECEPCIÓN EQUIPO + SERVICIO TÉCNICO $50.000
# ============================================================
print("\n" + "=" * 70)
print("  FASE 3: RECEPCIÓN EQUIPO + SERVICIO TÉCNICO")
print("=" * 70)

r = api("post", "/repair/with-items/", evo_token, CID, json_data={
    "partner_id": customer1_id,
    "issue_date": datetime.now().isoformat(),
    "problem_description": "Laptop no enciende, pantalla rota",
    "device_type": "Laptop", "brand": "Dell", "model": "Inspiron 15",
    "serial_number": "DL-2024-XYZ",
    "total_labor_cost": 30000, "total_parts_cost": 20000, "total_amount": 50000,
    "items": [
        {"description": "Reparación de pantalla laptop Dell", "quantity": 1,
         "unit_cost": 20000, "line_total": 20000, "warranty_status": "NO_WARRANTY"},
        {"description": "Mano de obra reparación laptop", "quantity": 1,
         "unit_cost": 30000, "line_total": 30000, "warranty_status": "NO_WARRANTY"}
    ]
})
repair_id = get_json(r).get("id") if ok_status(r) else None
if not ok_status(r):
    print(f"    Repair error: {r.status_code} {r.text[:300]}")
log("Fase 3", "Crear orden de reparación", repair_id is not None, f"id={repair_id}")

if repair_id:
    r = api("post", f"/repair/{repair_id}/generate-invoice/", evo_token, CID, json_data={
        "is_paid": True, "payment_method": "CASH", "amount_paid": 50000
    })
    invoice_repair = get_json(r).get("id") if ok_status(r) else None
    if not ok_status(r):
        print(f"    Invoice from repair error: {r.status_code} {r.text[:300]}")
    log("Fase 3", "Factura desde reparación (efectivo $50.000)", invoice_repair is not None, f"id={invoice_repair}")
else:
    log("Fase 3", "Factura desde reparación", False, "No hay orden de reparación")


# ============================================================
# FASE 4: FACTURACIÓN
# ============================================================
print("\n" + "=" * 70)
print("  FASE 4: FACTURACIÓN")
print("=" * 70)

# Factura 1: transferencia
r = api("post", "/invoicing/with-items/", evo_token, CID, json_data={
    "invoice_type": "SALE", "partner_id": customer2_id,
    "issue_date": datetime.now().isoformat(),
    "total_amount": 2500000, "payment_method": "BANK_TRANSFER", "is_paid": True,
    "items": [{
        "description": "Laptop HP Pavilion 15", "quantity": 1,
        "unit_price": 2500000, "line_total": 2500000,
        "product_id": product_id, "tax_rate": 19
    }]
})
invoice1_id = get_json(r).get("id") if ok_status(r) else None
if not ok_status(r):
    print(f"    Invoice1 error: {r.status_code} {r.text[:300]}")
log("Fase 4", "Factura venta transferencia $2.500.000", invoice1_id is not None, f"id={invoice1_id}")

# Factura 2: contado
r = api("post", "/invoicing/with-items/", evo_token, CID, json_data={
    "invoice_type": "SALE", "partner_id": customer1_id,
    "issue_date": datetime.now().isoformat(),
    "total_amount": 650000, "payment_method": "CASH", "is_paid": True,
    "items": [{
        "description": "Monitor LG 24 pulgadas", "quantity": 1,
        "unit_price": 650000, "line_total": 650000,
        "product_id": product2_id, "tax_rate": 19
    }]
})
invoice2_id = get_json(r).get("id") if ok_status(r) else None
if not ok_status(r):
    print(f"    Invoice2 error: {r.status_code} {r.text[:300]}")
log("Fase 4", "Factura venta contado $650.000", invoice2_id is not None, f"id={invoice2_id}")


# ============================================================
# FASE 5: COMPRAS
# ============================================================
print("\n" + "=" * 70)
print("  FASE 5: COMPRAS")
print("=" * 70)

# Compra 1: transferencia
r = api("post", "/purchases/", evo_token, CID, json_data={
    "purchase_number": f"COMP-{TS}-001", "partner_id": supplier1_id,
    "purchase_date": datetime.now().isoformat(),
    "payment_method": "BANK_TRANSFER", "status": "DRAFT",
    "items": [
        {"description": "Laptop HP (proveedor)", "quantity": 3, "unit_price": 1800000, "line_total": 5400000, "product_id": product_id, "tax_rate": 19},
        {"description": "Monitor LG (proveedor)", "quantity": 5, "unit_price": 450000, "line_total": 2250000, "product_id": product2_id, "tax_rate": 19},
    ]
})
purchase1_id = get_json(r).get("id") if ok_status(r) else None
if not ok_status(r):
    print(f"    Purchase1 error: {r.status_code} {r.text[:300]}")
log("Fase 5", "Compra 1 transferencia", purchase1_id is not None, f"id={purchase1_id}")

if purchase1_id:
    r = api("post", f"/purchases/{purchase1_id}/pay", evo_token, CID, json_data={
        "payment_method": "BANK_TRANSFER", "amount": 7650000, "reference": "TRF-2026-001"
    })
    log("Fase 5", "Pago compra 1 transferencia", ok_status(r), r.text[:100] if not ok_status(r) else "")

# Compra 2: efectivo
r = api("post", "/purchases/", evo_token, CID, json_data={
    "purchase_number": f"COMP-{TS}-002", "partner_id": supplier2_id,
    "purchase_date": datetime.now().isoformat(),
    "payment_method": "CASH", "status": "DRAFT",
    "items": [
        {"description": "Mouse Logitech", "quantity": 20, "unit_price": 45000, "line_total": 900000, "tax_rate": 19},
        {"description": "Teclado Redragon", "quantity": 10, "unit_price": 120000, "line_total": 1200000, "tax_rate": 19},
    ]
})
purchase2_id = get_json(r).get("id") if ok_status(r) else None
if not ok_status(r):
    print(f"    Purchase2 error: {r.status_code} {r.text[:300]}")
log("Fase 5", "Compra 2 efectivo", purchase2_id is not None, f"id={purchase2_id}")

if purchase2_id:
    r = api("post", f"/purchases/{purchase2_id}/pay", evo_token, CID, json_data={
        "payment_method": "CASH", "amount": 2100000, "reference": "EFV-2026-001"
    })
    log("Fase 5", "Pago compra 2 efectivo", ok_status(r), r.text[:100] if not ok_status(r) else "")

# Compra 3: crédito
r = api("post", "/purchases/", evo_token, CID, json_data={
    "purchase_number": f"COMP-{TS}-003", "partner_id": supplier3_id,
    "purchase_date": datetime.now().isoformat(),
    "payment_method": "CREDIT", "status": "DRAFT",
    "items": [
        {"description": "Impresora Epson L3250", "quantity": 4, "unit_price": 650000, "line_total": 2600000, "tax_rate": 19},
        {"description": "Escáner Brother", "quantity": 2, "unit_price": 380000, "line_total": 760000, "tax_rate": 19},
    ]
})
purchase3_id = get_json(r).get("id") if ok_status(r) else None
if not ok_status(r):
    print(f"    Purchase3 error: {r.status_code} {r.text[:300]}")
log("Fase 5", "Compra 3 crédito", purchase3_id is not None, f"id={purchase3_id}")


# ============================================================
# FASE 6: ASIENTO CONTABLE — ARRIENDO $1.000.000
# ============================================================
print("\n" + "=" * 70)
print("  FASE 6: ASIENTO CONTABLE — ARRIENDO")
print("=" * 70)

# Buscar cuentas
r = api("get", "/accounting/chart-of-accounts/", evo_token, CID)
expense_acc = None
bank_acc = None
if ok_status(r):
    for acc in r.json():
        c = acc.get("code", "")
        n = acc.get("name", "").lower()
        if c == "5220" or "arriendo" in n:
            expense_acc = acc
        if c == "111010":
            bank_acc = acc
    # Fallbacks
    if not expense_acc:
        for acc in r.json():
            if acc.get("code", "").startswith("5") and acc.get("account_type") == "EXPENSE":
                expense_acc = acc
                break
    if not bank_acc:
        for acc in r.json():
            if acc.get("code") in ("111001", "111010", "111012"):
                bank_acc = acc
                break

if expense_acc:
    log("Fase 6", "Cuenta gasto", True, f"{expense_acc['code']} - {expense_acc['name']}")
else:
    log("Fase 6", "Cuenta gasto", False, "No se encontró")

if bank_acc:
    log("Fase 6", "Cuenta banco", True, f"{bank_acc['code']} - {bank_acc['name']}")
else:
    log("Fase 6", "Cuenta banco", False, "No se encontró")

if expense_acc and bank_acc:
    r = api("post", "/accounting/journal-entries/with-lines/", evo_token, CID, json_data={
        "entry_date": datetime.now().isoformat(),
        "description": "Pago de arriendo mensual",
        "lines": [
            {"account_id": expense_acc["id"], "debit_amount": 1000000, "credit_amount": 0,
             "description": "Gasto arriendo mensual"},
            {"account_id": bank_acc["id"], "debit_amount": 0, "credit_amount": 1000000,
             "description": "Pago arriendo por transferencia bancaria"}
        ]
    })
    je_id = get_json(r).get("id") if ok_status(r) else None
    if not ok_status(r):
        print(f"    JE error: {r.status_code} {r.text[:300]}")
    log("Fase 6", "Asiento arriendo $1.000.000", je_id is not None, f"je_id={je_id}")

    # Verificar líneas del asiento
    if je_id:
        r2 = api("get", f"/accounting/journal-entries/{je_id}", evo_token, CID)
        if ok_status(r2):
            je = r2.json()
            lines = je.get("journal_entry_lines", [])
            print(f"    Asiento #{je_id}: {len(lines)} líneas")
            for l in lines:
                print(f"      Cuenta {l.get('account_id')}: débito={l.get('debit_amount')} crédito={l.get('credit_amount')}")
else:
    log("Fase 6", "Crear asiento arriendo", False, "Faltan cuentas contables")


# ============================================================
# FASE 7: REVISIÓN CONTABLE COMPLETA
# ============================================================
print("\n" + "=" * 70)
print("  FASE 7: REVISIÓN CONTABLE COMPLETA")
print("=" * 70)

# 7.1 Trial Balance
r = api("get", "/accounting/trial-balance", evo_token, CID)
if ok_status(r):
    tb = r.json()
    total_d = float(tb.get("total_debit", 0))
    total_c = float(tb.get("total_credit", 0))
    balanced = abs(total_d - total_c) < 0.01
    log("Fase 7.1", "Trial Balance", balanced,
        f"débitos=${total_d:,.2f} créditos=${total_c:,.2f}")
    for acc in tb.get("accounts", []):
        d = float(acc.get("total_debit", 0))
        c = float(acc.get("total_credit", 0))
        if d > 0 or c > 0:
            print(f"    {acc.get('code','')} {acc.get('name','')}: déb=${d:,.2f} crd=${c:,.2f}")
else:
    log("Fase 7.1", "Trial Balance", False, r.text[:200])

# 7.2 Balance General
r = api("get", "/accounting/balance-general/", evo_token, CID)
if ok_status(r):
    bg = r.json()
    a = float(bg.get("assets", {}).get("total", 0))
    l = float(bg.get("liabilities", {}).get("total", 0))
    p = float(bg.get("equity", {}).get("total", 0))
    ok = abs(a - (l + p)) < 0.01
    log("Fase 7.2", "Balance General", ok,
        f"A=${a:,.2f} P+Pa=${l+p:,.2f}")
else:
    log("Fase 7.2", "Balance General", False, r.text[:200])

# 7.3 Estado de Resultados
r = api("get", "/accounting/estado-resultados/", evo_token, CID)
if ok_status(r):
    er = r.json()
    ti = float(er.get("total_ingresos", 0))
    tc = float(er.get("total_costos", 0))
    tg = float(er.get("total_gastos", 0))
    un = float(er.get("utilidad_neta", 0))
    log("Fase 7.3", "Estado de Resultados", True,
        f"ingresos=${ti:,.2f} costos=${tc:,.2f} gastos=${tg:,.2f} utilidad=${un:,.2f}")
else:
    log("Fase 7.3", "Estado de Resultados", False, r.text[:200])

# 7.4 Libro Diario
r = api("get", "/accounting/journal-entries/", evo_token, CID)
if ok_status(r):
    entries = r.json()
    log("Fase 7.4", "Libro Diario", True, f"{len(entries)} asientos")
    for e in entries:
        posted = "✓" if e.get("is_posted") else "✗"
        print(f"    #{e.get('id','')} [{posted}] {e.get('description','')}")
else:
    log("Fase 7.4", "Libro Diario", False, r.text[:200])

# 7.5 Ingresos
r = api("get", "/accounting/reporte-ingresos/", evo_token, CID)
if ok_status(r):
    ri = r.json()
    t = ri.get("totals", {})
    log("Fase 7.5", "Reporte Ingresos", True,
        f"op=${float(t.get('total_ingresos_operacionales',0)):,.2f} nop=${float(t.get('total_ingresos_no_operacionales',0)):,.2f} iva_gen=${float(t.get('total_iva_generado',0)):,.2f}")
else:
    log("Fase 7.5", "Reporte Ingresos", False, r.text[:200])

# 7.6 Egresos
r = api("get", "/accounting/reporte-egresos/", evo_token, CID)
if ok_status(r):
    re_resp = r.json()
    t = re_resp.get("totals", {})
    log("Fase 7.6", "Reporte Egresos", True,
        f"compras=${float(t.get('total_compras_netas',0)):,.2f} iva_desc=${float(t.get('total_iva_descontable',0)):,.2f}")
else:
    log("Fase 7.6", "Reporte Egresos", False, r.text[:200])

# 7.7 Patrimonio
r = api("get", "/accounting/reporte-patrimonio/", evo_token, CID)
if ok_status(r):
    rp = r.json()
    log("Fase 7.7", "Reporte Patrimonio", True,
        f"activos=${float(rp.get('total_activos',0)):,.2f} pasivos=${float(rp.get('total_pasivos',0)):,.2f} patrimonio=${float(rp.get('total_patrimonio',0)):,.2f}")
else:
    log("Fase 7.7", "Reporte Patrimonio", False, r.text[:200])

# 7.8 Tesorería
r = api("get", "/treasury/summary/", evo_token, CID)
if ok_status(r):
    ts = r.json()
    log("Fase 7.8", "Tesorería Resumen", True,
        f"bancos=${ts.get('total_banks',0):,.2f} caja=${ts.get('total_cash',0):,.2f}")
else:
    log("Fase 7.8", "Tesorería Resumen", False, r.text[:200])

# 7.9 Transacciones
r = api("get", "/treasury/transactions/", evo_token, CID)
if ok_status(r):
    txs = r.json()
    log("Fase 7.9", "Transacciones Tesorería", True, f"{len(txs)} transacciones")
    for tx in txs:
        print(f"    #{tx.get('id','')}: {tx.get('transaction_type','')} ${float(tx.get('amount',0)):,.2f} {tx.get('description','')}")
else:
    log("Fase 7.9", "Transacciones Tesorería", False, r.text[:200])

# 7.10 Facturas
r = api("get", "/invoicing/", evo_token, CID)
if ok_status(r):
    invs = r.json()
    log("Fase 7.10", "Facturas", True, f"{len(invs)} facturas")
    for i in invs:
        print(f"    #{i.get('id','')} {i.get('invoice_number','N/A')} total=${float(i.get('total_amount',0)):,.2f} paid={i.get('is_paid',False)}")
else:
    log("Fase 7.10", "Facturas", False, r.text[:200])

# 7.11 Compras
r = api("get", "/purchases/", evo_token, CID)
if ok_status(r):
    pcs = r.json()
    log("Fase 7.11", "Compras", True, f"{len(pcs)} compras")
    for p in pcs:
        print(f"    #{p.get('id','')} {p.get('purchase_number','')} total=${float(p.get('total_amount',0)):,.2f} status={p.get('status','')}")
else:
    log("Fase 7.11", "Compras", False, r.text[:200])

# 7.12 Cuentas por Pagar
r = api("get", "/purchases/accounts-payable", evo_token, CID)
if ok_status(r):
    ap = r.json()
    s = ap.get("summary", {})
    log("Fase 7.12", "Cuentas por Pagar", True,
        f"pendientes={s.get('pending_count',0)} total=${s.get('total_pending',0):,.2f}")
else:
    log("Fase 7.12", "Cuentas por Pagar", False, r.text[:200])

# 7.13 Declaración IVA
r = api("get", "/accounting/declaracion-iva/", evo_token, CID)
if ok_status(r):
    iva = r.json()
    log("Fase 7.13", "Declaración IVA", True)
    for k, v in iva.items():
        if isinstance(v, (int, float)):
            print(f"    {k}: ${v:,.2f}")
else:
    log("Fase 7.13", "Declaración IVA", False, r.text[:200])


# ============================================================
# RESUMEN
# ============================================================
print("\n" + "=" * 70)
print("  RESUMEN DE PRUEBA FUNCIONAL")
print("=" * 70)

passed = sum(1 for r in RESULTS if r["ok"])
failed = sum(1 for r in RESULTS if not r["ok"])
total = len(RESULTS)

print(f"\n  Total: {total} | ✅ Pass: {passed} | ❌ Fail: {failed}")
print()

if ERRORS:
    print("  PROBLEMAS ENCONTRADOS:")
    for e in ERRORS:
        print(f"    ❌ [{e['phase']}] {e['step']}: {e['detail']}")
else:
    print("  🎉 TODAS LAS PRUEBAS PASARON")
print()
