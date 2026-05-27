# Instrucciones para Subir Código a Producción

Guía paso a paso para desplegar Reload Matrix en el servidor de producción.

---

## Prerrequisitos

- Acceso SSH al servidor de producción
- Git configurado con acceso al repositorio `git@github.com:geralexcas/Reload_Matrix.git`
- Docker y Docker Compose instalados en el servidor
- Archivo `.env` configurado en producción (ver sección de variables de entorno)

---

## Paso 1: Preparar los cambios localmente

### 1.1 Verificar que no hay cambios pendientes o sin commitear

```bash
git status
```

Si hay cambios sin commitear, revisarlos y hacer commit:

```bash
git add <archivos>
git commit -m "tipo: descripción del cambio"
```

### 1.2 Ejecutar linting localmente

```bash
# Backend
docker compose exec backend python -m ruff check app/

# Frontend
docker compose exec frontend sh -c "npm run lint -- --no-fix"
```

Si hay errores de lint, corregirlos antes de continuar.

### 1.3 Ejecutar las pruebas backend

```bash
docker compose exec backend python -m pytest -v
```

Todas las pruebas deben pasar antes de subir a producción.

### 1.4 Generar migraciones pendientes (si se modificaron modelos)

```bash
docker compose exec backend alembic revision --autogenerate -m "descripción del cambio"
```

Verificar el archivo generado en `backend/alembic/versions/` antes de commitear.

### 1.5 Hacer push al repositorio

```bash
git push origin master
```

---

## Paso 2: Conectarse al servidor de producción

```bash
ssh usuario@IP_DEL_SERVIDOR
```

Ejemplo:
```bash
ssh admin@192.168.1.13
```

---

## Paso 3: Descargar los cambios en el servidor

### 3.1 Navegar al directorio del proyecto

```bash
cd /home/geralexcas/Reload_Matrix
```

### 3.2 Hacer pull de los cambios

```bash
git pull origin master
```

Si hay conflictos, resolverlos antes de continuar:

```bash
git status                    # Ver archivos en conflicto
# Editar los archivos en conflicto manualmente
git add <archivos_resueltos>
git commit -m "fix: resolver conflictos de merge"
```

---

## Paso 4: Reconstruir los contenedores

### 4.1 Si solo cambió el backend

```bash
docker compose up -d --build backend
```

### 4.2 Si solo cambió el frontend

```bash
docker compose up -d --build frontend
```

### 4.3 Si cambiaron ambos (backend + frontend)

```bash
docker compose up -d --build backend frontend
```

### 4.4 Si cambiaron variables de entorno (.env) o docker-compose.yml

```bash
docker compose down
docker compose up -d --build
```

**Importante:** `docker compose down` detiene todos los servicios. Los datos de PostgreSQL se conservan porque están en un volumen nombrado (`postgres_data`).

---

## Paso 5: Aplicar migraciones de base de datos

Después de reconstruir el backend, aplicar las migraciones pendientes:

```bash
docker compose exec backend alembic upgrade head
```

Verificar que no hay errores en la salida.

---

## Paso 6: Ejecutar scripts de inicialización (si es necesario)

Solo si el deploy incluye nuevos scripts o cambios en permisos/datos iniciales:

```bash
# Inicializar permisos
docker compose exec backend python scripts/init_permissions.py

# Inicializar datos de la base de datos
docker compose exec backend python scripts/init_database.py

# Crear usuario administrador (solo si es un deploy fresco)
docker compose exec backend python scripts/create_admin.py
```

---

## Paso 7: Verificar el despliegue

### 7.1 Verificar que los contenedores están corriendo

```bash
docker compose ps
```

Los 3 servicios deben mostrar estado `Up` y `healthy`:
- `reload_matrix-backend-1`
- `reload_matrix-frontend-1`
- `reload_matrix-db-1`

### 7.2 Verificar logs del backend

```bash
docker compose logs backend --tail=50
```

Buscar errores o excepciones. Debe mostrar que Uvicorn está corriendo en puerto 8000.

### 7.3 Verificar logs del frontend

```bash
docker compose logs frontend --tail=20
```

### 7.4 Verificar conectividad de la API

```bash
curl -f http://localhost:8001/docs
```

Debe retornar HTTP 200.

### 7.5 Verificar el frontend en el navegador

