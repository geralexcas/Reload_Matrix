# Solución: Error 400/500 en Creación de Productos

Este documento detalla la solución aplicada para resolver los errores al crear productos (especialmente serializados) y la duplicación de compras de stock inicial.

## Problemas Identificados
1. **TypeError**: Error de "múltiples valores" para el parámetro `skip_initial_stock_purchase` en la creación masiva.
2. **AttributeError**: Fallo al actualizar productos porque el flag `skip_initial_stock_purchase` se intentaba guardar en la base de datos.
3. **UndefinedColumn**: La tabla `purchase_items` no tenía la columna `serial_number` en producción, bloqueando el registro de stock inicial.
4. **PendingRollbackError**: Transacciones bloqueadas en el backend debido a errores previos no resueltos.

## Solución Aplicada

### 1. Cambios en el Código (Backend)
Se han actualizado los siguientes archivos en la carpeta `backend/app/services/inventory_service.py`:
- Se corrigió la instanciación de `ProductCreate` en `bulk_create_products`.
- Se añadió un `exclude={'skip_initial_stock_purchase'}` en `create_product` y `update_product`.

### 2. Actualización de Base de Datos
Se añadió la columna faltante en la tabla de compras:
```sql
ALTER TABLE purchase_items ADD COLUMN IF NOT EXISTS serial_number VARCHAR(255);
```

---

## Comandos para Aplicar en Producción

Si necesitas replicar o asegurar que todo esté correcto en el servidor, ejecuta estos comandos desde la carpeta raíz del proyecto (`~/Reload_Matrix` o `~/Reload_Matrix_II`):

### Paso A: Asegurar Base de Datos
Ejecuta este comando para añadir la columna si aún no existe:
```bash
docker exec reload_matrix_ii-db-1 psql -U user -d business_db -c "ALTER TABLE purchase_items ADD COLUMN IF NOT EXISTS serial_number VARCHAR(255);"
```

### Paso B: Reiniciar el Backend
Para aplicar los cambios de código y limpiar las sesiones bloqueadas:
```bash
docker restart reload_matrix_ii-backend-1
```

### Paso C: Verificar Logs (Opcional)
Para confirmar que no hay nuevos errores:
```bash
docker logs -f reload_matrix_ii-backend-1
```
