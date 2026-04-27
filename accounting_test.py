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
    """Accounting verification test execution"""
    log_message("Starting Accounting Verification Tests")
    
    headers = {
        "Authorization": f"Bearer {test_token}",
        "Content-Type": "application/json"
    }
    
    # Get company ID
    log_message("\n=== Getting Company Information ===")
    response = test_api_endpoint("/api/v1/companies", "GET", headers=headers)
    if response and response.status_code == 200:
        companies = response.json()
        if companies:
            company_id = companies[0]["id"]
            log_message(f"Using company ID: {company_id}")
            
            # Test 1: Get detailed journal entries
            log_message("\n=== Test 1: Get Detailed Journal Entries ===")
            response = test_api_endpoint(f"/api/v1/accounting/journal-entries/?company_id={company_id}", "GET", headers=headers)
            if response and response.status_code == 200:
                entries = response.json()
                log_message(f"Found {len(entries)} journal entries")
                
                for entry in entries:
                    log_message(f"\nEntry {entry['id']}:")
                    log_message(f"  Date: {entry['entry_date']}")
                    log_message(f"  Description: {entry['description']}")
                    log_message(f"  Reference: {entry['reference']}")
                    log_message(f"  Posted: {entry['is_posted']}")
                    
                    # Get entry lines
                    lines_response = test_api_endpoint(f"/api/v1/accounting/journal-entries/{entry['id']}/lines", "GET", headers=headers)
                    if lines_response and lines_response.status_code == 200:
                        lines = lines_response.json()
                        log_message(f"  Lines: {len(lines)}")
                        total_debit = 0
                        total_credit = 0
                        
                        for line in lines:
                            log_message(f"    Account {line['account_id']}:")
                            log_message(f"      Description: {line['description']}")
                            log_message(f"      Debit: {line['debit_amount']}")
                            log_message(f"      Credit: {line['credit_amount']}")
                            total_debit += float(line['debit_amount'])
                            total_credit += float(line['credit_amount'])
                        
                        log_message(f"    Total Debit: {total_debit}")
                        log_message(f"    Total Credit: {total_credit}")
                        
                        if abs(total_debit - total_credit) < 0.01:
                            log_message(f"    ✓ Entry is balanced!")
                        else:
                            log_message(f"    ✗ Entry is NOT balanced! Difference: {total_debit - total_credit}", "ERROR")
            else:
                log_message("Could not get journal entries", "ERROR")
            
            # Test 2: Get chart of accounts
            log_message("\n=== Test 2: Get Chart of Accounts ===")
            response = test_api_endpoint(f"/api/v1/accounting/chart-of-accounts/?company_id={company_id}", "GET", headers=headers)
            if response and response.status_code == 200:
                accounts = response.json()
                log_message(f"Found {len(accounts)} accounts in chart")
                
                # Show some key accounts
                key_accounts = ["Caja", "Bancos", "Clientes", "Proveedores", "Ventas", "Compras", "IVA"]
                for account in accounts:
                    if any(keyword.lower() in account['name'].lower() for keyword in key_accounts):
                        log_message(f"  {account['code']} - {account['name']} (Type: {account['account_type']})")
            else:
                log_message("Could not get chart of accounts", "ERROR")
            
            # Test 3: Get trial balance
            log_message("\n=== Test 3: Get Trial Balance ===")
            response = test_api_endpoint(f"/api/v1/accounting/trial-balance/?company_id={company_id}", "GET", headers=headers)
            if response and response.status_code == 200:
                balance = response.json()
                log_message(f"Trial balance generated with {len(balance)} accounts")
                
                total_debit = sum(float(account['debit_balance']) for account in balance)
                total_credit = sum(float(account['credit_balance']) for account in balance)
                
                log_message(f"Total Debit Balance: {total_debit}")
                log_message(f"Total Credit Balance: {total_credit}")
                
                if abs(total_debit - total_credit) < 0.01:
                    log_message("✓ Trial balance is balanced!")
                else:
                    log_message(f"✗ Trial balance is NOT balanced! Difference: {total_debit - total_credit}", "ERROR")
                
                # Show accounts with balances
                log_message("\nAccounts with non-zero balances:")
                for account in balance:
                    debit = float(account['debit_balance'])
                    credit = float(account['credit_balance'])
                    if debit != 0 or credit != 0:
                        net_balance = debit - credit
                        log_message(f"  {account['account_code']} {account['account_name']}: Debit={debit}, Credit={credit}, Net={net_balance}")
            else:
                log_message("Could not get trial balance", "ERROR")
            
            # Test 4: Verify purchase-related accounting entries
            log_message("\n=== Test 4: Verify Purchase-Related Entries ===")
            
            # Get recent purchases
            purchases_response = test_api_endpoint(f"/api/v1/purchases/?company_id={company_id}", "GET", headers=headers)
            if purchases_response and purchases_response.status_code == 200:
                purchases = purchases_response.json()
                log_message(f"Found {len(purchases)} purchases")
                
                # Look for our test purchases
                test_purchases = [p for p in purchases if p['purchase_number'].startswith('TEST-')]
                log_message(f"Found {len(test_purchases)} test purchases")
                
                for purchase in test_purchases:
                    log_message(f"\nPurchase {purchase['purchase_number']}:")
                    log_message(f"  Partner: {purchase['partner']['name'] if purchase.get('partner') else 'N/A'}")
                    log_message(f"  Date: {purchase['purchase_date']}")
                    log_message(f"  Total: {purchase['total_amount']}")
                    log_message(f"  Status: {purchase['status']}")
                    
                    # Check if this purchase has accounting entries
                    # We would need to look for entries with the purchase number in reference
                    log_message(f"  Items: {len(purchase['items'])}")
                    for item in purchase['items']:
                        log_message(f"    - {item['description']}: {item['quantity']} x {item['unit_price']} = {item['line_total']}")
            else:
                log_message("Could not get purchases", "ERROR")
    else:
        log_message("Could not get companies", "ERROR")
    
    log_message("\n=== Accounting Verification Completed ===")

if __name__ == "__main__":
    main()