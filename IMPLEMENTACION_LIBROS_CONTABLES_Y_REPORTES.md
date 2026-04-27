# Implementación Libros Contables y Reportes Tributarios — 31 Marzo 2026

## Resumen

Se implementaron los **libros contables automáticos** y **reportes para declaraciones tributarias** requeridos por la normativa colombiana, cubriendo los items 6 y 7 del archivo `contunuacion 31 marzo.md`.

---

## 1. Libros Contables Automáticos

### 1.1 Libro Mayor

**Backend:**
- `AccountingService.get_libro_mayor()` — Genera el Libro Mayor generalizado con saldos por cuenta contable
- Calcula saldo inicial (período anterior), débitos, créditos y saldo final
- Respeta naturaleza de cuentas (deudora: Activo/Gasto, acreedora: Pasivo/Patrimonio/Ingreso)
- Filtro por rango de fechas y código de cuenta específico
- Solo incluye asientos publicados (`is_posted=True`)

**Frontend:**
- Vista `LibroMayorView.vue` — Tabla expandible por cuenta con movimientos detallados
- Filtros: fecha desde/hasta, código de cuenta
- Indicador de cuadre (débitos = créditos)
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/libro-mayor/`

### 1.2 Libro de Ventas

**Backend:**
- `AccountingService.get_libro_ventas()` — Registra todas las facturas de venta con desglose de IVA
- Clasifica por tarifa: IVA 19%, IVA 5%, sin IVA
- Calcula retenciones (Retefuente 2.5%, ReteIVA 15%) para agentes retenedores
- Totales acumulados por concepto

**Frontend:**
- Vista `LibroVentasView.vue` — Tabla con todas las facturas de venta
- Columnas: Fecha, N° Factura, NIT, Razón Social, Base IVA 19%, IVA 19%, Base IVA 5%, IVA 5%, Sin IVA, Total IVA, Retefuente, ReteIVA, Total, Estado DIAN
- Fila de totales acumulados
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/libro-ventas/`

### 1.3 Libro de Compras

**Backend:**
- `AccountingService.get_libro_compras()` — Registra todas las facturas de compra con IVA soportado
- Misma estructura que Libro de Ventas pero para compras
- Aplica retenciones solo para regímenes Común y Especial

**Frontend:**
- Vista `LibroComprasView.vue` — Tabla con todas las facturas de compra
- Mismas columnas que Libro de Ventas
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/libro-compras/`

---

## 2. Reportes para Declaraciones Tributarias

### 2.1 Declaración de IVA

**Backend:**
- `AccountingService.get_declaracion_iva()` — Genera declaración según Formulario 300 DIAN
- IVA generado (ventas) menos IVA soportado (compras) = IVA a pagar o a favor
- Excluye automáticamente Régimen Simple (no declara IVA por separado)
- Desglose por tarifa (19% y 5%)

**Frontend:**
- Vista `DeclaracionIVAView.vue` — Dos columnas (IVA Generado vs IVA Soportado)
- Resultado destacado: "IVA a Pagar" (amarillo) o "IVA a Favor" (verde)
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/declaracion-iva/`

### 2.2 Reporte de Retenciones

**Backend:**
- `AccountingService.get_reporte_retenciones()` — Detalle de todas las retenciones aplicadas
- Retefuente: 2.5% sobre base gravable de compras (servicios)
- ReteIVA: 15% sobre el IVA de compras
- Detecta agentes retenedores en facturas de venta
- Totales separados por tipo de retención

**Frontend:**
- Vista `ReporteRetencionesView.vue` — Tabla detallada por factura
- Columnas: Fecha, N° Factura, Tipo (Venta/Compra), NIT, Nombre, Concepto, Base, Tarifa, Valor
- Totales: Retefuente, ReteIVA, Total Retenciones
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/reporte-retenciones/`

### 2.3 Reporte de Ingresos

**Backend:**
- `AccountingService.get_reporte_ingresos()` — Clasificación de ingresos para declaración de renta
- Ingresos operacionales vs no operacionales
- Separa devoluciones y anulaciones (facturas CANCELLED)
- Calcula ingresos netos (operacionales - devoluciones)

**Frontend:**
- Vista `ReporteIngresosView.vue` — Tarjetas resumen + tabla detallada
- Tarjetas: Ingresos Operacionales, IVA Generado, Devoluciones, Ingresos Netos
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/reporte-ingresos/`

### 2.4 Reporte de Patrimonio

**Backend:**
- `AccountingService.get_reporte_patrimonio()` — Balance patrimonial al corte
- Basado en saldos del Libro Mayor (Activos - Pasivos = Patrimonio)
- Fecha de corte configurable
- Detalle por cuenta contable

**Frontend:**
- Vista `ReportePatrimonioView.vue` — Dos columnas (Activos / Pasivos) + ecuación patrimonial
- Visualización: `Activos - Pasivos = Patrimonio`
- Exportación CSV

**Endpoint:** `GET /api/v1/accounting/reporte-patrimonio/`

---

## 3. Archivos Modificados

