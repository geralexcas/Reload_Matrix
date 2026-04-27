# ENDPOINTS FALTANTES - Sistema de Gestión Empresarial

## Introducción

Durante las pruebas exhaustivas del sistema, se identificaron 3 endpoints críticos que no están implementados en la API actual. Estos endpoints son esenciales para completar la funcionalidad del sistema, especialmente en el módulo contable, y para cumplir con requisitos básicos de gestión financiera y auditoría.

## Endpoints Faltantes

### 1. Obtener Información del Usuario Autenticado

**Endpoint**: `GET /api/v1/users/me`

**Estado**: ❌ No implementado

**Propósito**: 
Retornar la información del usuario actualmente autenticado, incluyendo sus datos personales, rol y permisos.

**Importancia**: ⭐⭐⭐⭐⭐ (Crítica)

**Justificación**:
- **Experiencia de usuario**: Las aplicaciones frontend necesitan mostrar información del usuario logrado (nombre, email, rol)
- **Control de acceso**: Permite a la interfaz adaptarse según los permisos del usuario
- **Auditoría**: Registra qué usuario está realizando operaciones
- **Estándar de API**: La mayoría de sistemas modernos incluyen este endpoint

**Respuesta esperada**:
```json
{
  "id": 123,
  "username": "usuario_ejemplo",
  "email": "usuario@empresa.com",
  "full_name": "Nombre Completo",
  "role": "VENDEDOR",
  "is_active": true,
  "company_id": 1,
  "permissions": ["create_invoice", "view_reports"],
  "created_at": "2026-01-15T10:30:00Z",
  "last_login": "2026-04-17T14:25:00Z"
}
```

**Impacto de no implementar**:
- Las interfaces de usuario no pueden mostrar información básica del usuario
- Dificulta la personalización según roles y permisos
- Requiere soluciones alternativas (almacenamiento local, cache) que pueden desincronizarse

---

### 2. Obtener Líneas Detalladas de Asientos Contables

**Endpoint**: `GET /api/v1/accounting/journal-entries/{entry_id}/lines`

**Estado**: ❌ No implementado

**Propósito**:
Retornar el detalle completo de las líneas que componen un asiento contable específico, incluyendo las cuentas afectadas, montos de débito/crédito y descripciones.

**Importancia**: ⭐⭐⭐⭐⭐ (Crítica para contabilidad)

**Justificación**:
- **Auditoría contable**: Permite verificar la exactitud de los asientos registrados
- **Cumplimiento legal**: Requerido para cumplir con normas contables y fiscales
- **Análisis financiero**: Esencial para entender el impacto de cada transacción
- **Corrección de errores**: Permite identificar y corregir asientos incorrectos

**Respuesta esperada**:
```json
{
  "entry_id": 123,
  "entry_date": "2026-04-15T00:00:00Z",
  "description": "Factura de compra #INV-00123",
  "reference": "INV-00123",
  "is_posted": true,
  "lines": [
    {
      "id": 456,
      "account_id": 5100,
      "account_code": "5100",
      "account_name": "Compras de mercancías",
      "debit_amount": 1000000.00,
      "credit_amount": 0.00,
      "description": "Compra de 10 unidades de Producto A"
    },
    {
      "id": 457,
      "account_id": 2205,
      "account_code": "2205",
      "account_name": "IVA por pagar",
      "debit_amount": 190000.00,
      "credit_amount": 0.00,
      "description": "IVA 19% sobre compra"
    },
    {
      "id": 458,
      "account_id": 2105,
      "account_code": "2105",
      "account_name": "Proveedores nacionales",
      "debit_amount": 0.00,
      "credit_amount": 1190000.00,
      "description": "Pago a Proveedor XYZ SA"
    }
  ],
  "total_debit": 1190000.00,
  "total_credit": 1190000.00,
  "is_balanced": true
}
```

**Impacto de no implementar**:
- **Imposibilidad de auditoría**: No se puede verificar el detalle de los asientos
- **Incumplimiento contable**: Dificulta cumplir con normas como NIIF o estándares locales
- **Dificultad para corregir errores**: Sin visibilidad del detalle, es difícil identificar problemas
- **Limitaciones de reporting**: Imposible generar reportes financieros detallados

---

### 3. Generar Balance de Prueba

**Endpoint**: `GET /api/v1/accounting/trial-balance`

**Estado**: ❌ No implementado

**Propósito**:
Generar un balance de prueba que muestre los saldos de todas las cuentas contables, verificando que la suma de débitos iguale a la suma de créditos.

