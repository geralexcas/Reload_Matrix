# Guía de Configuración para el Servidor de Producción

Este documento resume los pasos y soluciones implementadas para desplegar y configurar correctamente la aplicación (Backend y Frontend) en un entorno de producción utilizando Docker.

## 1. Ejecución de Scripts del Backend (Ej. Crear Administrador)

**Problema:** Al ejecutar scripts como `create_admin.py` directamente en la terminal del servidor con `python3 create_admin.py`, se producía el error `ModuleNotFoundError: No module named 'sqlalchemy'`.
**Razón:** El servidor (host) no tiene instaladas las dependencias de Python del proyecto.
**Solución implementada:** Se actualizó el código de `backend/scripts/create_admin.py` para usar correctamente la conexión a PostgreSQL. Para ejecutarlo en producción, *siempre* se debe hacer dentro del contenedor de Docker.

**Comando correcto para ejecutar scripts:**
```bash
# Asegúrate de estar en la raíz del proyecto
cd /home/geralexcas/Reload_Matrix

# Ejecutar el script dentro del contenedor del backend
docker compose exec backend python scripts/create_admin.py
```

## 2. Configuración Dinámica de la URL del Frontend

**Problema:** Al intentar hacer login, la consola del navegador mostraba `ERR_CONNECTION_REFUSED` hacia `http://localhost:8001/api/v1/auth/token`.
**Razón:** El frontend estaba intentando comunicarse con `localhost` (la computadora del usuario) en lugar de la IP del servidor de producción.
**Solución implementada:** Se modificó `frontend/src/services/api.js` para que la URL de la API sea dinámica utilizando la IP/dominio actual del navegador:

```javascript
baseURL: process.env.VUE_APP_API_URL || `${window.location.protocol}//${window.location.hostname}:8001`
```
**Pasos tras cualquier cambio en el frontend:**
Siempre que modifiques el frontend, debes reconstruir su contenedor para que los cambios se empaqueten:
```bash
docker compose up -d --build frontend
```

## 3. Configuración de Políticas de Seguridad (CORS)

**Problema:** Al hacer una petición exitosa hacia el backend con la IP correcta, el navegador bloqueaba la respuesta con el error: `CORS policy: No 'Access-Control-Allow-Origin' header is present...`.
**Razón:** El backend de FastAPI estaba configurado por defecto para aceptar únicamente peticiones desde `localhost`, rechazando peticiones que originaban desde la IP del servidor (`http://192.168.1.13:8081`).
**Solución implementada:**
1. Se actualizó el archivo `docker-compose.yml` para que la variable de entorno `ALLOWED_ORIGINS` del backend lea dinámicamente desde el archivo `.env`:
   ```yaml
   - ALLOWED_ORIGINS=${ALLOWED_ORIGINS:-http://localhost:8081,http://localhost:8080}
   ```
2. Se agregó la IP del servidor de producción a la lista en el archivo `.env` de la raíz:
   ```env
   ALLOWED_ORIGINS=http://localhost:8081,http://localhost:8080,http://192.168.1.13:8081
   ```

**Pasos para aplicar cambios de entorno o CORS en el backend:**
Cualquier cambio en `.env` o en el `docker-compose.yml` relacionado al backend, requiere reiniciar el contenedor para que FastAPI cargue los nuevos orígenes permitidos:
```bash
# Apagar y volver a levantar para asegurar la recarga del .env
docker compose down
docker compose up -d
```

## Resumen del Flujo de Trabajo en Producción

Si realizas cambios en tu entorno local y necesitas subirlos al servidor de producción, este es el orden ideal:

1. Subir cambios al servidor (Ej. `git pull origin main`).
2. Si cambiaste variables en `.env` o el `docker-compose.yml`:
   ```bash
   docker compose down
   docker compose up -d
   ```
3. Si cambiaste código del **Frontend** (`/frontend`):
   ```bash
   docker compose up -d --build frontend
   ```
4. Si cambiaste código del **Backend** (`/backend`):
   ```bash
   docker compose up -d --build backend
   ```
5. Si necesitas ejecutar scripts o migraciones:
   ```bash
   docker compose exec backend python scripts/tu_script.py
   ```
