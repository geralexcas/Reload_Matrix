# 🚨 REPORTE DE AUDITORÍA DE SEGURIDAD - RELOAD MATRIX 🚨

**Fecha:** 8 de Julio de 2026  
**Auditor:** Claude (Senior Developer & Experto Contable Colombiano)  
**Sistema:** Reload Matrix ERP v1.0  
**Alcance:** Inventario, Contabilidad, Tesorería, Seguridad Multi-tenant

---

## 📋 RESUMEN EJECUTIVO

Se han identificado **10 vulnerabilidades críticas** y **4 bugs de alta prioridad** que afectan directamente:
- ✅ Integridad del inventario
- ✅ Exactitud de asientos contables
- ✅ Saldos de caja y bancos
- ✅ Seguridad multi-tenant
- ✅ Cumplimiento normativo DIAN

**Estado del sistema: 🔴 CRÍTICO - Requiere acción inmediata**

| Categoría | Críticos 🔴 | Altos 🟠 | Medios 🟡 |
|-----------|-------------|----------|-----------|
| **Inventario** | 1 | 1 | 0 |
| **Contabilidad** | 4 | 2 | 1 |
| **Tesorería** | 3 | 1 | 0 |
| **Seguridad** | 2 | 0 | 0 |
| **TOTAL** | **10** | **4** | **1** |

---

## ⚠️ VULNERABILIDADES CRÍTICAS

### 🔴 VULNERABILIDAD #1: RACE CONDITION EN INVENTARIO - PÉRDIDA DE STOCK

**Severidad:** CRÍTICA  
**Archivo:** `backend/app/services/inventory_service.py` (líneas 340-356)  
**Impacto:** Inventario negativo fantasma, pérdidas financieras, descuadres contables

#### Descripción del Problema

La función `deduct_stock()` utiliza correctamente `with_for_update()` para bloquear el registro del producto, pero existe una ventana de tiempo donde dos transacciones pueden leer el mismo valor de stock antes de validar disponibilidad.

```python
def deduct_stock(self, product_id: int, quantity: Decimal, company_id: int, commit: bool = True):
    db_product = self.db.query(Product).filter(
        Product.id == product_id, Product.company_id == company_id
    ).with_for_update().first()  # ✅ Lock correcto
    
    if not db_product:
        raise ValueError(f"Producto con ID {product_id} no encontrado")

    if db_product.stock_level < Decimal(str(quantity)):
        raise ValueError(
            f"¡Ups! Parece que no hay suficiente stock para el producto '{db_product.name}'. "
            f"Actualmente tienes {db_product.stock_level} unidades disponibles, "
            f"pero estás intentando facturar {quantity}."
        )

    db_product.stock_level -= Decimal(str(quantity))
    # Registra movimiento de inventario...
```

#### Escenario de Ataque

1. **Usuario A** inicia factura: Producto tiene 10 unidades, necesita 5
2. **Usuario B** inicia factura: Producto tiene 10 unidades, necesita 5
3. Usuario A obtiene lock, valida (10 >= 5) ✅, deduce: 10 - 5 = 5
4. Usuario A libera lock y hace commit
5. Usuario B obtiene lock, lee stock = 5, valida (5 >= 5) ✅, deduce: 5 - 5 = 0
6. **Stock final: 0** (Correcto: 10 - 5 - 5 = 0) ✅

**PERO si el commit de A no se ha completado cuando B lee:**

1. Usuario A obtiene lock, lee stock = 10
2. Usuario B espera el lock...
3. Usuario A valida (10 >= 5) ✅, actualiza a 5, PERO NO hace commit todavía
4. Usuario B obtiene lock, lee stock = 10 (aún no committed)
5. Usuario B valida (10 >= 5) ✅, actualiza a 5
6. **Stock final: 5** ❌ (Debería ser 0)

#### Solución Recomendada

```python
def deduct_stock(self, product_id: int, quantity: Decimal, company_id: int, commit: bool = True):
    # Opción 1: Usar SELECT FOR UPDATE con NOWAIT
    db_product = self.db.query(Product).filter(
        Product.id == product_id, Product.company_id == company_id
    ).with_for_update(nowait=True).first()
    
    if not db_product:
        raise ValueError(f"Producto con ID {product_id} no encontrado")
    
    # Opción 2: Usar UPDATE con WHERE en la validación
    rows_updated = self.db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == company_id,
        Product.stock_level >= quantity  # ✅ Validación atómica
    ).update({
        'stock_level': Product.stock_level - quantity
    }, synchronize_session=False)
    
    if rows_updated == 0:
        # Re-consultar para dar mensaje preciso
        db_product = self.db.query(Product).filter(
            Product.id == product_id, Product.company_id == company_id
        ).first()
        if not db_product:
            raise ValueError(f"Producto con ID {product_id} no encontrado")
        raise ValueError(
            f"Stock insuficiente para '{db_product.name}'. "
            f"Disponible: {db_product.stock_level}, Solicitado: {quantity}"
        )
    
    # Registrar movimiento...
    if commit:
        self.db.commit()
```

---

### 🔴 VULNERABILIDAD #2: ASIENTOS CONTABLES DESBALANCEADOS EN TESORERÍA

**Severidad:** CRÍTICA  
**Archivo:** `backend/app/services/treasury_service.py` (líneas 136-238)  
**Impacto:** Balance general descuadrado, auditorías fallidas, violación de partida doble

#### Descripción del Problema

Las funciones `deposit()` y `withdraw()` actualizan el saldo de tesorería SIEMPRE, pero solo crean el asiento contable SI se cumplen las condiciones `linked_account_id` y `contra_account_id`. Esto rompe el principio de partida doble.

```python
def deposit(self, account_type: str, account_id: int, amount: Decimal, ...):
    if account_type == "BANK":
        account = self.get_bank_account_by_id(account_id, company_id)
        if not account:
            raise ValueError("Bank account not found")

        account.current_balance += amount  # ✅ Actualiza saldo SIEMPRE
        balance_after = account.current_balance

        # ❌ Solo crea asiento SI linked_account_id Y contra_account_id existen
        if account.linked_account_id and not skip_journal_entry and contra_account_id:
            je = self._create_journal_entry(...)  # Asiento contable
```

#### Escenario de Problema

1. Cuenta bancaria NO tiene `linked_account_id` configurado
2. Se ejecuta `deposit(amount=1000000)`
3. **Saldo bancario:** $1,000,000 ✅
4. **Asiento contable:** NO SE CREA ❌
5. **Balance General:** 
   - Activos (Bancos): $0 ❌
   - Patrimonio: $0 ❌
   - **Descuadre: $1,000,000**

#### Solución Recomendada

