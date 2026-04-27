# Comprehensive Accounting Integration Test

This test suite verifies that all business operations (client creation, equipment intake, repairs, invoicing, purchases) properly generate accounting entries according to Colombian accounting standards.

## Test Coverage

The test covers:

1. **Client Creation** - Creates test clients for repairs
2. **Supplier Creation** - Creates test suppliers for purchases
3. **Product Creation** - Creates test products for inventory
4. **Equipment Intake** - Receives equipment from clients
5. **Repair Orders** - Creates repair orders with items
6. **Invoicing** - Generates invoices from repairs
7. **Purchases** - Creates purchase orders from suppliers
8. **Accounting Verification** - Validates all accounting entries

## Accounting Verification

The test verifies:

- **Journal Entries**: All transactions create proper double-entry accounting
- **Trial Balance**: Debits equal credits across all accounts
- **Sales Book (Libro de Ventas)**: Proper IVA generation and reporting
- **Purchases Book (Libro de Compras)**: Proper IVA support and reporting
- **Account Balances**: Proper classification by account type

## Prerequisites

1. Running application at `http://localhost:8081`
2. Admin user created (email: `admin@admin.com`, password: `admin`)
3. Python 3.8+ with `requests` library

## Setup

### Step 1: Install dependencies

```bash
pip install requests
```

### Step 2: Setup test user and company

Run the setup script to create a test user and company:

```bash
python setup_test_user.py
```

This will create:
- Test user: `testuser@test.com` / `testpassword123`
- Test company with proper permissions

### Step 3: Run the comprehensive test

```bash
python test_comprehensive_accounting.py
```

## Expected Accounting Entries

### From Repair Invoicing (Régimen Común)

**Debit**: Cuentas por cobrar (1130) - Total amount
**Credit**: Ingresos por ventas (4100) - Subtotal
**Credit**: Obligaciones fiscales / IVA (2130) - Tax amount

### From Purchases (Régimen Común)

**Debit**: Inventarios (1140) - Subtotal
**Debit**: IVA soportado (2408) - Tax amount
**Credit**: Cuentas por pagar (2205) / Efectivo / Bancos - Total amount

### From Inventory Usage in Repairs

**Debit**: Costo de ventas (5100) - Cost of parts
**Credit**: Inventarios (1140) - Cost of parts

## Test Output

The test will output:

1. Detailed journal entries with line items
2. Trial balance verification
3. Sales book entries
4. Purchases book entries
5. Balance verification for each entry

## Troubleshooting

### Authentication Issues

- Verify the application is running at `http://localhost:8081`
- Check that the admin user exists
- Verify CORS settings allow requests from localhost

### Permission Issues

- Ensure the test user has proper permissions
- Run the setup script again if permissions are missing

### API Endpoint Issues

- Check that all API endpoints are accessible
- Verify the backend is properly configured
- Check application logs for errors

## Manual Verification

After running the test, you can manually verify:

1. **Database**: Check `journal_entries` and `journal_entry_lines` tables
2. **UI**: Navigate to accounting reports in the web interface
3. **API**: Use tools like Postman to query accounting endpoints

## Technical Details

### Accounting Service

The `AccountingService` class handles:
- Automatic journal entry creation from business transactions
- Trial balance generation
- Colombian regulatory reports (Libro de Ventas, Libro de Compras)
- IVA declarations and withholding tax reports

### Key Methods

- `create_journal_entry_from_invoice()`: Creates entries from sales
- `create_journal_entry_from_purchase()`: Creates entries from purchases
- `create_inventory_journal_entry()`: Creates entries from inventory usage
- `get_trial_balance()`: Generates trial balance report
- `get_libro_ventas()`: Generates sales book
- `get_libro_compras()`: Generates purchases book

## Colombian Accounting Standards Compliance

The test verifies compliance with:

- **Decreto 2420/2015**: Accounting regulations
- **Art. 1.6.1.4.1 ET**: General accounting standards
- **Art. 1.6.1.4.10 ET**: Sales and purchases books
- **Art. 437, 468, 486 ET**: IVA declarations
- **Art. 368, 401 ET**: Withholding tax regulations

## Expected Results

✅ All journal entries should be balanced (debits = credits)
✅ Trial balance should be balanced
✅ Sales book should show proper IVA generation
✅ Purchases book should show proper IVA support
✅ All transactions should be properly classified by account type