Abrir en el navegador:
```
http://IP_DEL_SERVIDOR:8081
```

Verificar:
- La página de login carga correctamente
- Se puede iniciar sesión
- La navegación entre módulos funciona
- No hay errores en la consola del navegador (F12)

---

## Paso 8: Verificar la base de datos

### 8.1 Confirmar que las migraciones están al día

```bash
docker compose exec backend alembic current
```

Debe mostrar la revisión más reciente (`head`).

### 8.2 Verificar columnas nuevas (si aplican)

```bash
docker compose exec backend python -c "
from app.core.database import engine
from sqlalchemy import inspect
insp = inspect(engine)
cols = [c['name'] for c in insp.get_columns('nombre_tabla')]
print(cols)
"
```

---

## Paso 9: Configuración de CORS (si cambió la IP/dominio)

Si el servidor de producción usa una IP o dominio diferente al configurado, actualizar `.env`:

```bash
nano .env
```

Agregar la URL del frontend a `ALLOWED_ORIGINS`:

```env
ALLOWED_ORIGINS=http://localhost:8081,http://192.168.1.13:8081,http://tu-dominio.com
```

Luego reiniciar el backend:

```bash
docker compose up -d --build backend
```

---

## Paso 10: Backup post-despliegue

Hacer un backup de la base de datos después de un despliegue exitoso:

```bash
docker compose exec db pg_dump -U user business_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## Resumen rápido (checklist)

```
[ ] 1. Lint y pruebas pasan localmente
[ ] 2. Migraciones generadas y verificadas
[ ] 3. Push a master
[ ] 4. SSH al servidor
[ ] 5. git pull origin master
[ ] 6. docker compose up -d --build backend frontend
[ ] 7. docker compose exec backend alembic upgrade head
[ ] 8. docker compose ps (todos healthy)
[ ] 9. Verificar logs sin errores
[ ]10. Probar en navegador
[ ]11. Backup de BD
```

---

## Variables de entorno (.env) para producción

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta para JWT (obligatoria) | `openssl rand -hex 32` |
| `DATABASE_URL` | URL de conexión PostgreSQL | `postgresql://user:password@db:5432/business_db` |
| `ALLOWED_ORIGINS` | URLs del frontend separadas por coma | `http://192.168.1.13:8081` |
| `LOG_LEVEL` | Nivel de logging | `INFO` o `WARNING` |
| `ENVIRONMENT` | Entorno de ejecución | `production` |
| `UPLOAD_DIR` | Directorio de subidas | `uploads` |
| `GEMINI_API_KEY` | API key de Google Gemini (si se usa IA) | `AIza...` |
| `DIAN_CERT_PATH` | Ruta del certificado DIAN | `/app/certs/cert.p12` |
| `DIAN_CERT_PASSWORD` | Password del certificado DIAN | `****` |
| `DIAN_ENVIRONMENT` | Ambiente DIAN | `prod` |

**Importante:** NUNCA commitear el archivo `.env` al repositorio. Copiar `.env.example` y llenar con los valores reales en el servidor.

---

## Rollback (en caso de fallo)

Si el despliegue falla y necesitas revertir:

### 1. Volver a la versión anterior del código

```bash
git log --oneline -10          # Ver los últimos commits
git checkout <commit_anterior> # Volver al commit anterior
```

### 2. Reconstruir contenedores

```bash
docker compose up -d --build backend frontend
```

### 3. Revertir migración (si se aplicó una nueva)

```bash
docker compose exec backend alembic downgrade -1
```

### 4. Restaurar backup de base de datos (si es necesario)

```bash
docker compose down
# Restaurar el volumen de PostgreSQL
cat backup_YYYYMMDD_HHMMSS.sql | docker compose exec -T db psql -U user -d business_db
docker compose up -d
```

---

## Comandos de emergencia

| Situación | Comando |
|-----------|---------|
| Ver logs en tiempo real | `docker compose logs -f backend` |
| Reiniciar solo el backend | `docker compose restart backend` |
| Reset completo (pierde datos) | `./reset_database.sh` |
| Entrar al contenedor backend | `docker compose exec backend bash` |
| Ver uso de recursos | `docker stats` |
| Limpiar imágenes viejas | `docker image prune -f` |
| Espacio en disco del servidor | `df -h` |