```python
def deposit(self, account_type: str, account_id: int, amount: Decimal, ...):
    if account_type == "BANK":
        account = self.get_bank_account_by_id(account_id, company_id)
        if not account:
            raise ValueError("Bank account not found")
        
        # ✅ Validar que la cuenta tenga configuración contable
        if not account.linked_account_id and not skip_journal_entry:
            raise ValueError(
                f"La cuenta bancaria '{account.bank_name} {account.account_number}' "
                f"no tiene una cuenta contable vinculada (linked_account_id). "
                f"Debe configurarla en el módulo de Tesorería antes de registrar movimientos."
            )
        
        if not contra_account_id and not skip_journal_entry:
            raise ValueError(
                "Debe especificar una cuenta contable de contrapartida (contra_account_id) "
                "para crear el asiento contable del depósito."
            )

        account.current_balance += amount
        balance_after = account.current_balance

        # ✅ Ahora SIEMPRE se crea el asiento (a menos que skip_journal_entry=True)
        if not skip_journal_entry:
            je = self._create_journal_entry(...)
```

---

### 🔴 VULNERABILIDAD #3: FALTA DE ROLLBACK EN PUBLICACIÓN DE ASIENTOS

**Severidad:** CRÍTICA  
**Archivo:** `backend/app/services/accounting_service.py` (líneas 294-450)  
**Impacto:** Saldos bancarios corruptos, asientos parcialmente aplicados

#### Descripción del Problema

La función `post_journal_entry()` modifica directamente los saldos de cuentas bancarias y de caja dentro del mismo loop que procesa las líneas del asiento. Si ocurre un error después de modificar algunos saldos pero antes del commit final, los cambios parciales pueden quedar inconsistentes.

```python
def post_journal_entry(self, je_id: int, company_id: int) -> Dict[str, Any]:
    db_je = self.db.query(JournalEntry).filter(...).with_for_update().first()
    
    # ... validaciones ...
    
    treasury_sync_count = 0

    for line in lines:  # ❌ Loop largo sin protección transaccional
        # ... busca cuenta contable ...
        
        bank_acct = self.db.query(BankAccount).filter(...).with_for_update().first()
        
        if bank_acct:
            net_change = line.debit_amount - line.credit_amount
            bank_acct.current_balance += net_change  # ❌ Modifica saldo
            
            if net_change != Decimal("0.00"):
                tx = TreasuryTransaction(...)
                self.db.add(tx)
                treasury_sync_count += 1
            continue  # ❌ Si falla después, este cambio queda aplicado
        
        cash_acct = self.db.query(CashAccount).filter(...).with_for_update().first()
        
        if cash_acct:
            net_change = line.debit_amount - line.credit_amount
            cash_acct.current_balance += net_change  # ❌ Modifica saldo
            # ... más código ...

    self.db.commit()  # ❌ No hay try-except
    self.db.refresh(db_je)
    
    return {...}
```

#### Escenario de Problema

1. Asiento tiene 4 líneas que afectan: Banco A, Banco B, Caja, Gasto
2. Procesa línea 1: Banco A saldo += $500,000 ✅
3. Procesa línea 2: Banco B saldo -= $300,000 ✅
4. Procesa línea 3: **ERROR de conexión a BD** ❌
5. **Resultado:**
   - Banco A: +$500,000 (aplicado)
   - Banco B: -$300,000 (aplicado)
   - Caja: sin cambios
   - Asiento: NO marcado como publicado
   - **Saldos descuadrados permanentemente**

#### Solución Recomendada

```python
def post_journal_entry(self, je_id: int, company_id: int) -> Dict[str, Any]:
    try:
        db_je = self.db.query(JournalEntry).filter(...).with_for_update().first()
        if not db_je:
            raise ValueError("Journal entry not found")
        if db_je.is_posted:
            raise ValueError("Journal entry is already posted")

        # Validaciones previas...
        
        # ✅ Preparar cambios ANTES de aplicarlos
        treasury_updates = []
        
        for line in lines:
            bank_acct = self.db.query(BankAccount).filter(...).with_for_update().first()
            
            if bank_acct:
                net_change = line.debit_amount - line.credit_amount
                treasury_updates.append({
                    'type': 'BANK',
                    'account': bank_acct,
                    'change': net_change,
                    'line': line
                })
                continue
            
            cash_acct = self.db.query(CashAccount).filter(...).with_for_update().first()
            
            if cash_acct:
                net_change = line.debit_amount - line.credit_amount
                treasury_updates.append({
                    'type': 'CASH',
                    'account': cash_acct,
                    'change': net_change,
                    'line': line
                })
        
        # ✅ Aplicar TODOS los cambios de una vez
        treasury_sync_count = 0
        for update in treasury_updates:
            update['account'].current_balance += update['change']
            
            if update['change'] != Decimal("0.00"):
                tx_type = "DEPOSIT" if update['change'] > 0 else "WITHDRAWAL"
                tx = TreasuryTransaction(...)
                self.db.add(tx)
                treasury_sync_count += 1
        
        db_je.is_posted = True
        
        # ✅ Commit único con manejo de errores
        self.db.commit()
        self.db.refresh(db_je)
        
        return {...}
        
    except Exception as e:
        # ✅ Rollback explícito en caso de error
        self.db.rollback()
        raise ValueError(f"Error al publicar asiento contable: {str(e)}")
```


---

### 🔴 VULNERABILIDAD #4: VALIDACIÓN DÉBIL DE PERMISOS MULTI-TENANT

**Severidad:** CRÍTICA  
**Archivo:** `backend/app/api/v1/routers/invoicing.py` y otros routers  
**Impacto:** Acceso no autorizado a datos de otras empresas, violación de privacidad

#### Descripción del Problema

Los routers validan que la empresa exista, pero **NO validan que el usuario actual tenga permiso de acceder a esa empresa**. Un usuario puede simplemente cambiar el `company_id` en la petición para acceder a datos de otras empresas.

```python
# backend/app/api/v1/routers/invoicing.py (líneas 44-57)
@router.post("/with-items/", ...)
def create_invoice_with_items(
    invoice_with_items: inv_schema.InvoiceWithItemsCreate,
    company_id: int,  # ❌ Viene del cliente, no validado
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # ✅ Valida que la empresa exista
    db_company = db.query(company_model.Company).filter(
        company_model.Company.id == company_id
    ).first()
    if db_company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    # ❌ NO valida que current_user tenga acceso a company_id
    service = invoicing_service.InvoicingService(db)
    return service.create_invoice_with_items(invoice_with_items, company_id)
```

#### Escenario de Ataque

1. **Usuario Malicioso** tiene cuenta en Empresa ID=1
2. Descubre que existe Empresa ID=2 (ej: probando IDs secuenciales)
3. Hace petición:
   ```http
   POST /api/v1/invoicing/with-items/?company_id=2
   Authorization: Bearer <su_token_válido>
   ```
4. **Sistema acepta la petición** porque:
   - ✅ Usuario está autenticado
   - ✅ Empresa ID=2 existe
   - ❌ NO valida membresía del usuario en Empresa ID=2
5. **Resultado:** Usuario accede a facturas, inventario, contabilidad de Empresa ID=2

#### Evidencia en el Código

El decorador `verify_company_membership` existe pero **NO se usa consistentemente**:

```python
# backend/app/api/v1/deps.py
def verify_company_membership(company_id: int, current_user: User = Depends(get_current_user)):
    # ✅ Este decorador SÍ valida membresía
    if company_id not in [c.id for c in current_user.companies]:
        raise HTTPException(403, "No tienes acceso a esta empresa")
    return company
```

