# Pasos a Producción — Julio 10, 2026

## Resumen de cambios de esta sesión

| Cambio | Archivo | Detalle |
|--------|---------|---------|
| Asiento fantasma #7 eliminado | (ejecutado en BD) | JE id=30 `INV-000007` + 2 líneas borrados |
| Migración trigger anti-delete | `backend/alembic/versions/a4b5c6d7e8f9_prevent_direct_invoice_delete.py` | `BEFORE DELETE` en `invoices` que bloquea borrado directo |
| Endpoint DELETE removido | `backend/app/api/v1/routers/invoicing.py` | `DELETE /invoicing/{id}` siempre fallaba, frontend no lo usaba |
| Script deprecado | `backend/scripts/delete_invoice_prod.py` | Redirige a `delete_ghost_asiento.py` |
| Script nuevo | `backend/scripts/delete_ghost_asiento.py` | Limpia asientos huérfanos con dry-run + `--force` |

### Archivos a commitear (solo estos 4)

```
backend/alembic/versions/a4b5c6d7e8f9_prevent_direct_invoice_delete.py
backend/scripts/delete_ghost_asiento.py
backend/scripts/delete_invoice_prod.py
backend/app/api/v1/routers/invoicing.py
```

### Archivos EXCLUIDOS del commit (ya estaban modificados antes de la sesión)

```
backend/app/schemas/invoicing.py
backend/app/services/accounting_service.py
backend/app/services/invoicing_service.py
frontend/src/views/Invoicing/InvoicingView.vue
backend/backups/backup_20260710_144450.zip
```

---

## Pre-requisitos

- [ ] Acceso SSH al servidor (192.168.1.13)
- [ ] `.env` de producción con `SECRET_KEY`, `DATABASE_URL` y `ALLOWED_ORIGINS` correctos
- [ ] Docker Compose operativo en el servidor
- [ ] Cloudflare Tunnel corriendo (`sudo systemctl status cloudflared`)
- [ ] No hay usuarios activos usando el sistema (coordinar ventana de mantenimiento)

---

## Step 1 — Backup de la base de datos

```bash
# En el servidor, antes de tocar nada
cd /ruta/Reload_Matrix

# Backup completo de PostgreSQL
docker compose exec -T db pg_dump -U user business_db > backup_pre_julio10.sql

# Verificar que el backup no esté vacío
ls -lh backup_pre_julio10.sql
wc -l backup_pre_julio10.sql

# Backup del docker-compose.yml actual (por si hay que revertir)
cp docker-compose.yml docker-compose.yml.backup_julio10
```

---

## Step 2 — Commit y push (desde tu máquina local)

```bash
cd /home/geralexcas/Reload_Matrix

# 1. Revisar el diff antes de commitear
git diff backend/app/api/v1/routers/invoicing.py
git diff backend/scripts/delete_invoice_prod.py

# 2. Stage SOLO los 4 archivos de esta sesión
git add backend/alembic/versions/a4b5c6d7e8f9_prevent_direct_invoice_delete.py
git add backend/scripts/delete_ghost_asiento.py
git add backend/scripts/delete_invoice_prod.py
git add backend/app/api/v1/routers/invoicing.py

# 3. Verificar que NO se staged archivos excluidos
git status

# 4. Commit
git commit -m "fix: trigger anti-delete invoices + cleanup asiento fantasma #7

- Migracion a4b5c6d7e8f9: trigger BEFORE DELETE en invoices que bloquea
  borrado directo (previene asientos contables huerfanos)
- Eliminado endpoint DELETE /invoicing/{id} (siempre fallaba, frontend no lo usaba)
- delete_invoice_prod.py deprecado, redirige a delete_ghost_asiento.py
- delete_ghost_asiento.py: script reutilizable para limpiar asientos huerfanos
- Asiento fantasma INV-000007 (JE id=30) ya limpiado en BD"

# 5. Push a master
git push origin master
```

### Verificar que el CI pase

```bash
# Abrir en el navegador:
# https://github.com/geralexcas/Reload_Matrix/actions
# Esperar que los jobs backend-lint, backend-test y backend-build pasen en verde
```

---

## Step 3 — Pull en el servidor

```bash
# SSH al servidor
ssh tu_usuario@192.168.1.13

cd /ruta/Reload_Matrix

# Verificar estado actual
git log --oneline -3

# Pull de los cambios
git pull origin master

# Verificar que los archivos llegaron
git log --oneline -3
ls -la backend/alembic/versions/a4b5c6d7e8f9_prevent_direct_invoice_delete.py
ls -la backend/scripts/delete_ghost_asiento.py
```

