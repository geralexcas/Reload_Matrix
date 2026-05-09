import httpx
import os
import sys

sys.path.append(os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.sql.user import User

def get_token():
    # create a token manually without password
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        print("No users found.")
        return
    
    from app.core.security import create_access_token
    from datetime import timedelta
    token = create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=60)
    )
    
    url = "http://localhost:8001/api/v1/accounting/libro-compras/?company_id=1"
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.get(url, headers=headers)
    print("Status:", r.status_code)
    try:
        data = r.json()
        print("Keys:", data.keys())
        if "entries" in data:
            print("Number of entries:", len(data["entries"]))
            if data["entries"]:
                print("First entry:", data["entries"][0])
    except Exception as e:
        print("Error:", e, r.text)

if __name__ == "__main__":
    get_token()