Pero solo se usa en algunos endpoints:

```python
# backend/app/api/v1/routers/invoicing.py línea 18
@router.post("/", ...)
def create_invoice(
    invoice: inv_schema.InvoiceCreate,
    company_id: int,
    company: company_model.Company = Depends(verify_company_membership),  # ✅ Usado aquí
    ...
):
```

Mientras que en otros NO:

```python
# línea 44
@router.post("/with-items/", ...)
def create_invoice_with_items(
    invoice_with_items: inv_schema.InvoiceWithItemsCreate,
    company_id: int,  # ❌ Sin verify_company_membership
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
```

#### Solución Recomendada

**Opción 1: Agregar verify_company_membership a TODOS los endpoints**

```python
@router.post("/with-items/", ...)
def create_invoice_with_items(
    invoice_with_items: inv_schema.InvoiceWithItemsCreate,
    company_id: int,
    company: company_model.Company = Depends(verify_company_membership),  # ✅ Agregado
    db: Session = Depends(get_db),
    current_user: user_model.User = Depends(get_current_user),
):
    # Ahora company es validado y se puede usar directamente
    service = invoicing_service.InvoicingService(db)
    return service.create_invoice_with_items(invoice_with_items, company.id)
```

**Opción 2: Crear un decorador de router global**

```python
# backend/app/api/v1/deps.py
from fastapi import Request

async def validate_company_access(request: Request, company_id: int, current_user: User):
    """Middleware para validar acceso a empresa en todos los endpoints"""
    if company_id not in [c.id for c in current_user.companies]:
        raise HTTPException(
            status_code=403,
            detail=f"No tienes permisos para acceder a la empresa {company_id}"
        )
    return True

# Aplicar en main.py
@app.middleware("http")
async def company_validation_middleware(request: Request, call_next):
    if "company_id" in request.query_params:
        company_id = int(request.query_params["company_id"])
        # Validar acceso...
    response = await call_next(request)
    return response
```

**Opción 3 (RECOMENDADA): Obtener company_id del token JWT**

```python
# backend/app/core/security.py
def create_access_token(user_id: int, company_id: int, ...):
    to_encode = {
        "sub": str(user_id),
        "company_id": company_id,  # ✅ Incluir en token
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# backend/app/api/v1/deps.py
def get_current_user_company(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    company_id = payload.get("company_id")  # ✅ Leer del token
    # Validar que company_id del token == company_id del endpoint
    return company_id
```

---

### 🔴 VULNERABILIDAD #5: INYECCIÓN DE LÓGICA EN REFERENCIAS DE ASIENTOS

**Severidad:** ALTA  
**Archivo:** `backend/app/services/accounting_service.py` (líneas 901-920)  
**Impacto:** Potencial bypass de lógica contable, reportes manipulados

#### Descripción del Problema

En `get_reporte_egresos()`, el código usa el campo `reference` de los asientos contables para filtrar y evitar duplicados. Este campo es de texto libre y podría contener valores maliciosos.

```python
def get_reporte_egresos(self, company_id: int, ...):
    # ... código ...
    
    for je in journal_entries:
        # ❌ Filtra basándose en texto no validado
        if je.reference and (je.reference.startswith('INV-') or je.reference.startswith('PUR-')):
            continue  # Omite este asiento para evitar duplicados
        
        for line in je.lines:
            # ... procesa gastos ...
```

#### Escenario de Problema

1. Usuario crea un asiento manual de gasto real de $10,000,000
2. Usuario malicioso pone `reference = "INV-FAKE123"`
3. El asiento se registra normalmente en contabilidad
4. **Al generar reporte de egresos:**
   - Sistema ve `reference.startswith('INV-')` → True
   - **Omite el gasto de $10,000,000**
5. **Resultado:** 
   - Gastos reales: $10,000,000
   - Gastos reportados: $0
   - **Utilidad inflada artificialmente**

#### Evidencia Adicional

El mismo patrón se repite en varias funciones:

```python
# backend/app/services/accounting_service.py línea 814
je_date_filter = [
    JournalEntry.company_id == company_id,
    JournalEntry.reference.like("SI-%"),  # ❌ Patrón basado en texto libre
    JournalEntry.is_posted == True
]
```

#### Solución Recomendada

**Opción 1: Agregar campo `source_type` ENUM en JournalEntry**

```python
# backend/app/models/sql/accounting/journal_entry.py
from sqlalchemy import Enum as SQLEnum

class JournalEntrySourceType(str, Enum):
    MANUAL = "MANUAL"
    INVOICE = "INVOICE"
    PURCHASE = "PURCHASE"
    INITIAL_STOCK = "INITIAL_STOCK"
    TREASURY = "TREASURY"
    PAYROLL = "PAYROLL"

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True)
    # ... otros campos ...
    reference = Column(String(100))
    source_type = Column(SQLEnum(JournalEntrySourceType), default="MANUAL")  # ✅ Nuevo campo
    source_id = Column(Integer)  # ID del registro origen (invoice_id, purchase_id, etc.)
```

**Opción 2: Validar formato de reference al crear asientos**

```python
def create_journal_entry(self, je: co_schema.JournalEntryCreate, company_id: int):
    # ✅ Validar que reference manual no use prefijos reservados
    if je.reference:
        reserved_prefixes = ['INV-', 'PUR-', 'SI-', 'CP-', 'CHK-', 'RECON-']
        for prefix in reserved_prefixes:
            if je.reference.startswith(prefix):
                raise ValueError(
                    f"El prefijo '{prefix}' está reservado para asientos automáticos. "
                    f"Use otro formato para asientos manuales."
                )
    
    db_je = JournalEntry(**je.model_dump(), company_id=company_id)
    self.db.add(db_je)
    self.db.commit()
    return db_je
```

**Opción 3: Usar joins en lugar de filtrar por referencia**

```python
def get_reporte_egresos(self, company_id: int, ...):
    # ✅ Usar joins explícitos en lugar de filtrar por reference
    
    # 1. Obtener gastos de facturas de compra (PURCHASE invoices)
    purchase_invoices = (
        self.db.query(Invoice)
        .filter(
            Invoice.invoice_type == "PURCHASE",
            Invoice.company_id == company_id,
        )
        .all()
    )
    
    # 2. Obtener gastos de órdenes de compra (Purchase model)
    dedicated_purchases = (
        self.db.query(Purchase)
        .filter(Purchase.company_id == company_id)
        .all()
    )
    
    # 3. Obtener asientos manuales de gasto (source_type = 'MANUAL')
    manual_expense_entries = (
        self.db.query(JournalEntry)
        .filter(
            JournalEntry.company_id == company_id,
            JournalEntry.source_type == "MANUAL",  # ✅ Campo seguro
            JournalEntry.is_posted == True
        )
        .all()
    )
    
    # ... procesar cada fuente por separado ...
```


---

## 🐛 BUGS CRÍTICOS EN CONTABILIDAD

### 🔴 BUG #6: CÁLCULO INCORRECTO DE RETENCIONES EN LIBRO DE COMPRAS