---

## Step 4 — Aplicar la migración

```bash
cd /ruta/Reload_Matrix

# Verificar estado actual de Alembic
docker compose exec backend alembic current

# Aplicar migraciones pendientes
docker compose exec backend alembic upgrade head

# Verificar que la migración a4b5c6d7e8f9 quedó aplicada
docker compose exec backend alembic current
# Debe mostrar: a4b5c6d7e8f9 (head)

# Verificar que el trigger existe en la BD
docker compose exec db psql -U user -d business_db -c \
  "SELECT tgname FROM pg_trigger WHERE tgrelid = 'invoices'::regclass AND NOT tgisinternal;"
# Debe mostrar: trg_prevent_invoice_delete
```

---

## Step 5 — Reconstruir contenedores

```bash
cd /ruta/Reload_Matrix

# Reconstruir backend (para que tome el router sin endpoint DELETE)
docker compose up -d --build backend

# Reconstruir frontend (por si hubo cambios en InvoicingView.vue)
docker compose up -d --build frontend

# Esperar a que ambos estén healthy
docker compose ps
# Verificar que backend y frontend digan "Up (healthy)"
```

---

## Step 6 — Verificación post-deploy

```bash
cd /ruta/Reload_Matrix

# 1. Verificar que el endpoint DELETE ya no existe
docker compose exec backend python -c "
from app.main import app
routes = [r.path for r in app.routes if hasattr(r, 'methods') and 'DELETE' in r.methods and 'invoic' in r.path.lower()]
print('DELETE routes in invoicing:', routes)
"
# Debe imprimir: DELETE routes in invoicing: []

# 2. Verificar que el trigger bloquea DELETE directo
docker compose exec db psql -U user -d business_db -c "
BEGIN;
DELETE FROM invoices WHERE id = 1;
ROLLBACK;
"
# Debe fallar con: ERROR: DELETE directo en invoices prohibido. Use cancel_invoice...

# 3. Verificar que cancel_invoice (UPDATE) sigue funcionando
docker compose exec db psql -U user -d business_db -c "
BEGIN;
UPDATE invoices SET status = 'CANCELLED' WHERE id = 1 AND status = 'CANCELLED';
ROLLBACK;
"
# Debe transitar sin error

# 4. Verificar frontend y API desde fuera
curl -I https://midominio.com           # Frontend (200 OK)
curl -I https://midominio.com/api/v1/   # Backend API (404 o 405, pero responde)

# 5. Revisar logs del backend sin errores
docker compose logs backend --tail=50
# Buscar: no debe haber tracebacks ni errores de import
```

---

## Step 7 — Rollback (si algo sale mal)

### Rollback de la migración (elimina el trigger)

```bash
docker compose exec backend alembic downgrade -1
# Esto ejecuta el downgrade de a4b5c6d7e8f9:
#   DROP TRIGGER trg_prevent_invoice_delete ON invoices
#   DROP FUNCTION prevent_invoice_delete()
```

### Rollback del código

```bash
# En el servidor
cd /ruta/Reload_Matrix
git log --oneline -5          # Encontrar el hash del commit anterior
git reset --hard <commit_anterior>
```

### Restaurar backup de la base de datos

```bash
# Solo si hubo daños en datos
docker compose exec -T db psql -U user -d business_db < backup_pre_julio10.sql
```

### Restaurar docker-compose.yml

```bash
cp docker-compose.yml.backup_julio10 docker-compose.yml
docker compose up -d --build backend frontend
```

---

## Notas

- **Secretos:** NUNCA commitear `.env`, `backups/`, ni secretos. Verificar que `.gitignore` los excluye.
- **Trigger override:** Si un admin necesita borrar una factura deliberadamente:
  ```sql
  SET session_replication_role = 'replica';
  DELETE FROM invoices WHERE id = X;
  SET session_replication_role = 'origin';
  ```
- **Reusar el script ghost:** Si aparece otro asiento fantasma en el futuro:
  ```bash
  docker compose exec backend python scripts/delete_ghost_asiento.py --invoice-id <id>          # dry-run
  docker compose exec backend python scripts/delete_ghost_asiento.py --invoice-id <id> --force  # borrar
  ```