**Importancia**: ⭐⭐⭐⭐⭐ (Crítica para cierre contable)

**Justificación**:
- **Verificación de integridad**: Confirma que los libros contables están balanceados
- **Cierre de período**: Esencial para cerrar meses o años fiscales
- **Reportes financieros**: Base para generar estados financieros (balance general, estado de resultados)
- **Detección de errores**: Identifica desequilibrios que indican problemas contables
- **Cumplimiento legal**: Requerido por autoridades fiscales y auditores

**Parámetros opcionales**:
- `date_from`: Fecha de inicio del período
- `date_to`: Fecha de fin del período
- `account_type`: Filtrar por tipo de cuenta (ASSET, LIABILITY, etc.)

**Respuesta esperada**:
```json
{
  "company_id": 1,
  "period": "2026-04",
  "generated_at": "2026-04-17T15:30:00Z",
  "accounts": [
    {
      "account_id": 111001,
      "account_code": "111001",
      "account_name": "Caja principal",
      "account_type": "ASSET",
      "debit_balance": 5000000.00,
      "credit_balance": 0.00,
      "net_balance": 5000000.00
    },
    {
      "account_id": 2105,
      "account_code": "2105",
      "account_name": "Proveedores nacionales",
      "account_type": "LIABILITY",
      "debit_balance": 0.00,
      "credit_balance": 3000000.00,
      "net_balance": -3000000.00
    },
    {
      "account_id": 4100,
      "account_code": "4100",
      "account_name": "Ingresos por ventas",
      "account_type": "REVENUE",
      "debit_balance": 0.00,
      "credit_balance": 8000000.00,
      "net_balance": -8000000.00
    }
  ],
  "total_debit_balance": 12000000.00,
  "total_credit_balance": 12000000.00,
  "is_balanced": true,
  "difference": 0.00
}
```

**Impacto de no implementar**:
- **Imposibilidad de cierre contable**: No se pueden cerrar períodos financieros
- **Falta de cumplimiento**: Incumplimiento de obligaciones legales y fiscales
- **Dificultad en auditorías**: Los auditores no pueden verificar la integridad de los libros
- **Toma de decisiones limitada**: La gerencia no tiene visibilidad del estado financiero real
- **Riesgo de errores no detectados**: Desbalanceos contables pueden pasar desapercibidos

---

## Impacto Global de No Implementar Estos Endpoints

### 📉 Riesgos para el Negocio

1. **Incumplimiento Legal**:
   - Posibles sanciones por no cumplir con requisitos contables y fiscales
   - Dificultad para presentar declaraciones de impuestos
   - Problemas en auditorías externas

2. **Pérdida de Integridad de Datos**:
   - Imposibilidad de verificar la exactitud de la información financiera
   - Riesgo de errores contables no detectados
   - Dificultad para reconciliar cuentas

3. **Limitaciones Operativas**:
   - La interfaz de usuario no puede mostrar información básica
   - Los contadores no pueden realizar su trabajo eficientemente
   - Dificultad para generar reportes gerenciales

4. **Riesgo Reputacional**:
   - Percepción de sistema incompleto o poco profesional
   - Dificultad para obtener certificaciones de calidad
   - Posible pérdida de clientes por falta de funcionalidad esencial

### 💡 Beneficios de Implementar Estos Endpoints

1. **Cumplimiento Total**:
   - Cumplir con todas las normas contables y fiscales aplicables
   - Facilitar auditorías internas y externas
   - Generar reportes financieros completos

2. **Integridad de Datos**:
   - Verificación automática de la consistencia contable
   - Detección temprana de errores
   - Reconciliación fácil de cuentas

3. **Experiencia de Usuario Mejorada**:
   - Interfaz completa con información de usuario
   - Visibilidad total de operaciones contables
   - Herramientas completas para contadores y auditores

4. **Toma de Decisiones Informada**:
   - Acceso a información financiera en tiempo real
   - Generación de estados financieros precisos
   - Análisis de tendencias y desempeño

---

## Recomendaciones para Implementación

### 📅 Priorización

1. **Alta Prioridad (Inmediata)**:
   - `GET /api/v1/accounting/trial-balance` (para cierre de período actual)
   - `GET /api/v1/accounting/journal-entries/{id}/lines` (para auditoría)

2. **Media Prioridad (Próximo sprint)**:
   - `GET /api/v1/users/me` (para mejorar experiencia de usuario)

