# Plan: git pull origin master (be9fe12 → c06a132)

## Estado actual
- Branch master 10 commits atrás (fast-forwardable).
- `deleted:` backend/scripts/delete_invoice_prod.py (sin stagear).
- Untracked: backend/app/scripts/delete_invoice_prod.py, delete_invoice.py, 5 backups .zip locales.
- stash@{0} previo (se conserva).
- Pull trae: `A` backend/backups/backup_20260710_144450.zip (nombre NUEVO, no choca) + `M` backend/scripts/delete_invoice_prod.py.

## Decisión
Quedarse con la versión entrante de backend/scripts/delete_invoice_prod.py.

## Pasos

1. Restaurar el archivo borrado localmente desde HEAD:
   ```bash
   git restore backend/scripts/delete_invoice_prod.py
   ```

2. Fast-forward pull:
   ```bash
   git pull origin master
   ```

3. Verificar:
   ```bash
   git status
   git log --oneline -3
   ls backend/backups/
   ```

4. Limpieza opcional (copias redundantes untracked):
   ```bash
   rm backend/app/scripts/delete_invoice_prod.py delete_invoice.py
   ```
   (si las usás como helper local, dejarlas)

## Posterior (recomendado)
Ignorar backups del scheduler para que no vuelvan al repo:
```bash
printf '\nbackend/backups/*.zip\n' >> backend/.gitignore
```

## No afectado
- stash@{0} (intacto)
- 5 backups locales untracked (siguen ahí)