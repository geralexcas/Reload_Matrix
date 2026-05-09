import httpx
import os

def login_and_test():
    url = "http://localhost:8001"
    
    # Login
    login_data = {
        "username": "admin@example.com",
        "password": "adminpassword"
    }
    with httpx.Client() as client:
        r = client.post(f"{url}/api/v1/auth/login", data=login_data)
        if r.status_code != 200:
            print("Login failed:", r.status_code, r.text)
            return
            
        token = r.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get libro-compras
        r2 = client.get(f"{url}/api/v1/accounting/libro-compras/?company_id=1", headers=headers)
        print("Status:", r2.status_code)
        if r2.status_code != 200:
            print("Error details:", r2.text)
        else:
            print("Success!")
            # print(r2.json())

if __name__ == "__main__":
    login_and_test()
