# Guía de Inicio - Módulo Contable

**reload_Matrix** - Sistema de Gestión Comercial  
**Versión:** 1.0.0  
**Última actualización:** Abril 2025

---

## Tabla de Contenidos

1. [Requisitos Previos](#1-requisitos-previos)
2. [Configuración Inicial](#2-configuración-inicial)
3. [Plan de Cuentas](#3-plan-de-cuentas)
4. [Asientos Contables](#4-asientos-contables)
5. [Libros Contables](#5-libros-contables)
6. [Reportes Tributarios](#6-reportes-tributarios)
7. [Estados Financieros](#7-estados-financieros)
8. [Flujo de Trabajo Recomendado](#8-flujo-de-trabajo-recomendado)
9. [Roles y Permisos](#9-roles-y-permisos)
10. [Solución de Problemas](#10-solución-de-problemas)

---

## 1. Requisitos Previos

### Tecnología
- Docker y Docker Compose
- Navegador moderno (Chrome, Firefox, Edge)
- Acceso a `http://localhost:8081` (frontend) y `http://localhost:8001` (backend)

### Credenciales por defecto
| Campo | Valor |
|-------|-------|
| Usuario | `admin` |
| Email | `admin@reloadmatrix.com` |
| Contraseña | `Admin@123456` |

> ⚠️ **Importante:** Cambiar la contraseña antes de usar en producción.

---

## 2. Configuración Inicial

### Paso 1: Crear la Empresa

Antes de cualquier operación contable, debes registrar la empresa:

1. Inicia sesión como administrador
2. Ve a **Empresa** en el menú lateral
3. Completa los campos obligatorios:
   - **Nombre** de la empresa
   - **NIT** con dígito de verificación
   - **Representante legal**
   - **Dirección** y teléfono
   - **Régimen** (Común / Simple / Responsable de IVA)
   - **Fecha de inicio de actividades**
   - **Resolución de facturación**

### Paso 2: Configurar el Plan de Cuentas

El sistema incluye un plan de cuentas base basado en la normativa colombiana. Puedes:

1. Ir a **Contabilidad** → **Plan de Cuentas**
2. Verificar las cuentas existentes
3. Crear cuentas adicionales si es necesario

#### Estructura del Plan de Cuentas

| Código | Tipo | Descripción |
|--------|------|-------------|
| 1 | Activo | Recursos y derechos |
| 11 | Activo Corriente | Efectivo, bancos, clientes |
| 12 | Activo No Corriente | Propiedad, planta, equipo |
| 2 | Pasivo | Obligaciones y deudas |
| 21 | Pasivo Corriente | Proveedores, impuestos por pagar |
| 22 | Pasivo No Corriente | Deudas largo plazo |
| 3 | Patrimonio | Capital social, utilidades |
| 4 | Ingresos | Ventas, servicios, financieros |
| 5 | Gastos | Operacionales, administrativos |
| 6 | Costos | Costo de ventas, producción |

### Paso 3: Crear Usuarios con Roles

Ve a **Administración** → **Usuarios** y crea los usuarios necesarios:

| Rol | Descripción | Acceso |
|-----|-------------|--------|
| **ADMINISTRADOR** | Acceso total | Todos los módulos |
| **CONTADOR** | Gestión contable | Contabilidad, reportes |
| **FACTURADOR** | Facturación | Facturas, notas crédito/débito |
| **VENDEDOR** | Ventas | Clientes, facturación básica |
| **TECNICO** | Reparaciones | Módulo de reparaciones |
| **BODEGUERO** | Inventario | Productos, stock |

---

## 3. Plan de Cuentas

### Ver Cuentas Existentes

```
Contabilidad → Plan de Cuentas
```

### Crear una Nueva Cuenta

1. Click en **Crear Cuenta**
2. Completa:
   - **Código** (ej: `110505` - Caja menor)
   - **Nombre** de la cuenta
   - **Tipo** (Activo, Pasivo, Patrimonio, Ingreso, Gasto, Costo)
   - **Saldo Inicial** (si aplica)
   - **Cuenta Padre** (para cuentas jerárquicas)

### Reglas de Codificación

- **1 dígito:** Clase (1=Activo, 2=Pasivo, 3=Patrimonio, 4=Ingreso, 5=Gasto, 6=Costo)
- **2 dígitos:** Grupo
- **4 dígitos:** Cuenta
- **6 dígitos:** Subcuenta

---

## 4. Asientos Contables

### Crear un Asiento Contable

```
Contabilidad → Asientos Contables → Crear Asiento
```

#### Campos requeridos:

| Campo | Descripción |
|-------|-------------|
| **Fecha** | Fecha del asiento |
| **Descripción** | Concepto del asiento |
| **Líneas** | Movimientos debe/haber |

#### Reglas:

- ✅ El asiento debe estar **cuadrado** (Debe = Haber)
- ✅ Cada línea debe tener cuenta contable, descripción y monto
- ✅ Los montos en **Debe** son positivos
- ✅ Los montos en **Haber** son negativos o se registran como crédito

### Tipos de Asientos

| Tipo | Generación | Descripción |
|------|------------|-------------|
| **Manual** | Usuario | Asientos de ajuste, correcciones |
| **Automático** | Sistema | Al facturar, al pagar, al recibir |
| **Cierre** | Usuario | Cierre de período contable |

### Asientos Automáticos del Sistema

El sistema genera asientos automáticamente en:

| Evento | Débito | Crédito |
|--------|--------|---------|
| **Venta al contado** | Caja/Bancos | Ingresos por ventas |
| **Venta a crédito** | Cuentas por cobrar | Ingresos por ventas |
| **Compra de inventario** | Inventario | Proveedores/Caja |
| **Pago a proveedor** | Proveedores | Caja/Bancos |
| **Cobro a cliente** | Caja/Bancos | Cuentas por cobrar |
| **Reparación facturada** | Cuentas por cobrar | Ingresos por servicios |

---

## 5. Libros Contables

### 5.1 Libro Mayor

```
Contabilidad → Libro Mayor
```

Muestra el resumen de movimientos por cuenta contable:

- **Saldo Inicial** de cada cuenta
- **Débitos** del período
- **Créditos** del período
- **Saldo Final**

**Filtros disponibles:**
- Rango de fechas
- Cuenta específica
- Tipo de cuenta

### 5.2 Libro de Ventas

```
Contabilidad → Libro de Ventas
```

Registro de todas las facturas de venta emitidas:

| Columna | Descripción |
|---------|-------------|
| N° Factura | Número de la factura |
| Fecha | Fecha de emisión |
| Cliente | Nombre y NIT del cliente |
| Valor sin IVA | Base gravable |
| IVA | Impuesto sobre las ventas |
| Total | Valor total de la factura |
| Estado DIAN | Borrador / Enviado / Aceptado |

### 5.3 Libro de Compras

```
Contabilidad → Libro de Compras
```

Registro de todas las facturas de compra recibidas:

| Columna | Descripción |
|---------|-------------|
| N° Factura | Número de la factura |
| Fecha | Fecha de recepción |
| Proveedor | Nombre y NIT del proveedor |
| Valor sin IVA | Base gravable |
| IVA Soportado | Impuesto deducible |
| Total | Valor total de la compra |

---

## 6. Reportes Tributarios

### 6.1 Declaración de IVA

```
Contabilidad → Declaración IVA
```

Genera el reporte de IVA para declaración ante la DIAN:

| Concepto | Fórmula |
|----------|---------|
| **IVA Generado** | Suma de IVA en facturas de venta |
| **IVA Soportado** | Suma de IVA en facturas de compra |
| **IVA a Pagar** | IVA Generado - IVA Soportado |
| **Saldo a Favor** | Si IVA Soportado > IVA Generado |

**Filtros:**
- Período (mensual, bimestral, cuatrimestral)
- Fecha desde/hasta

### 6.2 Reporte de Retenciones

```
Contabilidad → Retenciones
```

Incluye:

| Tipo | Umbral | Tarifa |
|------|--------|--------|
| **Retefuente** | ≥ 27 UVT | 10% (bienes), 11% (servicios) |
| **Retefuente bienes** | Sin umbral | 10% |
| **ReteIVA** | Aplica | 15% del IVA |
| **ReteICA** | Según municipio | Variable |

### 6.3 Reporte de Ingresos

```
Contabilidad → Ingresos
```

Resumen de ingresos por período:

- Ingresos operacionales
- Ingresos no operacionales
- Total de ingresos
- Comparativo por período

### 6.4 Reporte de Patrimonio

```
Contabilidad → Patrimonio
```

Detalle del patrimonio:

- Capital social
- Utilidades del ejercicio
- Utilidades acumuladas
- Reservas legales
- Total patrimonio

---

## 7. Estados Financieros

### 7.1 Estado de Resultados

```
Contabilidad → Estado de Resultados
```

Muestra la rentabilidad del período:

```
INGRESOS
  Ingresos Operacionales
  Ingresos No Operacionales
  ───────────────────────
  Total Ingresos

COSTOS
  Costo de Ventas
  ───────────────────────
  Utilidad Bruta

GASTOS
  Gastos Operacionales
  Gastos Financieros
  ───────────────────────
  Total Gastos

  ═══════════════════════
  UTILIDAD NETA
```

**Filtros:**
- Fecha desde/hasta
- Exportar a CSV

### 7.2 Balance General

```
Contabilidad → Balance General
```

Muestra la situación financiera a una fecha de corte:

```
ACTIVOS
  Activos Corrientes
    Efectivo y equivalentes
    Cuentas por cobrar
    Inventarios
  Activos No Corrientes
    Propiedad, planta y equipo
  ───────────────────────
  Total Activos

PASIVOS
  Pasivos Corrientes
    Proveedores
    Impuestos por pagar
  Pasivos No Corrientes
    Deudas largo plazo
  ───────────────────────
  Total Pasivos

PATRIMONIO
  Capital social
  Utilidades
  ───────────────────────
  Total Patrimonio

  ═══════════════════════
  Ecuación: Activos = Pasivos + Patrimonio
```

**Verificación:**
- ✅ **Balanceado:** Activos = Pasivos + Patrimonio
- ❌ **Desbalanceado:** Revisar asientos contables

---

## 8. Flujo de Trabajo Recomendado

### Primer Mes de Operación

```
1. Configurar empresa y plan de cuentas
   ↓
2. Registrar saldos iniciales (asiento de apertura)
   ↓
3. Registrar socios (clientes y proveedores)
   ↓
4. Registrar inventario inicial
   ↓
5. Operar normalmente:
   - Emitir facturas de venta
   - Registrar facturas de compra
   - Registrar reparaciones
   ↓
6. Verificar libros contables
   ↓
7. Generar reportes tributarios
   ↓
8. Revisar estados financieros
   ↓
9. Declarar impuestos
```

### Cierre Mensual

1. **Verificar** que todos los asientos estén cuadrados
2. **Revisar** Libro Mayor por cuentas clave
3. **Generar** Estado de Resultados
4. **Generar** Balance General
5. **Verificar** ecuación patrimonial
6. **Declarar** IVA y retenciones

### Cierre Anual

1. Realizar todos los pasos del cierre mensual
2. Generar reportes anuales comparativos
3. Asiento de cierre de ingresos y gastos
4. Determinar utilidad del ejercicio
5. Preparar estados financieros definitivos

---

## 9. Roles y Permisos

### Acceso por Rol al Módulo Contable

| Función | Admin | Contador | Facturador | Vendedor |
|---------|-------|----------|------------|----------|
| Ver Plan de Cuentas | ✅ | ✅ | ✅ | ✅ |
| Crear Asientos | ✅ | ✅ | ❌ | ❌ |
| Ver Libro Mayor | ✅ | ✅ | ✅ | ❌ |
| Ver Libro de Ventas | ✅ | ✅ | ✅ | ✅ |
| Ver Libro de Compras | ✅ | ✅ | ❌ | ❌ |
| Declaración IVA | ✅ | ✅ | ❌ | ❌ |
| Retenciones | ✅ | ✅ | ❌ | ❌ |
| Estado de Resultados | ✅ | ✅ | ❌ | ❌ |
| Balance General | ✅ | ✅ | ❌ | ❌ |

### Permisos Granulares

El administrador puede asignar permisos específicos:

```
Administración → Usuarios → [Usuario] → Permisos
```

Módulos disponibles:
- `accounting` (create, read, update, delete)
- `invoicing` (create, read, update, delete, send_dian)
- `partners` (create, read, update, delete)
- `inventory` (create, read, update, delete)
- `repair` (create, read, update, delete)
- `wallet` (create, read, update, delete)

---

## 10. Solución de Problemas

### Problema: "El Balance General no cuadra"

**Causas comunes:**
1. Asiento contable descuadrado
2. Saldo inicial incorrecto
3. Asiento sin publicar

**Solución:**
1. Revisar asientos contables del período
2. Verificar que cada asiento tenga Debe = Haber
3. Publicar los asientos pendientes

### Problema: "No aparece IVA en la declaración"

**Verificar:**
1. Las facturas tienen IVA registrado
2. El período de fechas es correcto
3. Las facturas están en estado "Aceptado"

### Problema: "No puedo crear asientos contables"

**Verificar:**
1. El usuario tiene rol de CONTADOR o ADMINISTRADOR
2. La empresa está configurada
3. El plan de cuentas tiene cuentas creadas

### Problema: "Error al generar Estado de Resultados"

**Verificar:**
1. Existen asientos contables en el período
2. Las cuentas de ingresos y gastos están correctamente clasificadas
3. El rango de fechas es válido

---

## Glosario

| Término | Definición |
|---------|------------|
| **NIT** | Número de Identificación Tributaria |
| **DV** | Dígito de Verificación del NIT |
| **UVT** | Unidad de Valor Tributario |
| **Retefuente** | Retención en la fuente |
| **ReteIVA** | Retención del IVA |
| **DIAN** | Dirección de Impuestos y Aduanas Nacionales |
| **CUFE** | Código Único de Factura Electrónica |
| **Debe** | Columna izquierda del asiento contable |
| **Haber** | Columna derecha del asiento contable |
| **Libro Mayor** | Resumen de movimientos por cuenta |

---

## Contacto y Soporte

Para soporte técnico o consultas contables:

- **Documentación:** `/CAMBIOS_SESION_02_ABRIL_2025.md`
- **Plan de Acción:** `/PLAN_DE_ACCION.md`