### 👨‍💻 Consideraciones Técnicas

1. **Seguridad**:
   - Asegurar que solo usuarios autorizados puedan acceder a información contable
   - Implementar permisos basados en roles
   - Validar que los usuarios solo puedan ver datos de su compañía

2. **Rendimiento**:
   - Optimizar consultas para el trial balance (puede ser intensivo)
   - Implementar caching para datos que no cambian frecuentemente
   - Considerar paginación para listas grandes de líneas contables

3. **Documentación**:
   - Documentar claramente los parámetros y respuestas
   - Proporcionar ejemplos de uso
   - Especificar códigos de error posibles

4. **Pruebas**:
   - Crear pruebas unitarias y de integración
   - Verificar que los cálculos sean precisos
   - Asegurar que el balance de prueba siempre esté equilibrado

### 📋 Ejemplo de Implementación (Pseudocódigo)

```python
# En el router de accounting (app/api/v1/routers/accounting.py)

@router.get("/journal-entries/{entry_id}/lines", 
           response_model=List[schemas.JournalEntryLineResponse])
async def get_journal_entry_lines(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get detailed lines for a specific journal entry"""
    
    # Verificar que el asiento existe y pertenece a la compañía del usuario
    entry = db.query(models.JournalEntry).filter(
        models.JournalEntry.id == entry_id,
        models.JournalEntry.company_id == current_user.company_id
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=404, 
            detail="Journal entry not found or not accessible"
        )
    
    # Retornar las líneas con información de las cuentas
    return [
        {
            "id": line.id,
            "account_id": line.account_id,
            "account_code": line.account.code,
            "account_name": line.account.name,
            "debit_amount": float(line.debit_amount),
            "credit_amount": float(line.credit_amount),
            "description": line.description
        }
        for line in entry.lines
    ]

@router.get("/trial-balance", response_model=schemas.TrialBalanceResponse)
async def get_trial_balance(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate trial balance for the company"""
    
    # Obtener todas las cuentas de la compañía
    accounts = db.query(models.ChartOfAccounts).filter(
        models.ChartOfAccounts.company_id == current_user.company_id
    ).all()
    
    balance = []
    total_debit = 0.0
    total_credit = 0.0
    
    for account in accounts:
        # Calcular saldos para el período especificado
        debit_balance = calculate_account_debit_balance(
            db, account.id, date_from, date_to
        )
        credit_balance = calculate_account_credit_balance(
            db, account.id, date_from, date_to
        )
        
        balance.append({
            "account_id": account.id,
            "account_code": account.code,
            "account_name": account.name,
            "account_type": account.account_type,
            "debit_balance": debit_balance,
            "credit_balance": credit_balance,
            "net_balance": debit_balance - credit_balance
        })
        
        total_debit += debit_balance
        total_credit += credit_balance
    
    return {
        "company_id": current_user.company_id,
        "period": f"{date_from or 'Inicio'} - {date_to or 'Hoy'}",
        "generated_at": datetime.utcnow(),
        "accounts": balance,
        "total_debit_balance": total_debit,
        "total_credit_balance": total_credit,
        "is_balanced": abs(total_debit - total_credit) < 0.01,
        "difference": total_debit - total_credit
    }

@router.get("/users/me", response_model=schemas.UserResponse)
async def get_current_user_info(
    current_user: models.User = Depends(get_current_user)
):
    """Get information about the currently authenticated user"""
    
    # Retornar información del usuario con sus permisos
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "company_id": current_user.company_id,
        "permissions": [perm.name for perm in current_user.permissions],
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }
```

---

## Conclusión

La implementación de estos 3 endpoints es **crítica** para completar la funcionalidad del sistema de gestión empresarial. Sin ellos, el sistema no puede:

1. ✅ Cumplir con requisitos legales y contables
2. ✅ Proporcionar visibilidad completa de las operaciones financieras
3. ✅ Permitir auditorías y verificaciones de integridad
4. ✅ Generar reportes financieros esenciales
5. ✅ Ofrecer una experiencia de usuario completa

**Recomendación final**: Priorizar la implementación de estos endpoints en el próximo ciclo de desarrollo, comenzando con los endpoints contables (`trial-balance` y `journal-entries/{id}/lines`) que son esenciales para el cierre del período contable actual.

---

*Documento generado por Mistral Vibe - Análisis de API*
*Fecha: 17 de Abril de 2026*
*Prioridad: ALTA 🚨*