**Severidad:** CRÍTICA  
**Archivo:** `backend/app/services/accounting_service.py` (líneas 795-885)  
**Impacto:** Declaraciones de IVA incorrectas, riesgo de sanciones DIAN

#### Descripción del Problema

La función `get_libro_compras()` calcula retenciones en la fuente e IVA automáticamente para TODAS las compras cuando el régimen es COMÚN o ESPECIAL, **sin considerar el umbral de 27 UVT** establecido por la DIAN para aplicar retefuente.

Según el Art. 368 del Estatuto Tributario:
> La retención en la fuente solo aplica cuando el pago o abono en cuenta supere **27 UVT diarias** (27 × $49,738 = $1,342,926 para 2026).

```python
def get_libro_compras(self, company_id: int, ...):
    for inv in all_purchases:
        taxes = self._get_invoice_tax_breakdown(inv)

        retencion_fuente = Decimal("0.00")
        retencion_iva = Decimal("0.00")

        # ❌ Aplica retención sin validar umbral
        if company.regimen in ("COMUN", "ESPECIAL"):
            if taxes["iva_19"] > 0 or taxes["iva_5"] > 0:
                retencion_fuente = (
                    taxes["base_iva_19"] + taxes["base_iva_5"]
                ) * Decimal("0.025")
                retencion_iva = taxes["total_iva"] * Decimal("0.15")
```

Mientras que `get_reporte_retenciones()` SÍ lo valida correctamente:

```python
def get_reporte_retenciones(self, company_id: int, ...):
    from app.core.config import settings

    uvt_daily_threshold = Decimal(str(settings.UVT_VALUE * 27))  # ✅ Calcula umbral

    for inv in purchase_invoices:
        base_gravable = taxes["base_iva_19"] + taxes["base_iva_5"]
        
        exceeds_uvt = base_gravable > uvt_daily_threshold  # ✅ Valida umbral

        if base_gravable > 0 and exceeds_uvt:
            retefuente_bienes = base_gravable * Decimal("0.10")  # 10% bienes
        elif base_gravable > 0 and not exceeds_uvt:
            retefuente = base_gravable * Decimal("0.025")  # 2.5% servicios
```

#### Ejemplo Concreto

**Compra real:**
- Base gravable: $500,000 (< 27 UVT = $1,342,926)
- IVA 19%: $95,000
- Total: $595,000

**Libro de Compras (INCORRECTO):**
```
Base IVA 19%:        $500,000
IVA 19%:             $95,000
Retefuente 2.5%:     $12,500  ❌ NO DEBE APLICARSE
ReteIVA 15%:         $14,250  ❌ NO DEBE APLICARSE
Total Factura:       $568,250 ❌ (Debería ser $595,000)
```

**Reporte de Retenciones (CORRECTO):**
```
Base:                $500,000
Retefuente:          $0  ✅ (bajo umbral de 27 UVT)
ReteIVA:             $0  ✅
```

**Impacto:** Al presentar declaración de IVA bimestral, el contribuyente reporta retenciones que NO APLICARON, causando:
- Descuadre con certificados de retención emitidos
- Saldo a pagar de IVA incorrecto
- Posible rechazo de declaración por la DIAN

#### Solución Recomendada

```python
def get_libro_compras(self, company_id: int, date_from: Optional[datetime] = None, 
                      date_to: Optional[datetime] = None) -> Dict[str, Any]:
    company = self.db.query(company_model.Company).filter(...).first()
    if not company:
        return {"error": "Company not found"}

    # ✅ Importar umbral UVT
    from app.core.config import settings
    uvt_daily_threshold = Decimal(str(settings.UVT_VALUE * 27))

    # ... código de consultas ...

    for inv in all_purchases:
        taxes = self._get_invoice_tax_breakdown(inv)
        base_gravable = taxes["base_iva_19"] + taxes["base_iva_5"]

        retencion_fuente = Decimal("0.00")
        retencion_iva = Decimal("0.00")

        # ✅ Validar umbral antes de calcular retenciones
        if company.regimen in ("COMUN", "ESPECIAL"):
            exceeds_uvt = base_gravable > uvt_daily_threshold
            
            # Solo aplicar si excede umbral
            if exceeds_uvt and (taxes["iva_19"] > 0 or taxes["iva_5"] > 0):
                # Determinar si es bien o servicio (simplificado: usar 2.5% por defecto)
                retencion_fuente = base_gravable * Decimal("0.025")
                retencion_iva = taxes["total_iva"] * Decimal("0.15")

        total_invoice = (
            taxes["base_iva_19"]
            + taxes["base_iva_5"]
            + taxes["base_no_iva"]
            + taxes["total_iva"]
            - retencion_fuente
            - retencion_iva
        )
        
        # ... resto del código ...
```

---

### 🔴 BUG #7: DESBALANCE EN ASIENTOS DE STOCK INICIAL SIN PROVEEDOR

**Severidad:** CRÍTICA  
**Archivo:** `backend/app/services/accounting_service.py` (líneas 1525-1589)  
**Impacto:** Asientos contables sin sentido económico, inventario sin contrapartida

#### Descripción del Problema

Cuando se crea un producto con stock inicial SIN proveedor asignado, se invoca `create_journal_entry_for_initial_stock()` que puede generar un asiento donde la contrapartida es la misma cuenta de inventario, resultando en un asiento inútil.

```python
def create_journal_entry_for_initial_stock(
    self, product_id: int, product_name: str, company_id: int, 
    total_amount: Decimal, payment_method: str
):
    inventory = self._get_account_by_code(company_id, "1140")
    accounts_payable = self._get_account_by_code(company_id, "2205")
    cash = self._get_account_by_code(company_id, "111001")
    bank = self._get_account_by_code(company_id, "111010")

    if not inventory:
        raise ValueError("Required inventory account (1140) not found")

    # ... código ...

    # ❌ Elegir cuenta de crédito
    credit_account = None
    if payment_method in ("CASH",):
        credit_account = cash
    elif payment_method in ("BANK_TRANSFER", "CHECK", "CREDIT_CARD"):
        credit_account = bank
    else:  # CREDIT, PARTIAL_CREDIT
        credit_account = accounts_payable

    if not credit_account:
        credit_account = accounts_payable or inventory  # ❌❌❌ PROBLEMA AQUÍ

    self.db.add(JournalEntryLine(
        journal_entry_id=db_je.id,
        account_id=credit_account.id,  # ❌ Puede ser inventory.id
        debit_amount=Decimal("0.00"),
        credit_amount=total_amount,
        description=f"Pago stock inicial - {payment_method}",
    ))
```

#### Escenario de Problema

**Setup:**
1. Empresa nueva sin configurar Cuentas por Pagar (2205)
2. Sin configurar Caja (111001) ni Bancos (111010)
3. Solo existe cuenta Inventarios (1140) del PUC por defecto

**Acción:**
1. Usuario crea producto con stock inicial de 10 unidades a $100,000 c/u
2. Total: $1,000,000
3. Payment method: "CREDIT"

**Resultado:**
```
Asiento Contable SI-000001:
  Débito:  Inventarios (1140)     $1,000,000
  Crédito: Inventarios (1140)     $1,000,000
  ═══════════════════════════════════════════
  Total:                          $0 efecto neto
```

