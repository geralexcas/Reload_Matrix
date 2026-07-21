# Plan de Implementación: Sistema de Suscripciones y Pagos

## 1. Backend: Modelo de Datos y Lógica
- **Creación de Modelo `Subscription`:** 
    - Campos: `id`, `company_id`, `start_date`, `end_date`, `plan_type` (Enum: MONTHLY), `status` (ACTIVE, EXPIRED).
- **Creación de Modelo `PaymentHistory`:**
    - Campos: `id`, `subscription_id`, `amount`, `payment_date`, `reference`.
- **Nuevo Endpoint:** `POST /api/v1/platform/tenants/{id}/activate`
    - Validación: Rol `PLATFORM_ADMIN`.
    - Lógica: Crea `Subscription` + `PaymentHistory` y actualiza `is_trial=False` en `Company`.

## 2. Frontend: Dashboard de SuperAdmin
- **Vista `TenantsView.vue`:**
    - Botón "Registrar Pago/Activar" en la tabla de empresas.
    - Modal de registro: Monto, referencia, tipo de plan.
- **Vista del Cliente (Empresa):**
    - Componente de alerta (`v-if="days_until_expiry <= 5"`) en el layout para notificar vencimiento inminente.

## 3. Flujo de Activación y Notificación
- **Notificación:** El `scheduler` (revisión diaria) actualizará `days_until_expiry` y disparará banderas para la alerta visual en el frontend.
- **Futura escalabilidad:** Integración prevista con Wompi para pagos automáticos (reutilizando modelos creados).
