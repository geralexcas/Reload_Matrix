import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(str(settings.DATABASE_URL))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from app.api.v1.deps import get_current_user
def override_get_current_user():
    class User:
        id = 1
        email = "test@test.com"
        is_active = True
        is_superuser = True
        company_id = 1
    return User()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

response = client.get("/api/v1/purchases/?company_id=1")
print("STATUS:", response.status_code)
if response.status_code == 200:
    purchases = response.json()
    print("Purchases count:", len(purchases))
    for p in purchases:
        print(f"ID: {p['id']}, Number: {p['purchase_number']}")
else:
    print("ERROR:", response.text)