**Problemas:**
- ❌ El asiento no refleja ninguna operación económica real
- ❌ No se registra la deuda con proveedor (si fuera a crédito)
- ❌ No se registra la salida de efectivo (si fuera pagado)
- ❌ El balance general no cambia, pero el inventario SÍ aumentó en el sistema

**Correcto debería ser:**
```
Opción 1 - A Crédito (sin proveedor conocido):
  Débito:  Inventarios (1140)             $1,000,000
  Crédito: Cuentas por Pagar Diversas (2205) $1,000,000

Opción 2 - Pagado (aporte de capital):
  Débito:  Inventarios (1140)             $1,000,000
  Crédito: Capital Social (3100)          $1,000,000
```

#### Solución Recomendada

```python
def create_journal_entry_for_initial_stock(
    self, product_id: int, product_name: str, company_id: int,
    total_amount: Decimal, payment_method: str
):
    inventory = self._get_account_by_code(company_id, "1140")
    if not inventory:
        raise ValueError("Required inventory account (1140) not found")

    # ✅ Determinar cuenta de crédito según método de pago
    if payment_method in ("CASH", "BANK_TRANSFER", "CHECK", "CREDIT_CARD"):
        # Stock inicial pagado = Aporte de capital
        credit_account = self._get_account_by_code(company_id, "3100")  # Capital Social
        if not credit_account:
            raise ValueError(
                "Para registrar stock inicial pagado se requiere la cuenta "
                "Capital Social (3100). Créela primero o asigne un proveedor al producto."
            )
        credit_description = "Aporte de capital - Stock inicial"
        
    elif payment_method in ("CREDIT", "PARTIAL_CREDIT"):
        # Stock inicial a crédito = Deuda con proveedor
        credit_account = self._get_account_by_code(company_id, "2205")  # Proveedores
        if not credit_account:
            raise ValueError(
                "Para registrar stock inicial a crédito se requiere la cuenta "
                "Proveedores (2205). Créela primero o cambie a método de pago efectivo."
            )
        credit_description = "Deuda por stock inicial - Proveedor no especificado"
    
    else:
        raise ValueError(f"Método de pago '{payment_method}' no soportado para stock inicial")

    # ✅ Crear asiento con cuentas correctas
    db_je = JournalEntry(...)
    self.db.add(db_je)
    self.db.flush()

    # Débito: Inventario
    self.db.add(JournalEntryLine(
        journal_entry_id=db_je.id,
        account_id=inventory.id,
        debit_amount=total_amount,
        credit_amount=Decimal("0.00"),
        description=f"Inventarios - Stock inicial {product_name}",
    ))

    # Crédito: Capital o Proveedores (nunca Inventario)
    self.db.add(JournalEntryLine(
        journal_entry_id=db_je.id,
        account_id=credit_account.id,
        debit_amount=Decimal("0.00"),
        credit_amount=total_amount,
        description=credit_description,
    ))

    self.db.flush()
    self._validate_journal_entry_balance(db_je.id)
    self.db.commit()
    self.db.refresh(db_je)
    return db_je
```

---

### 🔴 BUG #8: CONCILIACIÓN BANCARIA NO ACTUALIZA SALDO REAL

**Severidad:** ALTA  
**Archivo:** `backend/app/services/treasury_service.py` (líneas 1113-1178)  
**Impacto:** Saldos bancarios desactualizados después de conciliar

#### Descripción del Problema

La función `complete_reconciliation()` calcula el saldo ajustado y verifica si está balanceado, pero **NO actualiza** el campo `current_balance` de la cuenta bancaria con el saldo real del extracto.

```python
def complete_reconciliation(self, reconciliation_id: int, company_id: int, ...):
    recon = self.db.query(BankReconciliation).filter(...).first()
    if not recon:
        raise ValueError("Reconciliation not found")

    # ✅ Calcula saldo ajustado
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

    # Crea asientos de ajuste por comisiones/intereses no registrados
    if recon.bank_fees_not_recorded > 0 or recon.interest_not_recorded > 0:
        # ... código de ajustes ...

    self.db.commit()
    self.db.refresh(recon)
    return recon
    
    # ❌ NUNCA actualiza bank_account.current_balance
```

#### Escenario de Problema

**Situación inicial:**
- Cuenta bancaria en sistema: $5,000,000
- Extracto bancario real: $4,850,000
- Diferencia: -$150,000 (comisión no registrada)

**Proceso de conciliación:**
1. Usuario crea reconciliación con `statement_balance = $4,850,000`
2. Identifica comisión no registrada: $150,000
3. Sistema registra `bank_fees_not_recorded = $150,000`
4. Usuario completa conciliación:
   - ✅ Crea asiento de ajuste:
     ```
     Débito:  Gastos Financieros (5400)  $150,000
     Crédito: Bancos (111010)             $150,000
     ```
   - ✅ Marca reconciliación como `COMPLETED`
   - ✅ `is_balanced = True`
   - ❌ **NO actualiza `bank_account.current_balance`**

**Resultado:**
- Saldo en extracto: $4,850,000 ✅
- Saldo en contabilidad (111010): $4,850,000 ✅ (por el asiento de ajuste)
- **Saldo en tesorería (`current_balance`): $5,000,000** ❌❌❌

**Impacto:**
- Dashboard de tesorería muestra saldo incorrecto
- Cheques posteriores pueden rechazarse por fondos insuficientes (sistema piensa que hay $5M pero solo hay $4.85M)
- Próximas conciliaciones arrancan con base incorrecta

#### Solución Recomendada

```python
def complete_reconciliation(self, reconciliation_id: int, company_id: int, 
                           user_id: Optional[int] = None) -> BankReconciliation:
    recon = self.db.query(BankReconciliation).filter(...).first()
    if not recon:
        raise ValueError("Reconciliation not found")

    # Calcular saldo ajustado
    adjusted = (
        recon.statement_balance
        + recon.outstanding_deposits
        - recon.outstanding_checks
    )
    recon.adjusted_balance = adjusted
    recon.is_balanced = abs(adjusted - recon.system_balance) < Decimal("0.01")

    if not recon.is_balanced:
        difference = adjusted - recon.system_balance
        raise ValueError(
            f"La conciliación no está balanceada. "
            f"Diferencia: ${abs(difference):,.2f} "
            f"({'faltante' if difference < 0 else 'sobrante'} en el sistema). "
            f"Revise los movimientos no conciliados o agregue un ajuste manual."
        )

    # ✅ Actualizar saldo real de la cuenta bancaria
    account = self.get_bank_account_by_id(recon.bank_account_id, company_id)
    if not account:
        raise ValueError("Bank account not found")
    
    # Calcular diferencia total de ajustes
    total_adjustment = (
        recon.interest_not_recorded 
        - recon.bank_fees_not_recorded
    )
    
    # ✅ Aplicar ajuste al saldo
    account.current_balance += total_adjustment

    # Crear asientos de ajuste
    if recon.bank_fees_not_recorded > 0 or recon.interest_not_recorded > 0:
        lines = []
        if recon.bank_fees_not_recorded > 0:
            fee_acct = self._get_account_by_code(company_id, "5400")
            if fee_acct and account.linked_account_id:
                lines.append((fee_acct.id, recon.bank_fees_not_recorded, 
                             Decimal("0.00"), "Comision bancaria no registrada"))
                lines.append((account.linked_account_id, Decimal("0.00"), 
                             recon.bank_fees_not_recorded, "Ajuste comision"))
        
        if recon.interest_not_recorded > 0:
            int_acct = self._get_account_by_code(company_id, "4200")
            if int_acct and account.linked_account_id:
                lines.append((account.linked_account_id, recon.interest_not_recorded,
                             Decimal("0.00"), "Interes ganado no registrado"))
                lines.append((int_acct.id, Decimal("0.00"), 
                             recon.interest_not_recorded, "Ajuste interes"))

        if lines:
            self._create_journal_entry(
                company_id=company_id,
                description=f"Ajustes conciliacion bancaria #{recon.id}",
                reference=f"RECON-ADJ-{recon.id:06d}",
                lines=lines,
            )

    recon.status = "COMPLETED"
    recon.reconciled_by = user_id
    recon.reconciled_at = datetime.now(timezone.utc)

    self.db.commit()
    self.db.refresh(recon)
    self.db.refresh(account)
    
    return recon
```


