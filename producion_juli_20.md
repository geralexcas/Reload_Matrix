migrar
docker compose exec backend alembic upgrade head
luego 
docker compose exec backend python scripts/init_database.py
