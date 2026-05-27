# Instrucciones de Despliegue en Producción - Seriales de Productos
**Fecha:** 26 de Mayo de 2026

Estas instrucciones detallan los pasos exactos para subir al servidor de producción los cambios que habilitan el registro, almacenamiento e impresión de números de serie / IMEI en el módulo de facturación.

## 1. Subir los cambios desde tu entorno local
Primero, asegúrate de enviar al repositorio (GitHub/GitLab) todos los cambios que hicimos localmente:

```bash
# En tu entorno local
cd /home/geralexcas/Reload_Matrix
git add backend/alembic/versions/d1e2f3a4b5c6_add_serial_number_to_invoice_items.py
git add backend/app/models/sql/invoicing.py
git add backend/app/schemas/invoicing.py
git add frontend/src/views/Invoicing/InvoicingView.vue
git add frontend/src/components/Invoicing/InvoicePrintModal.vue

git commit -m "feat: Habilitar seguimiento de seriales/IMEI en facturación y ticket POS"
git push origin main  # o la rama que estés utilizando (ej. develop)
```

## 2. Actualizar el código en el Servidor de Producción
Conéctate por SSH a tu servidor de producción y descarga los últimos cambios:

```bash
# Conectarse al servidor (reemplaza 'usuario@ip' con tus datos)
ssh usuario@ip_del_servidor

# Navegar a la carpeta del proyecto
cd /ruta/hacia/Reload_Matrix

# Descargar los cambios
git pull origin main
```

## 3. Aplicar Migraciones de Base de Datos
Debemos ejecutar la migración que agrega la columna `serial_number` en la tabla `invoice_items` en la base de datos de producción. 

```bash
# Estando en la carpeta del proyecto en el servidor:
docker compose exec backend alembic upgrade head
```
*Si la migración da algún error similar a que la versión ya está actualizada sin que exista la columna, puede que Alembic en producción haya perdido el hilo. En ese caso, aplica un "stamp" a la versión anterior y luego vuelve a ejecutar el upgrade (igual que hicimos en local).*

## 4. Reconstruir los Contenedores
Para que los cambios del Frontend (Vue.js) y del Backend (FastAPI) tengan efecto, necesitamos reconstruir y reiniciar los contenedores.

```bash
# Reconstruir el frontend (esto tomará unos minutos)
docker compose up -d --build frontend

# Reiniciar el backend para cargar los nuevos esquemas y modelos
docker compose restart backend
```

## 5. Verificación
Una vez que los contenedores estén funcionando:
1. Accede a la URL de producción desde tu navegador.
2. Presiona **Ctrl + F5** (o Cmd + Shift + R) en la vista de `/invoicing` para asegurarte de que el navegador no esté guardando en caché el frontend viejo.
3. Intenta crear una venta con un producto que tenga código de barras, confirma que se llene automáticamente el campo "N° Serie / IMEI".
4. Imprime la factura en formato POS y confirma que el serial salga impreso.