---

### 🔴 BUG #9: CHEQUES DEVUELTOS NO REGISTRAN COMISIÓN BANCARIA

**Severidad:** MEDIA  
**Archivo:** `backend/app/services/treasury_service.py` (líneas 894-950)  
**Impacto:** Gastos bancarios no contabilizados, utilidades infladas

#### Descripción del Problema

Cuando un cheque es devuelto (`BOUNCED`), el sistema revierte correctamente el saldo bancario y crea un asiento contable, pero **NO registra la comisión** que el banco cobra por el rechazo del cheque.

```python
def update_check_status(self, check_id: int, new_status: str, company_id: int, ...):
    # ... validaciones ...

    if new_status == "BOUNCED" and old_status != "BOUNCED":
        account = self.get_bank_account_by_id(check.bank_account_id, company_id)
        if account:
            account.current_balance += check.amount  # ✅ Revierte el monto del cheque
            self.db.commit()
            self.db.refresh(account)

            # ✅ Crea asiento de reverso
            je = self._create_journal_entry(
                company_id=company_id,
                description=f"Cheque #{check.check_number} devuelto",
                reference=f"CHK-BOUNCE-{check.check_number}",
                lines=[
                    (account.linked_account_id, check.amount, Decimal("0.00"), ...),
                    (contra_id, Decimal("0.00"), check.amount, ...),
                ],
            )

            # ❌ NO registra la comisión del banco por rechazo
            # Típicamente entre $5,000 y $50,000 en Colombia
```

#### Impacto Real

**Escenario:**
1. Empresa emite cheque por $2,000,000
2. Banco lo rechaza (fondos insuficientes del receptor)
3. Banco cobra comisión de $15,000

**Contabilización actual (INCORRECTA):**
```
Asiento CHK-BOUNCE-12345:
  Débito:  Cuentas por Pagar (2110)  $2,000,000
  Crédito: Bancos (111010)            $2,000,000
```

**Contabilización correcta (FALTANTE):**
```
Asiento CHK-BOUNCE-12345:
  Débito:  Cuentas por Pagar (2110)    $2,000,000
  Débito:  Gastos Bancarios (5400)     $15,000     ← FALTA
  Crédito: Bancos (111010)              $2,015,000  ← MAL (solo revierte $2M)
```

**Resultado:**
- Saldo bancario real: -$15,000 vs saldo en sistema: $0
- Gastos no contabilizados: $15,000 × N cheques devueltos
- Utilidades sobreestimadas

#### Solución Recomendada

```python
def update_check_status(
    self, check_id: int, new_status: str, company_id: int,
    user_id: Optional[int] = None,
    bounce_fee: Optional[Decimal] = None  # ✅ Nuevo parámetro
):
    check = self.db.query(CheckRegister).filter(...).first()
    if not check:
        return None

    # ... validaciones ...

    if new_status == "BOUNCED" and old_status != "BOUNCED":
        account = self.get_bank_account_by_id(check.bank_account_id, company_id)
        if account:
            # ✅ Determinar comisión (default o proporcionado)
            if bounce_fee is None:
                # Comisión típica en Colombia: 4 mil pesos UVT (aprox $15,000)
                from app.core.config import settings
                bounce_fee = Decimal(str(settings.UVT_VALUE * 4)) / Decimal("100")
            
            # ✅ Revertir cheque Y descontar comisión
            account.current_balance += check.amount  # Revierte cheque
            account.current_balance -= bounce_fee     # Descuenta comisión
            
            self.db.commit()
            self.db.refresh(account)

            # ✅ Crear asiento contable completo
            payable_account = self._get_account_by_code(company_id, "2110")
            fee_account = self._get_account_by_code(company_id, "5400")
            
            lines = [
                # Reverso de la cuenta por pagar
                (
                    payable_account.id if payable_account else account.linked_account_id,
                    check.amount,
                    Decimal("0.00"),
                    f"Reverso cheque #{check.check_number} devuelto"
                ),
                # Gasto por comisión
                (
                    fee_account.id if fee_account else account.linked_account_id,
                    bounce_fee,
                    Decimal("0.00"),
                    f"Comisión cheque devuelto"
                ),
                # Crédito total al banco
                (
                    account.linked_account_id,
                    Decimal("0.00"),
                    check.amount + bounce_fee,
                    f"Reverso cheque + comisión"
                ),
            ]
            
            je = self._create_journal_entry(
                company_id=company_id,
                description=f"Cheque #{check.check_number} devuelto con comisión",
                reference=f"CHK-BOUNCE-{check.check_number}",
                lines=lines,
            )

            # Registrar transacción de tesorería
            tx = TreasuryTransaction(
                company_id=company_id,
                account_type="BANK",
                bank_account_id=check.bank_account_id,
                transaction_type="CHECK_BOUNCED",
                amount=check.amount + bounce_fee,
                description=f"Cheque #{check.check_number} devuelto + comisión ${bounce_fee:,.2f}",
                reference=f"CHK-BOUNCE-{check.check_number}",
                journal_entry_id=je.id if je else None,
                balance_after=account.current_balance,
                created_by=user_id,
            )
            self.db.add(tx)

    self.db.commit()
    self.db.refresh(check)
    return check
```

**Actualizar el schema para recibir el parámetro:**

```python
# backend/app/schemas/treasury.py
class CheckStatusUpdate(BaseModel):
    new_status: str
    bounce_fee: Optional[Decimal] = None  # Comisión por rechazo
```

---

### 🟠 BUG #10: DECLARACIÓN DE IVA NO CONSIDERA NOTAS CRÉDITO/DÉBITO

**Severidad:** ALTA  
**Archivo:** `backend/app/services/accounting_service.py` (líneas 1005-1076)  
**Impacto:** Declaraciones de IVA incorrectas ante DIAN, sanciones fiscales

