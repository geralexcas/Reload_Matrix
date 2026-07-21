migrar
docker compose exec backend alembic upgrade head
luego 
docker compose exec backend python scripts/init_database.py

For production deployments
# Bootstrap (creates admin + seeds + assigns permissions):
docker compose exec backend python scripts/init_database.py

# Backfill existing users after code deploy:
docker compose exec backend python scripts/init_permissions.py --backfill

# Assign all perms to a specific user:
docker compose exec backend python scripts/init_permissions.py --assign-username german
The 403 errors on /partners/, /companies/, /dashboard/ should now be resolved for german.
