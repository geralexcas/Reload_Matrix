#!/usr/bin/env python3
"""
Setup script to create a test user for accounting tests
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

# Admin credentials (should be created manually first)
ADMIN_USERNAME = "testadmin"
ADMIN_PASSWORD = "Test@1234"

# Test user to create
TEST_USERNAME = "testuser5@test.com"
TEST_PASSWORD = "Test@Password123"
TEST_FULL_NAME = "Test User 5"

def log_message(message, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {message}")

def authenticate_admin():
    """Authenticate as admin"""
    auth_url = f"{API_BASE}/auth/token"
    auth_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    try:
        # Use form data for OAuth2 password flow
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(auth_url, data=auth_data, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            return token_data["access_token"]
        else:
            log_message(f"Admin authentication failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_message(f"Admin authentication error: {str(e)}", "ERROR")
        return None

def create_test_user(token):
    """Create test user"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    user_data = {
        "email": TEST_USERNAME,
        "username": TEST_USERNAME.split("@")[0],  # Use email prefix as username
        "password": TEST_PASSWORD,
        "full_name": TEST_FULL_NAME,
        "role": "VENDEDOR",
        "is_active": True,
        "is_superuser": False
    }
    
    response = requests.post(f"{API_BASE}/admin/users", json=user_data, headers=headers)
    
    if response.status_code == 201:
        user = response.json()
        log_message(f"Created test user: {user['email']} (ID: {user['id']})")
        return user
    else:
        log_message(f"Failed to create test user: {response.text}", "ERROR")
        return None

def create_test_company(token):
    """Create test company"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    company_data = {
        "name": "Test Company 2 S.A.S.",
        "nit": "987654321",
        "dv": "2",
        "legal_representative": "Jane Doe",
        "fecha_inicio_actividades": "2024-01-01",
        "email": "testcompany2@test.com",
        "phone": "3007654321",
        "address": "Calle Test #456",
        "city": "Medellín",
        "regimen": "COMUN",
        "responsibility_fiscal": "RESPONSABLE_DE_IVA"
    }
    
    response = requests.post(f"{API_BASE}/companies", json=company_data, headers=headers)
    
    if response.status_code == 201:
        company = response.json()
        log_message(f"Created test company: {company['name']} (ID: {company['id']})")
        return company
    else:
        log_message(f"Failed to create test company: {response.text}", "ERROR")
        return None

def assign_user_to_company(token, user_id, company_id):
    """Assign user to company"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # First, get available permissions
    response = requests.get(f"{API_BASE}/admin/permissions/", headers=headers)
    
    if response.status_code != 200:
        log_message(f"Failed to get permissions list: {response.text}", "ERROR")
        return False
    
    permissions_list = response.json()
    log_message(f"Available permissions: {[p['name'] for p in permissions_list]}")
    
    # Assign basic permissions by name (we need to find permission IDs)
    required_permissions = [
        "view_company",
        "manage_clients", 
        "manage_suppliers",
        "manage_products",
        "manage_repairs",
        "manage_invoices",
        "manage_purchases",
        "view_accounting"
    ]
    
    for perm_name in required_permissions:
        # Find permission by name
        perm = next((p for p in permissions_list if p['name'] == perm_name), None)
        if perm:
            # Assign permission
            assign_response = requests.post(
                f"{API_BASE}/admin/users/{user_id}/permissions/{perm['id']}",
                headers=headers
            )
            if assign_response.status_code == 200:
                log_message(f"Assigned permission: {perm_name}")
            else:
                log_message(f"Failed to assign {perm_name}: {assign_response.text}", "ERROR")
        else:
            log_message(f"Permission not found: {perm_name}", "ERROR")
    
    return True
    
    if response.status_code == 200:
        log_message(f"Assigned permissions to user {user_id} for company {company_id}")
        return True
    else:
        log_message(f"Failed to assign permissions: {response.text}", "ERROR")
        return False

def main():
    """Main setup execution"""
    log_message("Starting Test User Setup")
    
    # Step 1: Authenticate as admin
    log_message("\n=== Step 1: Admin Authentication ===")
    token = authenticate_admin()
    if not token:
        log_message("Admin authentication failed, cannot continue", "ERROR")
        return
    
    log_message("Admin authentication successful")
    
    # Step 2: Create test user
    log_message("\n=== Step 2: Create Test User ===")
    user = create_test_user(token)
    if not user:
        log_message("Failed to create test user", "ERROR")
        return
    
    # Step 3: Create test company
    log_message("\n=== Step 3: Create Test Company ===")
    company = create_test_company(token)
    if not company:
        log_message("Failed to create test company", "ERROR")
        return
    
    # Step 4: Assign user to company
    log_message("\n=== Step 4: Assign User to Company ===")
    success = assign_user_to_company(token, user['id'], company['id'])
    if not success:
        log_message("Failed to assign user to company", "ERROR")
        return
    
    log_message("\n=== Test User Setup Completed ===")
    log_message(f"Test credentials:")
    log_message(f"  Username: {TEST_USERNAME}")
    log_message(f"  Password: {TEST_PASSWORD}")
    log_message(f"  Company ID: {company['id']}")
    log_message("\nYou can now run the comprehensive accounting test!")

if __name__ == "__main__":
    main()