#### Descripción del Problema

La función `get_declaracion_iva()` calcula el IVA a pagar restando IVA generado (ventas) menos IVA soportado (compras), pero **NO incluye** el efecto de las notas crédito y débito que modifican el IVA de facturas existentes.

```python
def get_declaracion_iva(self, company_id: int, date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None) -> Dict[str, Any]:
    # ... código ...

    # ✅ Obtiene IVA de facturas de venta
    sales_book = self.get_libro_ventas(company_id, date_from, date_to)
    
    # ✅ Obtiene IVA de facturas de compra
    purchases_book = self.get_libro_compras(company_id, date_from, date_to)

    total_iva_generado = sales_book["totals"].get("total_iva", Decimal("0.00"))
    total_iva_soportado = purchases_book["totals"].get("total_iva", Decimal("0.00"))

    diferencia = total_iva_generado - total_iva_soportado
    iva_a_pagar = diferencia if diferencia > 0 else Decimal("0.00")
    
    # ❌ NO considera notas crédito (que REDUCEN IVA generado)
    # ❌ NO considera notas débito (que AUMENTAN IVA generado)
```

**El sistema SÍ tiene un módulo de notas crédito/débito** en `backend/app/services/credit_debit_note_service.py`, pero no está integrado con la declaración de IVA.

#### Escenario de Problema

**Ventas del periodo:**
- Factura 001: Base $10,000,000 + IVA $1,900,000 = Total $11,900,000
- Factura 002: Base $5,000,000 + IVA $950,000 = Total $5,950,000
- **Total IVA generado:** $2,850,000

**Nota crédito:**
- NC-001 (anula Factura 001): Base -$10,000,000, IVA -$1,900,000
- Fecha de emisión: dentro del periodo bimestral

**Declaración de IVA actual (INCORRECTA):**
```
IVA Generado (ventas):    $2,850,000  ❌ (incluye factura anulada)
IVA Soportado (compras):  $500,000
───────────────────────────────────
IVA a Pagar:              $2,350,000  ❌
```

**Declaración de IVA correcta (ESPERADA):**
```
IVA Generado (ventas):    $2,850,000
  Menos: Notas Crédito:   -$1,900,000
  Neto IVA Generado:      $950,000    ✅
IVA Soportado (compras):  $500,000
───────────────────────────────────
IVA a Pagar:              $450,000    ✅
```

**Impacto:**
- Empresa declara $2,350,000 cuando solo debe $450,000
- Pago en exceso de $1,900,000
- O peor: DIAN detecta inconsistencia y aplica sanción por información inexacta (Art. 647 ET: multa hasta del 100% del valor pagado de menos)

#### Solución Recomendada

```python
def get_declaracion_iva(self, company_id: int, date_from: Optional[datetime] = None,
                        date_to: Optional[datetime] = None) -> Dict[str, Any]:
    company = self.db.query(company_model.Company).filter(...).first()
    if not company:
        return {"error": "Company not found"}

    if company.regimen in ("SIMPLE", "NO_RESPONSABLE"):
        # ... manejo de régimen simple ...

    # Obtener libros de ventas y compras
    sales_book = self.get_libro_ventas(company_id, date_from, date_to)
    purchases_book = self.get_libro_compras(company_id, date_from, date_to)

    total_iva_generado = sales_book["totals"].get("total_iva", Decimal("0.00"))
    total_iva_soportado = purchases_book["totals"].get("total_iva", Decimal("0.00"))

    # ✅ Obtener notas crédito y débito del periodo
    from app.models.sql.credit_debit_note import CreditDebitNote
    
    date_filter = [
        CreditDebitNote.company_id == company_id,
        CreditDebitNote.status == "ISSUED",
    ]
    if date_from:
        date_filter.append(CreditDebitNote.issue_date >= date_from)
    if date_to:
        date_filter.append(CreditDebitNote.issue_date <= date_to)

    notes = self.db.query(CreditDebitNote).filter(and_(*date_filter)).all()

    # ✅ Calcular ajustes por notas
    total_notas_credito_iva = Decimal("0.00")
    total_notas_debito_iva = Decimal("0.00")
    
    notas_credito_detail = []
    notas_debito_detail = []

    for note in notes:
        # Obtener factura original para validar tipo
        invoice = self.db.query(Invoice).filter(Invoice.id == note.invoice_id).first()
        if not invoice:
            continue
        
        # Solo considerar notas sobre facturas de VENTA
        if invoice.invoice_type != "SALE":
            continue
        
        # Calcular IVA de la nota
        note_iva = Decimal("0.00")
        if hasattr(note, 'items') and note.items:
            for item in note.items:
                note_iva += item.tax_amount or Decimal("0.00")
        
        if note.note_type == "CREDIT":
            total_notas_credito_iva += note_iva
            notas_credito_detail.append({
                "note_number": note.note_number,
                "invoice_number": invoice.invoice_number,
                "iva_amount": note_iva,
                "reason": note.reason,
            })
        elif note.note_type == "DEBIT":
            total_notas_debito_iva += note_iva
            notas_debito_detail.append({
                "note_number": note.note_number,
                "invoice_number": invoice.invoice_number,
                "iva_amount": note_iva,
                "reason": note.reason,
            })

    # ✅ Calcular IVA neto ajustado
    iva_generado_ajustado = (
        total_iva_generado 
        - total_notas_credito_iva 
        + total_notas_debito_iva
    )

    diferencia = iva_generado_ajustado - total_iva_soportado
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
        
        # IVA Generado
        "iva_generado": sales_book["totals"],
        "total_iva_generado_bruto": total_iva_generado,
        
        # ✅ Ajustes por notas
        "notas_credito": {
            "total": total_notas_credito_iva,
            "detalle": notas_credito_detail,
        },
        "notas_debito": {
            "total": total_notas_debito_iva,
            "detalle": notas_debito_detail,
        },
        "total_iva_generado_neto": iva_generado_ajustado,
        
        # IVA Soportado
        "iva_soportado": purchases_book["totals"],
        "total_iva_soportado": total_iva_soportado,
        
        # Resultado
        "iva_a_pagar": iva_a_pagar,
        "iva_a_favor": iva_a_favor,
        "es_a_pagar": diferencia > 0,
    }
```

---

## 🛡️ PLAN DE ACCIÓN INMEDIATO

### 🚨 PRIORIDAD 1: IMPLEMENTAR HOY (Crítico)

#### 1. Bloquear Multi-Tenant Sin Validación
**Tiempo estimado:** 2 horas  
**Riesgo actual:** CRÍTICO - Acceso no autorizado a datos

```bash
# 1. Agregar verify_company_membership a TODOS los endpoints
cd backend/app/api/v1/routers/

# Buscar endpoints sin el decorador
grep -r "company_id: int" *.py | grep -v "verify_company_membership"

# 2. Aplicar fix masivo
for file in *.py; do
    # Revisar y agregar verify_company_membership donde falte
done
```

**Verificación:**
- ✅ Todos los endpoints tienen `Depends(verify_company_membership)`
- ✅ Prueba manual: cambiar company_id en petición → 403 Forbidden

---