### Backend

| Archivo | Cambios |
|---|---|
| `backend/app/schemas/accounting.py` | +120 líneas: Schemas para MayorResponse, SalesBookResponse, PurchaseBookResponse, IVADeclarationResponse, RetencionesResponse, IngresosResponse, PatrimonioResponse |
| `backend/app/services/accounting_service.py` | +450 líneas: 7 métodos nuevos (get_libro_mayor, get_libro_ventas, get_libro_compras, get_declaracion_iva, get_reporte_retenciones, get_reporte_ingresos, get_reporte_patrimonio) + helpers (_parse_tax_rate, _is_approx_equal, _get_invoice_tax_breakdown, _format_period) |
| `backend/app/api/v1/routers/accounting.py` | +120 líneas: 7 nuevos endpoints GET |

### Frontend

| Archivo | Cambios |
|---|---|
| `frontend/src/views/Accounting/LibroMayorView.vue` | **Nuevo** — Vista del Libro Mayor con tabla expandible |
| `frontend/src/views/Accounting/LibroVentasView.vue` | **Nuevo** — Vista del Libro de Ventas |
| `frontend/src/views/Accounting/LibroComprasView.vue` | **Nuevo** — Vista del Libro de Compras |
| `frontend/src/views/Accounting/DeclaracionIVAView.vue` | **Nuevo** — Vista de Declaración de IVA |
| `frontend/src/views/Accounting/ReporteRetencionesView.vue` | **Nuevo** — Vista de Retenciones |
| `frontend/src/views/Accounting/ReporteIngresosView.vue` | **Nuevo** — Vista de Ingresos |
| `frontend/src/views/Accounting/ReportePatrimonioView.vue` | **Nuevo** — Vista de Patrimonio |
| `frontend/src/views/Accounting/IndexView.vue` | Actualizado: 3 nuevas tarjetas (Libro Mayor, Ventas, Compras) |
| `frontend/src/router/index.js` | +24 líneas: 7 nuevas rutas |
| `frontend/src/components/layout/SidebarNav.vue` | Actualizado: 7 nuevos items de navegación con sección "Reportes Tributarios" |
| `frontend/src/components/layout/DashboardLayout.vue` | Actualizado: 7 nuevos títulos de página |

---

## 4. Normativa Colombiana Aplicada

| Norma | Aplicación |
|---|---|
| **Decreto 2420/2015** | Libro Mayor con saldos por cuenta, movimientos cronológicos |
| **Art. 1.6.1.4.10 ET** | Libros de Ventas y Compras con campos obligatorios DIAN |
| **Art. 437, 468, 486 ET** | Declaración de IVA (generado vs soportado) |
| **Art. 368 ET** | Retención en la fuente sobre servicios (2.5%) |
| **Art. 401 ET** | Retención en el IVA (15%) |
| **Art. 287, 631 ET** | Clasificación de ingresos operacionales |
| **Art. 374 ET** | Reporte de patrimonio (impuesto al patrimonio) |
| **Resolución 000042/2020 DIAN** | Campos obligatorios en libros (NIT, razón social, bases IVA) |

### Tarifas IVA Soportadas

| Tarifa | Tipo | Uso |
|---|---|---|
| 19% | General | Bienes y servicios gravados |
| 5% | Reducida | Servicios públicos, ciertos alimentos |
| 0% | Exento | Exportaciones, ciertos productos |
| Excluido | No gravado | Servicios excluidos |

### Regímenes Tributarios

| Régimen | IVA Discriminado | Retenciones |
|---|---|---|
| Común | Sí (19%, 5%) | Sí |
| Especial | Sí (19%, 5%) | Sí |
| Simple | No (incluido en total) | No aplica |

---

## 5. Estructura de Navegación

```
Contabilidad
├── Plan de Cuentas
├── Asientos Contables
├── Libro Mayor              ← NUEVO
├── Libro de Ventas          ← NUEVO
├── Libro de Compras         ← NUEVO
└── Reportes Tributarios     ← NUEVO (sección)
    ├── Declaración IVA      ← NUEVO
    ├── Retenciones          ← NUEVO
    ├── Ingresos             ← NUEVO
    └── Patrimonio           ← NUEVO
```

---

## 6. Observaciones y Mejoras Futuras

### Pendiente (Prioridad Media)
- **Retefuente bienes (10%)**: Actualmente solo 2.5% servicios. Falta distinguir bienes vs servicios
- **Umbral 27 UVT**: No se valida el umbral diario para retención en la fuente (Art. 368 ET)
- **Notas crédito/débito**: No implementadas (item 22 del archivo original)
- **Impuesto al patrimonio**: Solo reporte informativo, no calcula el impuesto (1% sobre >$5.000M)

### Pendiente (Prioridad Baja)
- **Grandes contribuyentes**: Tarifas especiales no implementadas
- **Estado de Resultados**: Mencionado en IndexView pero no implementado
- **Balance General**: Mencionado en IndexView pero no implementado
- **Formulario 350**: Declaración de renta no implementada
