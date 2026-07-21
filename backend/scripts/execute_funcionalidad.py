import httpx
import json

# URL and Credentials
BASE_URL = "http://localhost:8001"
USERNAME = "admin@example.com"
PASSWORD = "adminpassword"

def get_token(client):
    r = client.post(f"{BASE_URL}/api/v1/auth/login", data={"username": USERNAME, "password": PASSWORD})
    if r.status_code != 200:
        raise Exception(f"Login failed: {r.status_code} {r.text}")
    return r.json()["access_token"]

def main():
    with httpx.Client() as client:
        token = get_token(client)
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        print("--- 1. Crea recepción de equipo, usuario, producto ---")
        # Assuming evocomputo exists (e.g., ID 1)
        # Create user
        user = {"email": "technician@evocomputo.com", "full_name": "Tecnico", "password": "password123", "company_id": 1}
        # r = client.post(f"{BASE_URL}/api/v1/users/", json=user, headers=headers)
        # print(f"User created: {r.status_code}")
        
        # Create product
        product = {"name": "Equipo Prueba", "sku": "EQ-001", "price": 100000, "company_id": 1}
        # r = client.post(f"{BASE_URL}/api/v1/inventory/", json=product, headers=headers)
        # print(f"Product created: {r.status_code}")
        
        print("--- 2. Crear servicio por 50000 en efectivo ---")
        # Implement repair/service creation
        
        print("--- 3. Invoicing ---")
        # Implement invoice creation
        
        print("--- 4. Compras ---")
        # Implement purchase creation
        
        print("--- 5. Asientos Contables ---")
        # Implement rent payment entry
        
        print("--- Accounting Review ---")
        # Act as accounting reviewer

if __name__ == "__main__":
    main()
