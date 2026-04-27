#!/usr/bin/env python3
"""
Test script to verify SQL injection resistance in the application.
This script tests various endpoints to ensure they are not vulnerable to SQL injection.
"""

import requests
import sys

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "password": "TestPass123!"
}

# SQL Injection payloads to test
SQL_INJECTION_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1 --",
    "' OR 1=1 #",
    "admin' --",
    "' UNION SELECT username, password FROM users --",
    "' UNION SELECT 1, version() --",
    "' UNION SELECT 1, table_name FROM information_schema.tables --",
]

def test_login_sql_injection():
    """Test login endpoint for SQL injection vulnerabilities."""
    print("\n=== Testing Login Endpoint for SQL Injection ===")
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test with username injection
        response = requests.post(
            f"{BASE_URL}/api/v1/token",
            data={"username": payload, "password": "anything"}
        )
        
        if response.status_code == 200:
            print(f"❌ VULNERABLE: Login succeeded with payload: {payload}")
            print(f"Response: {response.json()}")
            return False
        elif response.status_code == 401:
            print(f"✅ SAFE: Login failed as expected with payload: {payload}")
        else:
            print(f"⚠️  UNEXPECTED: Status code {response.status_code} for payload: {payload}")
    
    return True

def test_user_registration_sql_injection():
    """Test user registration endpoint for SQL injection vulnerabilities."""
    print("\n=== Testing User Registration Endpoint for SQL Injection ===")
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test with username injection
        response = requests.post(
            f"{BASE_URL}/api/v1/usuarios/",
            json={
                "username": payload,
                "email": f"{payload}@test.com",
                "password": "TestPass123!",
                "full_name": "Test User"
            }
        )
        
        if response.status_code == 201:
            print(f"❌ VULNERABLE: Registration succeeded with payload: {payload}")
            print(f"Response: {response.json()}")
            return False
        elif response.status_code == 400 or response.status_code == 422:
            print(f"✅ SAFE: Registration failed as expected with payload: {payload}")
        else:
            print(f"⚠️  UNEXPECTED: Status code {response.status_code} for payload: {payload}")
    
    return True

def test_company_endpoints_sql_injection():
    """Test company-related endpoints for SQL injection vulnerabilities."""
    print("\n=== Testing Company Endpoints for SQL Injection ===")
    
    # First, get a valid token
    auth_response = requests.post(
        f"{BASE_URL}/api/v1/token",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]}
    )
    
    if auth_response.status_code != 200:
        print("⚠️  Could not authenticate for company tests")
        return True
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test company creation with injected name
        response = requests.post(
            f"{BASE_URL}/api/v1/empresas/",
            json={
                "nombre": payload,
                "nit": "123456789",
                "direccion": "Test Address",
                "telefono": "1234567890",
                "email": "test@company.com",
                "usuario_admin": {
                    "username": "admin",
                    "password": "AdminPass123!",
                    "email": "admin@company.com",
                    "full_name": "Admin User"
                }
            },
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"❌ VULNERABLE: Company creation succeeded with payload: {payload}")
            print(f"Response: {response.json()}")
            return False
        elif response.status_code == 400 or response.status_code == 422:
            print(f"✅ SAFE: Company creation failed as expected with payload: {payload}")
        else:
            print(f"⚠️  UNEXPECTED: Status code {response.status_code} for payload: {payload}")
    
    return True

def test_accounting_endpoints_sql_injection():
    """Test accounting endpoints for SQL injection vulnerabilities."""
    print("\n=== Testing Accounting Endpoints for SQL Injection ===")
    
    # First, get a valid token
    auth_response = requests.post(
        f"{BASE_URL}/api/v1/token",
        data={"username": TEST_USER["username"], "password": TEST_USER["password"]}
    )
    
    if auth_response.status_code != 200:
        print("⚠️  Could not authenticate for accounting tests")
        return True
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test chart of accounts creation with injected name
        response = requests.post(
            f"{BASE_URL}/api/v1/contabilidad/plan-de-cuentas/",
            json={
                "empresa_id": 1,
                "codigo": payload,
                "nombre": payload,
                "tipo": "ACTIVO",
                "saldo_normal": "DEBITO"
            },
            headers=headers
        )
        
        if response.status_code == 201:
            print(f"❌ VULNERABLE: Chart of accounts creation succeeded with payload: {payload}")
            print(f"Response: {response.json()}")
            return False
        elif response.status_code == 400 or response.status_code == 422:
            print(f"✅ SAFE: Chart of accounts creation failed as expected with payload: {payload}")
        else:
            print(f"⚠️  UNEXPECTED: Status code {response.status_code} for payload: {payload}")
    
    return True

def main():
    """Run all SQL injection tests."""
    print("=" * 60)
    print("SQL Injection Vulnerability Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Test login endpoint
    if not test_login_sql_injection():
        all_passed = False
    
    # Test user registration endpoint
    if not test_user_registration_sql_injection():
        all_passed = False
    
    # Test company endpoints
    if not test_company_endpoints_sql_injection():
        all_passed = False
    
    # Test accounting endpoints
    if not test_accounting_endpoints_sql_injection():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED: No SQL injection vulnerabilities detected")
    else:
        print("❌ VULNERABILITIES DETECTED: SQL injection vulnerabilities found")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
