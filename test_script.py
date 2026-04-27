#!/usr/bin/env python3

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://localhost:8001"
FRONTEND_URL = "http://localhost:8081"

# Credenciales (usaremos las que están en la base de datos)
ADMIN_CREDENTIALS = {
    "username": "admin@reloadmatrix.com",
    "password": "Admin@12345"  # Esta es la contraseña que deberíamos usar según el plan
}

TECHNICIAN_CREDENTIALS = {
    "username": "geralexcas@gmail.com",
    "password": "German22&"
}

# Credenciales de usuario de prueba que podemos crear
TEST_CREDENTIALS = {
    "username": "testuser",
    "password": "TestPass123!"
}

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
        return response
    except Exception as e:
        log_message(f"Error testing {endpoint}: {str(e)}", "ERROR")
        return None

def authenticate_user(credentials):
    """Authenticate user and return token"""
    auth_url = f"{BASE_URL}/api/v1/auth/token"
    
    try:
        # Primero intentamos con form-data como en el frontend
        response = requests.post(auth_url, 
                                data=f"username={credentials['username']}&password={credentials['password']}",
                                headers={"Content-Type": "application/x-www-form-urlencoded"})
        
        if response.status_code == 200:
            token_data = response.json()
            log_message(f"Authentication successful for {credentials['username']}")
            return token_data["access_token"]
        else:
            log_message(f"Authentication failed for {credentials['username']}: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_message(f"Authentication error: {str(e)}", "ERROR")
        return None

def test_authentication():
    """Test Case TC-001: Authentication and Access"""
    log_message("\n=== Testing Authentication (TC-001) ===")
    
    # Test admin authentication
    admin_token = authenticate_user(ADMIN_CREDENTIALS)
    
    # Test technician authentication  
    technician_token = authenticate_user(TECHNICIAN_CREDENTIALS)
    
    # Test with our test user
    test_token = authenticate_user(TEST_CREDENTIALS)
    
    if test_token:
        # Test protected endpoint with test token
        headers = {"Authorization": f"Bearer {test_token}"}
        response = test_api_endpoint("/api/v1/users/me", "GET", headers=headers)
        if response and response.status_code == 200:
            log_message("Test user can access protected endpoints")
            user_data = response.json()
            log_message(f"Authenticated as: {user_data['username']} ({user_data['email']})")
        else:
            log_message("Test user cannot access protected endpoints", "ERROR")
    
    return test_token, technician_token  # Usamos test_token como admin_token para pruebas

def test_create_user(admin_token):
    """Test Case TC-002: Create Users"""
    log_message("\n=== Testing User Creation (TC-002) ===")
    
    if not admin_token:
        log_message("No admin token available", "ERROR")
        return
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Create test users
    test_users = [
        {
            "username": "test_vendedor",
            "email": "vendedor@test.com",
            "password": "Pass123!",
            "full_name": "Vendedor Test",
            "role": "VENDEDOR"
        },
        {
            "username": "test_bodeguero", 
            "email": "bodeguero@test.com",
            "password": "Pass123!",
            "full_name": "Bodeguero Test",
            "role": "BODEGUERO"
        },
        {
            "username": "test_contador",
            "email": "contador@test.com",
            "password": "Pass123!",
            "full_name": "Contador Test",
            "role": "CONTADOR"
        }
    ]
    
    for user_data in test_users:
        response = test_api_endpoint("/api/v1/admin/users", "POST", user_data, headers)
        if response and response.status_code == 201:
            log_message(f"User {user_data['username']} created successfully")
        else:
            log_message(f"Failed to create user {user_data['username']}: {response.text if response else 'No response'}", "ERROR")

def test_create_suppliers(admin_token):
    """Test Case TC-003: Create Suppliers"""
    log_message("\n=== Testing Supplier Creation (TC-003) ===")
    
    if not admin_token:
        log_message("No admin token available", "ERROR")
        return
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Get company ID first (we need it for creating partners)
    company_response = test_api_endpoint("/api/v1/companies", "GET", headers=headers)
    
    if not company_response or company_response.status_code != 200:
        log_message("Cannot get company information", "ERROR")
        return
    
    companies = company_response.json()
    if not companies:
        log_message("No companies found", "ERROR")
        return
    
    company_id = companies[0]["id"]
    
    # Create test suppliers
    test_suppliers = [
        {
            "nit": "123456789",
            "dv": "0",
            "name": "Proveedor Tecnológico SA",
            "partner_type": "SUPPLIER",
            "responsibility_fiscal": "RESPONSABLE IVA",
            "address": "Calle 123, Bogotá",
            "phone": "3101234567",
            "email": "proveedor1@test.com",
            "credit_limit": 10000000.00,
            "company_id": company_id
        },
        {
            "nit": "987654321",
            "dv": "5", 
            "name": "Distribuidora Mayorista LTDA",
            "partner_type": "SUPPLIER",
            "responsibility_fiscal": "NO RESPONSABLE",
            "address": "Avenida 456, Medellín",
            "phone": "3209876543",
            "email": "proveedor2@test.com",
            "credit_limit": 5000000.00,
            "company_id": company_id
        }
    ]
    
    for supplier_data in test_suppliers:
        response = test_api_endpoint("/api/v1/partners", "POST", supplier_data, headers)
        if response and response.status_code == 201:
            log_message(f"Supplier {supplier_data['name']} created successfully")
        else:
            log_message(f"Failed to create supplier {supplier_data['name']}: {response.text if response else 'No response'}", "ERROR")

def test_create_purchase(admin_token):
    """Test Case TC-004: Create Purchase Invoice"""
    log_message("\n=== Testing Purchase Creation (TC-004) ===")
    
    if not admin_token:
        log_message("No admin token available", "ERROR")
        return
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # First, get a supplier
    suppliers_response = test_api_endpoint("/api/v1/partners?partner_type=SUPPLIER", "GET", headers=headers)
    
    if not suppliers_response or suppliers_response.status_code != 200:
        log_message("Cannot get suppliers", "ERROR")
        return
    
    suppliers = suppliers_response.json()
    if not suppliers:
        log_message("No suppliers found", "ERROR")
        return
    
    supplier_id = suppliers[0]["id"]
    
    # Create purchase data
    purchase_data = {
        "purchase_number": f"COMPRA-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "partner_id": supplier_id,
        "purchase_date": datetime.now().isoformat(),
        "due_date": datetime.now().isoformat(),
        "payment_method": "CREDIT",
        "items": [
            {
                "description": "Producto A",
                "quantity": 10.00,
                "unit_price": 100000.00,
                "tax_rate": 19.00,
                "line_total": 1190000.00  # 10 * 100000 * 1.19
            },
            {
                "description": "Producto B", 
                "quantity": 5.00,
                "unit_price": 200000.00,
                "tax_rate": 0.00,
                "line_total": 1000000.00  # 5 * 200000
            }
        ]
    }
    
    response = test_api_endpoint("/api/v1/purchases", "POST", purchase_data, headers)
    if response and response.status_code == 201:
        purchase = response.json()
        log_message(f"Purchase {purchase['purchase_number']} created successfully")
        log_message(f"Purchase ID: {purchase['id']}, Total: {purchase['total_amount']}")
        return purchase['id']
    else:
        log_message(f"Failed to create purchase: {response.text if response else 'No response'}", "ERROR")
        return None

def test_purchase_payment(admin_token, purchase_id):
    """Test Case TC-005: Purchase Payment"""
    log_message("\n=== Testing Purchase Payment (TC-005) ===")
    
    if not admin_token or not purchase_id:
        log_message("Missing admin token or purchase ID", "ERROR")
        return
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    payment_data = {
        "purchase_id": purchase_id,
        "payment_method": "BANK_TRANSFER",
        "amount": 1000000.00,
        "payment_date": datetime.now().isoformat(),
        "reference": "Pago parcial transferencia",
        "notes": "Pago parcial de factura"
    }
    
    response = test_api_endpoint("/api/v1/purchases/payments", "POST", payment_data, headers)
    if response and response.status_code == 201:
        payment = response.json()
        log_message(f"Payment of {payment['amount']} registered successfully")
        log_message(f"Payment ID: {payment['id']}")
    else:
        log_message(f"Failed to register payment: {response.text if response else 'No response'}", "ERROR")

def test_accounting_entries(admin_token):
    """Test Case TC-007/TC-008: Verify Accounting Entries"""
    log_message("\n=== Testing Accounting Entries (TC-007/TC-008) ===")
    
    if not admin_token:
        log_message("No admin token available", "ERROR")
        return
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    # Get journal entries
    entries_response = test_api_endpoint("/api/v1/accounting/journal-entries", "GET", headers=headers)
    
    if entries_response and entries_response.status_code == 200:
        entries = entries_response.json()
        log_message(f"Found {len(entries)} journal entries")
        
        for entry in entries:
            log_message(f"Entry {entry['id']}: {entry['description']} - Date: {entry['entry_date']}")
            
            # Get entry lines
            lines_response = test_api_endpoint(f"/api/v1/accounting/journal-entries/{entry['id']}/lines", "GET", headers=headers)
            if lines_response and lines_response.status_code == 200:
                lines = lines_response.json()
                for line in lines:
                    log_message(f"  - Account {line['account_id']}: Debit {line['debit_amount']}, Credit {line['credit_amount']}")
    else:
        log_message(f"Failed to get journal entries: {entries_response.text if entries_response else 'No response'}", "ERROR")
    
    # Get trial balance
    balance_response = test_api_endpoint("/api/v1/accounting/trial-balance", "GET", headers=headers)
    
    if balance_response and balance_response.status_code == 200:
        balance = balance_response.json()
        log_message(f"Trial balance generated with {len(balance)} accounts")
        
        total_debit = sum(account['debit_balance'] for account in balance)
        total_credit = sum(account['credit_balance'] for account in balance)
        
        log_message(f"Total Debit: {total_debit}, Total Credit: {total_credit}")
        
        if abs(total_debit - total_credit) < 0.01:  # Allow for floating point precision
            log_message("Trial balance is balanced!")
        else:
            log_message("Trial balance is NOT balanced!", "ERROR")
    else:
        log_message(f"Failed to get trial balance: {balance_response.text if balance_response else 'No response'}", "ERROR")

def main():
    """Main test execution"""
    log_message("Starting Business Management System Tests")
    log_message(f"Testing API at {BASE_URL}")
    log_message(f"Frontend at {FRONTEND_URL}")
    
    # Test authentication
    admin_token, technician_token = test_authentication()
    
    if not admin_token:
        log_message("Cannot proceed without admin authentication", "ERROR")
        return
    
    # Test user creation
    test_create_user(admin_token)
    
    # Test supplier creation
    test_create_suppliers(admin_token)
    
    # Test purchase creation
    purchase_id = test_create_purchase(admin_token)
    
    # Test purchase payment
    if purchase_id:
        test_purchase_payment(admin_token, purchase_id)
    
    # Test accounting entries
    test_accounting_entries(admin_token)
    
    log_message("\n=== Test Execution Completed ===")

if __name__ == "__main__":
    main()