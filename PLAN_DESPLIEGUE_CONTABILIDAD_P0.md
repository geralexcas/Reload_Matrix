# Plan de Despliegue en Producción - Correcciones Contables P0

Este plan detalla los pasos requeridos para desplegar las correcciones estructurales de contabilidad en el entorno de producción (192.168.1.13:8081) y limpiar los registros históricos corruptos de forma segura.

## Objetivo
Implementar los cambios que previenen la duplicidad contable y el uso de las cuentas "3100/5400" en la base de datos de producción, y ejecutar un script diseñado específicamente para depurar los asientos duplicados históricos.

## 1. Script de Limpieza de Datos
Se ha creado el script `backend/scripts/cleanup_duplicate_accounting_p0.py`. Este script está diseñado de manera conservadora para **únicamente** buscar y eliminar asientos que cumplan con todos los siguientes criterios:
- La referencia empiece con `DEP-` o `WDL-` (generados por tesorería).
- La descripción coincida exactamente con las cadenas automáticas generadas por el sistema (`Pago a proveedor - Factura %`, `Cobro reparación %`, `Pago - Factura %`, `Reversión por anulación de factura %`).

Al encontrar estos asientos duplicados, el script:
1. Desvinculará la transacción de tesorería del asiento duplicado (`journal_entry_id = None`).
2. Eliminará las líneas del asiento (`JournalEntryLine`).
3. Eliminará el asiento principal (`JournalEntry`).

> [!CAUTION]
> El script eliminará datos financieros, por lo que es de carácter obligatorio realizar un backup completo de la base de datos de producción antes de ejecutarlo.

## 2. Pasos de Despliegue

### Fase 1: Respaldo (Backup)
Ingresar por SSH al servidor de producción y generar un volcado de seguridad:
```bash
docker compose exec db pg_dump -U user -d business_db -F c -f /var/lib/postgresql/data/backup_pre_cleanup_p0.dump
```

### Fase 2: Actualización de Código
Traer los últimos cambios desde el repositorio (rama principal):
```bash
git pull origin main
```

### Fase 3: Reconstrucción y Reinicio de Servicios
Reconstruir la imagen del backend para que incorpore el nuevo código y el nuevo script:
```bash
docker compose up -d --build backend
```
Verificar que el servicio levantó correctamente revisando los logs:
```bash
docker compose logs -f backend
```

### Fase 4: Ejecución del Script de Limpieza
Ejecutar el script que eliminará los asientos duplicados históricos:
```bash
docker compose exec backend python scripts/cleanup_duplicate_accounting_p0.py
```
> [!IMPORTANT]
> El script imprimirá en pantalla el número exacto de asientos encontrados y eliminados. Se debe revisar este output para certificar que funcionó como se esperaba.

## Verificación Post-Despliegue
- Ingresar al sistema desde el frontend en Producción.
- Realizar una transacción de prueba (Ej: Pagar una factura de compra o registrar una venta) y revisar el **Libro Diario**.
- Confirmar que:
  - Solo se haya generado un (1) asiento contable en lugar de dos.
  - La transacción de la caja de tesorería se haya descontado correctamente sin afectar artificialmente la cuenta de Capital (3100) ni Gastos Financieros (5400).
- Revisar los saldos del Balance General y Estado de Resultados para confirmar la nivelación de las cuentas.