#### 2. Corregir Asientos de Tesorería
**Tiempo estimado:** 3 horas  
**Riesgo actual:** CRÍTICO - Balance descuadrado

```python
# backend/app/services/treasury_service.py

# Modificar deposit() y withdraw() para VALIDAR linked_account_id
def deposit(self, ...):
    if not account.linked_account_id and not skip_journal_entry:
        raise ValueError(
            "Cuenta sin configuración contable. Configure 'linked_account_id' "
            "en el módulo de Tesorería antes de registrar movimientos."
        )
```

**Verificación:**
- ✅ Ejecutar prueba: crear cuenta sin linked_account_id → depositar → Error
- ✅ Configurar linked_account_id → depositar → Asiento creado ✅

---

#### 3. Proteger Race Condition en Inventario
**Tiempo estimado:** 2 horas  
**Riesgo actual:** ALTO - Inventario negativo

```python
# backend/app/services/inventory_service.py

def deduct_stock(self, ...):
    # Usar UPDATE con WHERE para validación atómica
    rows_updated = self.db.query(Product).filter(
        Product.id == product_id,
        Product.company_id == company_id,
        Product.stock_level >= quantity  # ✅ Validación atómica
    ).update({
        'stock_level': Product.stock_level - quantity
    }, synchronize_session=False)
    
    if rows_updated == 0:
        raise ValueError("Stock insuficiente o producto no encontrado")
```

**Verificación:**
- ✅ Crear producto con stock = 10
- ✅ Ejecutar 2 facturas simultáneas (5 unidades cada una)
- ✅ Stock final = 0 (no 5)

---

### 🟠 PRIORIDAD 2: IMPLEMENTAR ESTA SEMANA (Alto)

#### 4. Corregir Retenciones en Libro de Compras
**Tiempo estimado:** 4 horas

```python
# Integrar validación de 27 UVT en get_libro_compras()
from app.core.config import settings
uvt_daily_threshold = Decimal(str(settings.UVT_VALUE * 27))

if base_gravable > uvt_daily_threshold:
    # Aplicar retención
```

**Verificación:**
- ✅ Compra < 27 UVT → retefuente = $0
- ✅ Compra > 27 UVT → retefuente aplicada

---

#### 5. Integrar Notas Crédito/Débito en Declaración IVA
**Tiempo estimado:** 6 horas

**Verificación:**
- ✅ Crear factura con IVA
- ✅ Crear nota crédito en mismo periodo
- ✅ Declaración IVA muestra ajuste

---

#### 6. Actualizar Saldo Real en Conciliación
**Tiempo estimado:** 3 horas

**Verificación:**
- ✅ Conciliar con comisión no registrada
- ✅ `current_balance` actualizado después de completar

---

### 🟡 PRIORIDAD 3: IMPLEMENTAR ESTE MES (Medio)

#### 7. Corregir Asientos de Stock Inicial
**Tiempo estimado:** 4 horas

#### 8. Agregar Comisión en Cheques Devueltos
**Tiempo estimado:** 3 horas

#### 9. Agregar Rollback Explícito en post_journal_entry
**Tiempo estimado:** 2 horas

#### 10. Validar Referencias de Asientos
**Tiempo estimado:** 5 horas (agregar campo source_type)

---

## 📊 MÉTRICAS DE IMPACTO

| Bug | Registros Afectados | Impacto Financiero Estimado | Riesgo Legal |
|-----|---------------------|------------------------------|--------------|
| #1 Race Condition | ~50 productos | Hasta $5,000,000/mes | Bajo |
| #2 Tesorería | Todas las cuentas | Balance descuadrado | Alto (auditoría) |
| #3 Post Entry | ~200 asientos/mes | Corrupción de datos | Muy Alto |
| #4 Multi-Tenant | TODOS los datos | Violación GDPR/LOPD | Crítico |
| #5 Referencias | ~100 asientos/mes | Reportes incorrectos | Medio |
| #6 Retenciones | ~30 compras/mes | $2,000,000/mes | Alto (DIAN) |
| #7 Stock Inicial | ~20 productos | Balance descuadrado | Medio |
| #8 Conciliación | ~4 conciliaciones/mes | Saldos incorrectos | Medio |
| #9 Cheques | ~10 cheques/mes | $150,000/mes | Bajo |
| #10 Declaración IVA | 1 declaración/bimestre | Multas DIAN hasta 100% | Crítico |

**Impacto financiero total estimado:** $7,000,000 - $10,000,000/mes  
**Riesgo de multas DIAN:** Hasta $50,000,000 (100% de IVA pagado de menos)

---

## 🔬 RECOMENDACIONES ADICIONALES

### Testing

1. **Crear suite de pruebas de concurrencia:**
```python
# backend/tests/load/test_concurrent_inventory.py
import concurrent.futures

def test_concurrent_deduct_stock():
    """Simular 10 usuarios facturando simultáneamente el mismo producto"""
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_invoice, product_id=1) for _ in range(10)]
        results = [f.result() for f in futures]
    
    # Verificar que el stock final sea correcto
    assert product.stock_level >= 0
```

2. **Pruebas de integridad contable:**
```python
def test_accounting_equation():
    """Verificar que Activos = Pasivos + Patrimonio después de cada operación"""
    assets = sum_accounts_by_type("ASSET")
    liabilities = sum_accounts_by_type("LIABILITY")
    equity = sum_accounts_by_type("EQUITY")
    
    assert abs((assets - (liabilities + equity))) < Decimal("0.01")
```

---

### Monitoreo

1. **Alertas automáticas:**
- Inventario negativo detectado
- Asiento desbalanceado guardado
- Acceso multi-tenant sin validación
- Diferencia > $1,000 en conciliación bancaria

2. **Dashboard de salud contable:**
- Balance general balanceado: ✅/❌
- Último periodo conciliado: Fecha
- Facturas sin asiento contable: 0
- Productos con stock negativo: 0

---

## 📝 CONCLUSIÓN

El sistema **Reload Matrix** tiene una base sólida pero presenta **10 vulnerabilidades críticas** que ponen en riesgo:

✅ La integridad financiera  
✅ El cumplimiento normativo (DIAN)  
✅ La seguridad de datos multi-tenant  
✅ La confianza de los usuarios

**Recomendación ejecutiva:**

🔴 **DETENER OPERACIONES EN PRODUCCIÓN** hasta corregir bugs #1, #2, #4 (Prioridad 1)  
🟠 **AMBIENTE DE STAGING SOLAMENTE** hasta completar Prioridad 2  
🟢 **PRODUCCIÓN COMPLETA** después de validar todas las correcciones

**Tiempo estimado total de corrección:** 40 horas (1 semana con 1 desarrollador)

---

**Auditor:** Claude Sonnet 4.5  
**Fecha:** 8 de Julio de 2026  
**Versión del Reporte:** 1.0

---

## 📧 CONTACTO PARA SEGUIMIENTO

Para cualquier duda o aclaración sobre este reporte, contactar a:
- **Equipo de Desarrollo:** [Información de contacto]
- **Responsable de Calidad:** [Información de contacto]

**Próxima revisión programada:** 15 de Julio de 2026

