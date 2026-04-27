#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8001"

# Token que obtuvimos manualmente
test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTc3NzE3MDQ1N30.ajWn7LGpRRBT7tvEKm7O_KoFXqCsE_TM6GJ3945bOcY"

def log_message(message, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {message}")

def test_api_endpoint(endpoint, method="GET", data=None, headers=None):
    """Test a generic API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        
        log_message(f"{method} {endpoint} - Status: {response.status_code}")
        if response.status_code != 200 and response.status_code != 201:
            log_message(f"Response: {response.text}", "DEBUG")
        return response
    except Exception as e:
        log_message(f"Error testing {endpoint}: {str(e)}", "ERROR")
        return None

def main():
    """Simple test execution"""
    log_message("Starting Simple API Tests")
    
    headers = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get user info
    log_message("\n=== Test 1: Get User Info ===")
    response = test_api_endpoint("/api/v1/users/me", "GET", headers=headers)
    if response and response.status_code == 200:
        user_data = response.json()
        log_message(f"Authenticated as: {user_data.get('username', 'N/A')} ({user_data.get('email', 'N/A')})")
        log_message(f"Role: {user_data.get('role', 'N/A')}")
    
    # Test 2: Get companies
    log_message("\n=== Test 2: Get Companies ===")
    response = test_api_endpoint("/api/v1/companies", "GET", headers=headers)
    if response and response.status_code == 200:
        companies = response.json()
        log_message(f"Found {len(companies)} companies")
        if companies:
            company_id = companies[0]["id"]
            log_message(f"Using company ID: {company_id}")
            
            # Test 3: Get partners (suppliers)
            log_message("\n=== Test 3: Get Partners (Suppliers) ===")
            response = test_api_endpoint(f"/api/v1/partners/?company_id={company_id}", "GET", headers=headers)
            if response and response.status_code == 200:
                partners = response.json()
                log_message(f"Found {len(partners)} partners")
                for partner in partners:
                    log_message(f"  - {partner['name']} ({partner['partner_type']})")
            
            # Test 4: Create a test supplier
            log_message("\n=== Test 4: Create Test Supplier ===")
            supplier_data = {
                "nit": "123456789-0",  # Solo dígitos y guión
                "dv": "0",
                "name": "Proveedor de Prueba SA",
                "partner_type": "SUPPLIER",
                "responsibility_fiscal": "RESPONSABLE IVA",
                "address": "Calle Test 123",
                "phone": "3101234567",
                "email": "proveedor.prueba@test.com",
                "credit_limit": 1000000.00,
                "company_id": company_id
            }
            
            # Necesitamos enviar company_id como parámetro de query
            response = test_api_endpoint(f"/api/v1/partners/?company_id={company_id}", "POST", supplier_data, headers)
            if response and response.status_code == 201:
                supplier = response.json()
                log_message(f"Supplier created successfully: {supplier['name']} (ID: {supplier['id']})")
                
                # Test 5: Create a test purchase
                log_message("\n=== Test 5: Create Test Purchase ===")
                purchase_data = {
                    "purchase_number": f"TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                    "partner_id": supplier["id"],
                    "purchase_date": datetime.now().isoformat(),
                    "due_date": datetime.now().isoformat(),
                    "payment_method": "CREDIT",
                    "items": [
                        {
                            "description": "Producto de Prueba A",
                            "quantity": 5.00,
                            "unit_price": 100000.00,
                            "tax_rate": 19.00,
                            "line_total": 595000.00  # 5 * 100000 * 1.19
                        }
                    ]
                }
                
                response = test_api_endpoint(f"/api/v1/purchases/?company_id={company_id}", "POST", purchase_data, headers)
                if response and response.status_code == 201:
                    purchase = response.json()
                    log_message(f"Purchase created successfully: {purchase['purchase_number']}")
                    log_message(f"Purchase ID: {purchase['id']}, Total: {purchase['total_amount']}")
                    
                    # Test 6: Check accounting entries
                    log_message("\n=== Test 6: Check Accounting Entries ===")
                    response = test_api_endpoint(f"/api/v1/accounting/journal-entries/?company_id={company_id}", "GET", headers=headers)
                    if response and response.status_code == 200:
                        entries = response.json()
                        log_message(f"Found {len(entries)} journal entries")
                        for entry in entries:
                            log_message(f"  Entry {entry['id']}: {entry['description']}")
                    else:
                        log_message("Could not get journal entries", "ERROR")
                else:
                    log_message(f"Failed to create purchase: {response.text if response else 'No response'}", "ERROR")
            else:
                log_message(f"Failed to create supplier: {response.text if response else 'No response'}", "ERROR")
    else:
        log_message("Could not get companies", "ERROR")
    
    log_message("\n=== Simple Test Execution Completed ===")

if __name__ == "__main__":
    main()