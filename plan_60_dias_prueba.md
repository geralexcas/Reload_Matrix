# Implementar Periodo de Prueba de 60 Días para Empresas

Se requiere implementar un periodo de prueba automático de 60 días al crear nuevas empresas. Si la empresa no cambia a un estado "pago" (o si el periodo expira), la empresa se desactivará automáticamente. Además, cuando falten 10 días para expirar, se mostrará un recordatorio al usuario en el sistema.

## User Review Required

> [!WARNING]
> **Migración de Base de Datos:** Esta implementación requerirá agregar la columna `is_trial` a la tabla `companies`. Se creará una migración automática con Alembic. Las empresas existentes deberán definirse como `is_trial=False` (empresas estables) o `True` según se defina. Por defecto las estableceré como `False` en la migración para que no se desactiven abruptamente las empresas que ya se encuentran operando.
>
> **Política de Desactivación Automática:** Actualmente la desactivación dejará a todos los usuarios del tenant sin poder iniciar sesión o acceder a la API (si tienen el `is_active=False` a nivel de compañía, o si el acceso es denegado al validar la empresa activa). Revisa si este es el comportamiento esperado.

## Open Questions

> [!IMPORTANT]
> 1. ¿Cómo se cambiará el estado de la empresa de "prueba" a "pago"? Por el momento, dejaré que el administrador general (platform admin) pueda modificar este campo (desmarcar la casilla de prueba) desde el panel de control o por base de datos, ya que no se especifica una pasarela de pagos.
> 2. Las empresas ya existentes en la base de datos, ¿deben tratarse como empresas en prueba, o empresas de pago? (Asumiré que son de pago para evitar que se desactiven por error).

## Proposed Changes

---

### Backend: Modelos y Base de Datos

Se modificará el modelo principal de las empresas para incluir el estado de prueba.

#### [MODIFY] `app/models/sql/company.py`
- Agregar la columna `is_trial = Column(Boolean, default=True)` para identificar a las empresas que están en el periodo de gracia inicial.

#### [MODIFY] `app/schemas/company.py`
- Agregar `is_trial: bool` en el esquema `CompanyResponse` para que el frontend pueda conocer el estado actual de la empresa.

#### [NEW] `alembic/versions/[hash]_add_company_trial_fields.py`
- Generar una nueva migración con `alembic revision --autogenerate` que añada la columna `is_trial`.

---

### Backend: Tarea Programada (Scheduler)

Se agregará un nuevo Job diario para revisar las fechas de creación y desactivar a los morosos.

#### [MODIFY] `app/core/scheduler.py`
- Agregar una función `check_trial_expirations()`.
- Esta función buscará las empresas donde `is_trial=True` y `is_active=True`.
- Calculará si `datetime.now() > created_at + timedelta(days=60)`.
- Si es verdadero, establecerá `is_active=False` y guardará los cambios, registrando un log (y opcionalmente audit log).
- Programar esta función para que corra cada 24 horas (usando el actual APScheduler configurado).

---

### Frontend: UI Recordatorio

Se mostrará una alerta permanente en la aplicación cuando queden 10 días (o menos) del periodo de prueba.

#### [MODIFY] `frontend/src/store/modules/auth.js` o `company.js`
- Asegurar que al recuperar la sesión y los datos del usuario, los campos `created_at` y `is_trial` de la empresa del usuario queden almacenados en el store (Vuex).

#### [MODIFY] `frontend/src/components/layout/DashboardLayout.vue`
- Agregar una barra de notificaciones (`<div class="trial-banner">...</div>`) encima o debajo del `TopHeader`.
- Esta alerta evaluará: si `is_trial` es true, calculará `dias_transcurridos = (fecha_actual - created_at)`.
- Si `dias_transcurridos >= 50` y `dias_transcurridos < 60`, se mostrará la alerta: *"Te quedan X días de tu periodo de prueba de 60 días. Contacta con soporte para mantener el servicio."*
- Se aplicarán clases CSS (fondo amarillo/naranja con texto destacado) para que resalte.

## Verification Plan

### Automated Tests
1. Añadir/Actualizar test en `tests/unit/test_company.py` o similar si es necesario, o testear la logica del scheduler aislando la llamada a la DB (mock).
2. Se correrán las pruebas del backend con `pytest` para verificar que ninguna funcionalidad de creación se rompa al agregar el nuevo campo.

### Manual Verification
1. Levantar contenedores (`docker-compose up --build`).
2. Crear una nueva empresa y revisar que se guarda con `is_trial=True`.
3. Simular en la base de datos cambiando el `created_at` de esa empresa a hace 55 días y recargar el frontend para validar que aparezca el banner rojo/naranja.
4. Cambiar el `created_at` a hace 61 días.
5. Ejecutar la función del scheduler manualmente o esperar a que corra, y verificar en base de datos que `is_active` pase a ser `False`.
6. Tratar de hacer login o operaciones y verificar que el sistema restringe a la empresa desactivada.
