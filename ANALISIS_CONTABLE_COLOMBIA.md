# Análisis Contable del Sistema (Perspectiva de Contador Profesional Colombiano)

Tras realizar una auditoría detallada al código (`backend/app/services/accounting_service.py`) y a la documentación del proyecto (`GUIA_MODULO_CONTABLE.md`, `PLAN_DE_ACCION.md`, `IMPLEMENTACION_*.md`), se identifican brechas significativas entre el estado actual de la aplicación y la normativa contable, tributaria y fiscal exigente en Colombia.

A continuación, se detalla el análisis de problemas y funciones faltantes clasificados por áreas de impacto.

---

## 1. Cumplimiento Tributario y Fiscal (DIAN)

> **⚠️ ADVERTENCIA:** La aplicación actualmente presenta omisiones que pueden desencadenar sanciones o desconocimiento de costos/deducciones ante la DIAN.

### 1.1 Documento Soporte Electrónico
- **Problema:** En Colombia, al comprar bienes o servicios a proveedores no obligados a facturar (por ejemplo, personas naturales en el Régimen Simple o no responsables de IVA), es OBLIGATORIO emitir el **Documento Soporte en Adquisiciones Efectuadas a No Obligados a Facturar**.
- **Impacto:** Si la aplicación no genera y transmite este documento a la DIAN, todos esos costos y gastos serán rechazados en la declaración de Renta.
- **Solución faltante:** Crear el tipo de documento `SUPPORT_DOCUMENT`, con integración a la DIAN y generación del respectivo asiento contable (Costos/Gastos vs Cuentas por Pagar).

### 1.2 Multiplicidad de Retenciones (ReteICA, ReteIVA, Autorretenciones)
- **Problema:** El código asume retenciones en la fuente fijas (2.5% o 10%) e IVA (15%). Sin embargo, la normativa exige retenciones escalonadas y el cálculo del **ReteICA** (Retención de Industria y Comercio) que depende del municipio y la actividad económica. Además, no se maneja la **Autorretención Especial en la Fuente** (Decreto 2201 de 2016).
- **Solución faltante:** El sistema debe tener una tabla base de tarifas por concepto de retención y por municipio (tarifas por mil para ICA). Debe permitir marcar a la empresa como "Autorretenedora" para autoliquidarse.

### 1.3 Facturación POS y Documento Equivalente Electrónico
- **Problema:** Debido a la Resolución 165 de 2023, el tiquete de máquina registradora POS debe emitirse electrónicamente (Documento Equivalente Electrónico). Todo tiquete POS que supere 5 UVT debe saltar automáticamente a Factura Electrónica.
- **Solución faltante:** Implementar control del límite de UVT (aprox. 235.000 COP) y la transición forzosa a Facturación Electrónica B2B/B2C, así como el formato XML para el POS Electrónico.

### 1.4 Impuesto Nacional al Consumo (INC)
- **Problema:** Si el sistema fuera usado por prestadores de servicios de telefonía, restaurantes o venta de algunos vehículos, aplicaría Impuesto al Consumo (8% típicamente), el cual no se encuentra mapeado en el backend (solo se habla de IVA al 19% y 5%).

---

## 2. Información Financiera (NIIF para Pymes)

> **❗ IMPORTANTE:** El sistema lleva la contabilidad como un registro básico de "Debe" y "Haber", pero no automatiza procesos bajo el marco técnico normativo de NIIF (Decreto 2420 de 2015).

### 2.1 Depreciación, Amortización y Deterioro
- **Faltante:** No existe módulo de **Propiedad, Planta y Equipo (Activos Fijos)**. Se necesita automatizar la depreciación mensual contable y fiscal (que difieren).
- **Impacto:** Un asiento manual mensual para depreciar computadores, herramientas o maquinaria es propenso a errores y sobrevalora el Activo en el `Balance General`.

### 2.2 Costo de Inventario (Kárdex y Método de Valoración)
- **Faltante:** Si bien hay referencias a "Costo de Ventas", no queda claro cómo la aplicación maneja el método de valoración (Promedio Ponderado o PEPS/FIFO, que son los aceptados). Debería haber un Kárdex detallado para respaldar el costo de la cuenta `1140 (Inventarios)` y `5100 (Costo de ventas)`.

---

## 3. Integraciones Contables Claves Faltantes

### 3.1 Módulo de Nómina Electrónica
- **Problema:** Para que los gastos laborales sean deducibles fiscalmente, deben reportarse vía Nómina Electrónica.
- **Faltante:** No hay manejo de devengos y deducciones salariales, generación del documento soporte de Nómina Electrónica ni de su respectivo asiento (Sueldos, Salud, Pensión, ARL, Parafiscales a pasivos correspondientes).

