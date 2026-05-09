# Resolución: Compras no visibles en el Libro de Compras

Se ha resuelto el problema que impedía que los registros de compras se mostraran en la interfaz de contabilidad (`/accounting/libro-compras`).

## Cambios Realizados

### 1. Corrección de Construcción de URLs (Frontend)
Se identificó un error donde las llamadas a la API generaban una URL con doble barra inicial (`//api/v1/...`). Esto ocurría porque:
- `baseURL` en `api.js` estaba configurado como `/`.
- Los componentes concatenaban `${process.env.VUE_APP_API_URL}/api/v1/...`.
- Al estar vacía la variable de entorno, el resultado era `//api/v1/...`, lo cual el navegador interpreta como un host llamado `api`, fallando la petición y recibiendo el HTML de `index.html` como respuesta de fallback.

**Solución:** Se centralizó la configuración en `api.js` y se eliminaron los prefijos manuales en los componentes `LibroComprasView.vue` y `LibroVentasView.vue`.

### 2. Robustez en el Renderizado (Frontend)
Se añadieron validaciones defensivas en `LibroComprasView.vue` para evitar que la aplicación falle (crash) si los datos de totales o la respuesta de la API no tienen el formato esperado.

### 3. Despliegue de Cambios
Dado que el contenedor de frontend no tenía mapeo de volúmenes para cambios en caliente, se procedió a:
1. Reconstruir la imagen de Docker del frontend.
2. Reiniciar el servicio `frontend`.

## Verificación Final

Se confirmó mediante pruebas en el navegador que:
- La tabla de compras carga correctamente.
- Se muestran **3 registros** (incluyendo compras directas y facturas de compra).
- Los totales se calculan y muestran correctamente ($3,080,000 en total).

### Captura de Pantalla de Verificación
![Libro de Compras con datos](/home/geralexcas/.gemini/antigravity/brain/7a4d2331-4f97-422a-bac8-9034705ecb18/.system_generated/screenshots/screenshot_1778298687538.png)
*(Nota: Se observan los 3 registros mencionados anteriormente)*
