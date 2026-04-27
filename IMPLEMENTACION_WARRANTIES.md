# Implementación: Tabla Warranties (Garantías) - Item 1

**Fecha:** 31 de marzo 2026

## Descripción

Se creó la tabla `warranties` como modelo independiente de base de datos, tal como estaba contemplado en el plan inicial pero no existía. Anteriormente, la garantía estaba embebida en `repair_items` como campo `warranty_status` y en `repair_orders` como flag `warranty_applied`.

## Archivos modificados

### 1. Modelo SQLAlchemy
**Archivo:** `backend/app/models/sql/repair.py`
- Agregado modelo `Warranty` con campos:
  - `id`, `repair_order_id` (FK), `repair_item_id` (FK nullable), `company_id` (FK)
  - `warranty_type`: MANUFACTURER, SERVICE, PARTS
  - `start_date`, `end_date` (fechas de vigencia)
  - `status`: ACTIVE, EXPIRED, VOID, CLAIMED
  - `description`, `terms_and_conditions`
  - `claim_date`, `claim_description`, `claim_resolution` (para reclamos)
  - `created_at`, `updated_at`
- Relaciones con `RepairOrder`, `RepairItem` y `Company`

### 2. Schemas Pydantic
**Archivo:** `backend/app/schemas/repair.py`
- `WarrantyBase`: campos base con validación de warranty_type
- `WarrantyCreate`: para creación
- `WarrantyResponse`: para respuestas API
- `WarrantyClaim`: para registrar reclamos de garantía

### 3. Servicio de negocio
**Archivo:** `backend/app/services/repair_service.py`
- `create_warranty()`: Crea garantía validando repair_order y repair_item
- `get_warranties()`: Lista con paginación y filtro por estado
- `get_warranty_by_id()`: Obtener por ID
- `get_warranties_by_repair_order()`: Garantías de una orden específica
- `update_warranty_status()`: Cambiar estado (ACTIVE/EXPIRED/VOID/CLAIMED)
- `file_warranty_claim()`: Registrar reclamo con validaciones (activa, no vencida)
- `check_expired_warranties()`: Marca automáticamente garantías vencidas
- `delete_warranty()`: Eliminar garantía

### 4. Endpoints API
**Archivo:** `backend/app/api/v1/routers/repair.py`
- `POST /api/v1/repair/warranties/` - Crear garantía
- `GET /api/v1/repair/warranties/` - Listar (filtro opcional por estado)
- `GET /api/v1/repair/warranties/{id}` - Obtener por ID
- `GET /api/v1/repair/repair-orders/{id}/warranties/` - Garantías por orden
- `PUT /api/v1/repair/warranties/{id}/status/` - Actualizar estado
- `POST /api/v1/repair/warranties/{id}/claim/` - Registrar reclamo
- `POST /api/v1/repair/warranties/check-expired/` - Verificar vencidas
- `DELETE /api/v1/repair/warranties/{id}` - Eliminar

### 5. Migración Alembic
**Archivo:** `backend/alembic/versions/6f3ede781b9a_add_warranties_table.py`
- Creación de tabla `warranties` con índices y tipos ENUM
- Rollback completo en downgrade

## Verificación

Todos los imports verifican correctamente:
- Modelo Warranty ✅
- Schemas (WarrantyCreate, WarrantyResponse, WarrantyClaim) ✅
- RepairService con métodos de warranty ✅
- Router con nuevos endpoints ✅
- Aplicación FastAPI completa ✅