### 3.2 Conciliación Bancaria
- **Problema:** La aplicación no incluye un mecanismo para homologar o emparejar los auxiliares de las cuentas de bancos (`1110` o `1120`) con los extractos bancarios mensuales.
- **Faltante:** Pantalla de cruce transaccional (Carga de extracto CSV/OFX vs Asientos contables).

### 3.3 Información Exógena (Medios Magnéticos)
- **Problema:** Es de las obligaciones más engorrosas para contadores colombianos. La aplicación captura el NIT del cliente/proveedor, pero no permite la parametrización de formatos (1001, 1005, 1006).
- **Faltante:** Generador de reportes en XML para subir al prevalidador de la DIAN al cierre del año. Requiere clasificación exhaustiva de terceros y conceptos.

### 3.4 CIERRE ANUAL CONTABLE Y FISCAL
- **Faltante:** El sistema no tiene un subproceso de "Cierre Anual". Requisito para cancelar las cuentas de resultados (Ingresos Clase 4, Gastos Clase 5 y Costos Clase 6) contra la cuenta de "Utilidad del Ejercicio" (Clase 3) y marcar el periodo como bloqueado para modificaciones.

---

## 4. Validaciones Técnicas en el Software Actual

- **Umbrales UVT Anclados:** En `accounting_service.py` se validan las 27 UVT para Retefuente. Sin embargo, el valor de la UVT cambia anualmente; el sistema requiere un repositorio o tabla cronológica de UVTs para no aplicar UVTs de 2026 en liquidaciones corregidas de 2025.
- **Notas Crédito / Débito Reales:** Indicadas en el `PLAN_DE_ACCION.md` como prioridad 3, pero para un contador es crítico, porque anular una factura directamente (sin nota crédito) destruye el principio de inalterabilidad contable.
- **Asimilación de Integraciones DIAN:** El estado de las facturas (`BORRADOR`, `ENVIADO`, `ACEPTADO`, `RECHAZADO`) depende de un servicio "Stub". No está manejando asíncronamente el acuse de recibo y la aceptación expresa exigida ahora por la DIAN (Ley 2155).

---

## 5. Escenario para Pequeñas Empresas (No Responsables de IVA / Antiguo Régimen Simplificado)

> **💡 CONTEXTO ESPECIAL:** Muchas empresas pequeñas que usan este tipo de sistemas no están obligadas a facturar electrónicamente, ni son responsables de IVA, por lo que el sistema actual no les ofrece un modo "simplificado" adecuado a su naturaleza.

### 5.1 Cuentas de Cobro / Remisiones
- **Problema:** El sistema actualiza todo alrededor del concepto de "Factura" (Invoice), lo que para un no responsable podría generar una contingencia fiscal si emite un documento que la DIAN considere factura sin cumplimiento de requisitos.
- **Faltante:** Capacidad de emitir **Cuentas de Cobro** o **Remisiones** en formato PDF sin ninguna validación ni stub hacia la DIAN.

### 5.2 Libro Fiscal de Registro de Operaciones Diarias
- **Faltante:** Las personas naturales o pequeñas empresas no responsables de IVA, aunque no lleven contabilidad formal, suelen estar obligadas o requerir un **Libro Fiscal de Operaciones Diarias** (registro de ingresos diarios) para demostrar que no superan los topes de 3.500 UVT que los obligaría a volverse responsables de IVA.

### 5.3 Parametrización "Modo Simplificado"
- **Faltante:** El sistema debería permitir, al crear la empresa, un switch de "No obligado a facturar / No responsable de IVA". Esto debería deshabilitar:
  - Cálculos automáticos de IVA generado local.
  - Botones y estados de "Envío a DIAN".
  - Retenciones complejas que no aplican para quienes no son agentes retenedores.

---

## Resumen de la Recomendación a Nivel de Negocio y Desarrollo

1. **Corto Plazo:** Desplegar notas crédito/débito y la tabla UVT anual con aplicación de retenciones variables por municipio (ICA) y tipo de compra.
2. **Mediano Plazo:** Lanzamiento del Documento Soporte Electrónico para no responsables, e incorporación del Documento Equivalente POS Electrónico con la DIAN en vivo.
3. **Largo Plazo:** Nómina Electrónica, Módulo de Activos Fijos (Depreciaciones Automáticas), y exportador de Medios Magnéticos y Formularios reales (110 y 350).
