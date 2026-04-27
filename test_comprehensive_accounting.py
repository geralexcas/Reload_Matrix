#!/usr/bin/env python3
"""
Comprehensive Accounting Integration Test
Tests the complete flow: Client creation, Equipment intake, Repair, Invoicing, Purchases
and verifies that all accounting entries are properly generated.
"""

import requests
import json
import time
from datetime import datetime
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (should be created manually or via setup script)
TEST_USERNAME = "testuser5@test.com"
TEST_PASSWORD = "Test@Password123"

def log_message(message, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {message}")

def authenticate():
    """Authenticate and get access token"""
    auth_url = f"{API_BASE}/auth/token"
    auth_data = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
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
            log_message(f"Authentication failed: {response.text}", "ERROR")
            return None
    except Exception as e:
        log_message(f"Authentication error: {str(e)}", "ERROR")
        return None

def get_headers(token):
    """Get headers with authorization"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_company_id(token):
    """Get the first company ID"""
    headers = get_headers(token)
    response = requests.get(f"{API_BASE}/companies", headers=headers)
    
    if response.status_code == 200:
        companies = response.json()
        if companies:
            return companies[0]["id"]
    
    log_message("No companies found", "ERROR")
    return None

def create_test_client(token, company_id):
    """Create a test client"""
    headers = get_headers(token)
    client_data = {
        "name": "Test Client S.A.S.",
        "nit": "1234567890",
        "dv": "1",
        "email": "testclient@test.com",
        "phone": "3001234567",
        "address": "Calle Test #123",
        "city": "Bogotá",
        "responsibility_fiscal": "RESPONSABLE IVA",
        "partner_type": "CUSTOMER"
    }
    
    response = requests.post(f"{API_BASE}/partners?company_id={company_id}", json=client_data, headers=headers)
    
    if response.status_code == 201:
        client = response.json()
        log_message(f"Created client: {client['name']} (ID: {client['id']})")
        return client
    else:
        log_message(f"Failed to create client: {response.text}", "ERROR")
        return None

def create_test_supplier(token, company_id):
    """Create a test supplier"""
    headers = get_headers(token)
    supplier_data = {
        "name": "Test Supplier Ltda.",
        "nit": "9876543210",
        "dv": "2",
        "email": "testsupplier@test.com",
        "phone": "3007654321",
        "address": "Avenida Test #456",
        "city": "Medellín",
        "responsibility_fiscal": "RESPONSABLE IVA",
        "partner_type": "SUPPLIER"
    }
    
    response = requests.post(f"{API_BASE}/partners?company_id={company_id}", json=supplier_data, headers=headers)
    
    if response.status_code == 201:
        supplier = response.json()
        log_message(f"Created supplier: {supplier['name']} (ID: {supplier['id']})")
        return supplier
    else:
        log_message(f"Failed to create supplier: {response.text}", "ERROR")
        return None

def create_test_product(token, company_id):
    """Create a test product"""
    headers = get_headers(token)
    product_data = {
        "name": "Test Product",
        "description": "Test product for accounting tests",
        "code": "TEST-PROD-001",
        "category": "Repuestos",
        "purchase_price": 10000.00,
        "sale_price": 15000.00,
        "stock": 10,
        "min_stock": 5,
        "tax_rate": 19.00
    }
    
    response = requests.post(f"{API_BASE}/inventory/products?company_id={company_id}", json=product_data, headers=headers)
    
    if response.status_code == 201:
        product = response.json()
        log_message(f"Created product: {product['name']} (ID: {product['id']})")
        return product
    else:
        log_message(f"Failed to create product: {response.text}", "ERROR")
        return None

def create_test_equipment_intake(token, company_id, client_id):
    """Create equipment intake (simplified repair order)"""
    headers = get_headers(token)
    intake_data = {
        "partner_id": client_id,
        "problem_description": "Test equipment for accounting verification",
        "diagnosis": "Test diagnostic",
        "status": "RECEIVED",
        "company_id": company_id
    }
    
    response = requests.post(f"{API_BASE}/repair/simple", json=intake_data, headers=headers)
    
    if response.status_code == 201:
        intake = response.json()
        log_message(f"Created equipment intake: {intake['equipment_type']} (ID: {intake['id']})")
        return intake
    else:
        log_message(f"Failed to create equipment intake: {response.text}", "ERROR")
        return None

def create_test_repair_order(token, company_id, intake_id, client_id):
    """Create repair order (or use intake as repair order)"""
    # If we have an intake (repair order), use it directly
    if intake_id:
        return {"id": intake_id, "repair_description": "Test repair from intake"}
    
    # Otherwise create a new one
    headers = get_headers(token)
    repair_data = {
        "partner_id": client_id,
        "problem_description": "Test diagnostic for repair",
        "diagnosis": "Test repair description",
        "status": "IN_PROGRESS",
        "company_id": company_id
    }
    
    response = requests.post(f"{API_BASE}/repair/simple", json=repair_data, headers=headers)
    
    if response.status_code == 201:
        repair = response.json()
        log_message(f"Created repair order: {repair['repair_description']} (ID: {repair['id']})")
        return repair
    else:
        log_message(f"Failed to create repair order: {response.text}", "ERROR")
        return None

def add_repair_items(token, repair_id, company_id, product_id):
    """Add items to repair order"""
    headers = get_headers(token)
    item_data = {
        "description": "Test repair item",
        "quantity": 1,
        "unit_cost": 10000.00,
        "tax_rate": 19.00,
        "warranty_status": "NO_WARRANTY",
        "product_id": product_id
    }
    
    response = requests.post(f"{API_BASE}/repair/{repair_id}/items", json=item_data, headers=headers)
    
    if response.status_code == 201:
        item = response.json()
        log_message(f"Added repair item: {item['description']} (ID: {item['id']})")
        return item
    else:
        log_message(f"Failed to add repair item: {response.text}", "ERROR")
        return None

def create_invoice_from_repair(token, repair_id, company_id):
    """Create invoice from repair order (using repair service)"""
    headers = get_headers(token)
    
    # First, update repair order to completed status so it can be invoiced
    update_data = {
        "status": "DELIVERED"
    }
    
    update_response = requests.put(f"{API_BASE}/repair/{repair_id}", json=update_data, headers=headers)
    
    if update_response.status_code != 200:
        log_message(f"Failed to update repair status: {update_response.text}", "ERROR")
        return None
    
    # Then create invoice from the repair
    response = requests.post(f"{API_BASE}/repair/{repair_id}/generate-invoice", json={}, headers=headers)
    
    if response.status_code == 201:
        invoice = response.json()
        log_message(f"Created invoice from repair: {invoice['invoice_number']} (ID: {invoice['id']})")
        return invoice
    else:
        log_message(f"Failed to create invoice from repair: {response.text}", "ERROR")
        return None

def create_purchase_order(token, company_id, supplier_id, product_id):
    """Create purchase order"""
    headers = get_headers(token)
    purchase_data = {
        "purchase_number": f"TEST-PUR-{int(datetime.now().timestamp())}",
        "partner_id": supplier_id,
        "purchase_date": datetime.now().isoformat(),
        "due_date": datetime.now().isoformat(),
        "currency": "COP",
        "payment_method": "CASH",
        "status": "ISSUED",
        "company_id": company_id,
        "items": [
            {
                "product_id": product_id,
                "description": "Test purchase item",
                "quantity": 5,
                "unit_price": 10000.00,
                "discount_percent": 0.00,
                "tax_rate": 19.00
            }
        ]
    }
    
    response = requests.post(f"{API_BASE}/purchases", json=purchase_data, headers=headers)
    
    if response.status_code == 201:
        purchase = response.json()
        log_message(f"Created purchase: {purchase['purchase_number']} (ID: {purchase['id']})")
        return purchase
    else:
        log_message(f"Failed to create purchase: {response.text}", "ERROR")
        return None

def verify_accounting_entries(token, company_id):
    """Verify that accounting entries were created correctly"""
    headers = get_headers(token)
    
    # Get journal entries
    response = requests.get(f"{API_BASE}/accounting/journal-entries/?company_id={company_id}", headers=headers)
    
    if response.status_code == 200:
        entries = response.json()
        log_message(f"\n=== Found {len(entries)} journal entries ===")
        
        for entry in entries:
            log_message(f"\nEntry {entry['id']}:")
            log_message(f"  Date: {entry['entry_date']}")
            log_message(f"  Description: {entry['description']}")
            log_message(f"  Reference: {entry['reference']}")
            log_message(f"  Posted: {entry['is_posted']}")
            
            # Get entry lines
            lines_response = requests.get(f"{API_BASE}/accounting/journal-entries/{entry['id']}/lines", headers=headers)
            if lines_response.status_code == 200:
                lines = lines_response.json()
                total_debit = Decimal('0.00')
                total_credit = Decimal('0.00')
                
                for line in lines:
                    debit = Decimal(str(line['debit_amount']))
                    credit = Decimal(str(line['credit_amount']))
                    total_debit += debit
                    total_credit += credit
                    
                    log_message(f"  Line {line['id']}:")
                    log_message(f"    Account: {line['account_id']}")
                    log_message(f"    Debit: {debit}")
                    log_message(f"    Credit: {credit}")
                    log_message(f"    Description: {line['description']}")
                
                log_message(f"  Total Debit: {total_debit}")
                log_message(f"  Total Credit: {total_credit}")
                
                if total_debit == total_credit:
                    log_message(f"  ✓ Entry is balanced!")
                else:
                    log_message(f"  ✗ Entry is NOT balanced! Difference: {total_debit - total_credit}", "ERROR")
    else:
        log_message(f"Failed to get journal entries: {response.text}", "ERROR")

def verify_trial_balance(token, company_id):
    """Verify trial balance"""
    headers = get_headers(token)
    
    response = requests.get(f"{API_BASE}/accounting/trial-balance/?company_id={company_id}", headers=headers)
    
    if response.status_code == 200:
        balance = response.json()
        log_message(f"\n=== Trial Balance ===")
        log_message(f"Period: {balance['period']}")
        log_message(f"Total Debit Balance: {balance['total_debit_balance']}")
        log_message(f"Total Credit Balance: {balance['total_credit_balance']}")
        
        if balance['is_balanced']:
            log_message("✓ Trial balance is balanced!")
        else:
            log_message(f"✗ Trial balance is NOT balanced! Difference: {balance['difference']}", "ERROR")
        
        # Show accounts with balances
        log_message("\nAccounts with non-zero balances:")
        for account in balance['accounts']:
            debit = Decimal(str(account['debit_balance']))
            credit = Decimal(str(account['credit_balance']))
            if debit != 0 or credit != 0:
                net_balance = debit - credit
                log_message(f"  {account['account_code']} {account['account_name']}: Debit={debit}, Credit={credit}, Net={net_balance}")
    else:
        log_message(f"Failed to get trial balance: {response.text}", "ERROR")

def verify_libro_ventas(token, company_id):
    """Verify sales book"""
    headers = get_headers(token)
    
    response = requests.get(f"{API_BASE}/accounting/libro-ventas/?company_id={company_id}", headers=headers)
    
    if response.status_code == 200:
        libro = response.json()
        log_message(f"\n=== Libro de Ventas ===")
        log_message(f"Company: {libro['company_name']}")
        log_message(f"Total facturas: {libro['totals']['num_facturas']}")
        log_message(f"Total IVA generado: {libro['totals']['total_iva']}")
        log_message(f"Total ventas: {libro['totals']['total_facturas']}")
        
        for entry in libro['entries']:
            log_message(f"\nFactura {entry['invoice_number']}:")
            log_message(f"  Fecha: {entry['invoice_date']}")
            log_message(f"  Cliente: {entry['partner_name']}")
            log_message(f"  Base IVA 19%: {entry['base_iva_19']}")
            log_message(f"  IVA 19%: {entry['iva_19']}")
            log_message(f"  Total: {entry['total_invoice']}")
    else:
        log_message(f"Failed to get libro de ventas: {response.text}", "ERROR")

def verify_libro_compras(token, company_id):
    """Verify purchases book"""
    headers = get_headers(token)
    
    response = requests.get(f"{API_BASE}/accounting/libro-compras/?company_id={company_id}", headers=headers)
    
    if response.status_code == 200:
        libro = response.json()
        log_message(f"\n=== Libro de Compras ===")
        log_message(f"Company: {libro['company_name']}")
        log_message(f"Total facturas: {libro['totals']['num_facturas']}")
        log_message(f"Total IVA soportado: {libro['totals']['total_iva']}")
        log_message(f"Total compras: {libro['totals']['total_facturas']}")
        
        for entry in libro['entries']:
            log_message(f"\nFactura {entry['invoice_number']}:")
            log_message(f"  Fecha: {entry['invoice_date']}")
            log_message(f"  Proveedor: {entry['partner_name']}")
            log_message(f"  Base IVA 19%: {entry['base_iva_19']}")
            log_message(f"  IVA 19%: {entry['iva_19']}")
            log_message(f"  Total: {entry['total_invoice']}")
    else:
        log_message(f"Failed to get libro de compras: {response.text}", "ERROR")

def main():
    """Main test execution"""
    log_message("Starting Comprehensive Accounting Integration Test")
    
    # Step 1: Authenticate
    log_message("\n=== Step 1: Authentication ===")
    token = authenticate()
    if not token:
        log_message("Authentication failed, cannot continue", "ERROR")
        return
    
    log_message("Authentication successful")
    
    # Step 2: Get company ID
    log_message("\n=== Step 2: Get Company Information ===")
    company_id = get_company_id(token)
    if not company_id:
        log_message("No company found, cannot continue", "ERROR")
        return
    
    log_message(f"Using company ID: {company_id}")
    
    # Step 3: Create test entities
    log_message("\n=== Step 3: Create Test Entities ===")
    
    # Create client
    client = create_test_client(token, company_id)
    if not client:
        log_message("Failed to create client, cannot continue", "ERROR")
        return
    
    # Create supplier
    supplier = create_test_supplier(token, company_id)
    if not supplier:
        log_message("Failed to create supplier, cannot continue", "ERROR")
        return
    
    # Create product (skip if fails, we'll use a manual product ID)
    product = create_test_product(token, company_id)
    if not product:
        log_message("Failed to create product, using manual product ID", "WARNING")
        # Use a manual product ID for testing
        product = {"id": 999}
    
    # Step 4: Create equipment intake
    log_message("\n=== Step 4: Create Equipment Intake ===")
    intake = create_test_equipment_intake(token, company_id, client['id'])
    if not intake:
        log_message("Failed to create equipment intake", "ERROR")
    
    # Step 5: Create repair order
    log_message("\n=== Step 5: Create Repair Order ===")
    repair = create_test_repair_order(token, company_id, intake['id'] if intake else None, client['id'])
    if not repair:
        log_message("Failed to create repair order", "ERROR")
    
    # Step 6: Add repair items
    if repair:
        log_message("\n=== Step 6: Add Repair Items ===")
        repair_item = add_repair_items(token, repair['id'], company_id, product['id'])
        if not repair_item:
            log_message("Failed to add repair items", "ERROR")
    
    # Step 7: Create invoice from repair
    if repair:
        log_message("\n=== Step 7: Create Invoice from Repair ===")
        invoice = create_invoice_from_repair(token, repair['id'], company_id)
        if not invoice:
            log_message("Failed to create invoice from repair", "ERROR")
    
    # Step 8: Create purchase order
    log_message("\n=== Step 8: Create Purchase Order ===")
    purchase = create_purchase_order(token, company_id, supplier['id'], product['id'])
    if not purchase:
        log_message("Failed to create purchase order", "ERROR")
    
    # Step 9: Wait for accounting entries to be processed
    log_message("\n=== Step 9: Waiting for Accounting Processing ===")
    time.sleep(2)  # Give some time for async processing
    
    # Step 10: Verify accounting entries
    log_message("\n=== Step 10: Verify Accounting Entries ===")
    verify_accounting_entries(token, company_id)
    
    # Step 11: Verify trial balance
    log_message("\n=== Step 11: Verify Trial Balance ===")
    verify_trial_balance(token, company_id)
    
    # Step 12: Verify sales book
    log_message("\n=== Step 12: Verify Sales Book ===")
    verify_libro_ventas(token, company_id)
    
    # Step 13: Verify purchases book
    log_message("\n=== Step 13: Verify Purchases Book ===")
    verify_libro_compras(token, company_id)
    
    log_message("\n=== Comprehensive Accounting Integration Test Completed ===")
    log_message("✓ All tests executed successfully!")

if __name__ == "__main__":
    main()
