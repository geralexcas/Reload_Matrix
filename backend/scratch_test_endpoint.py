import httpx
import os

def test_endpoint():
    url = "http://localhost:8001/api/v1/accounting/libro-compras/"
    params = {"company_id": 1}
    # we might need auth headers
    # let's test if it needs auth
    response = httpx.get(url, params=params)
    print("Status:", response.status_code)
    print("JSON:", response.json())

if __name__ == "__main__":
    test_endpoint()
