# 🧾 Comprehensive Accounting Integration Test Suite

## 📋 Overview

This test suite provides comprehensive testing of the accounting integration in the reload_Matrix application. It verifies that all business operations properly generate accounting entries according to Colombian accounting standards (Decreto 2420/2015, Estatuto Tributario).

## 🎯 Test Objectives

1. **Verify Double-Entry Accounting**: Ensure all transactions create balanced journal entries
2. **Validate Regulatory Compliance**: Confirm compliance with Colombian accounting standards
3. **Test End-to-End Flow**: Test complete business processes from start to finish
4. **Validate Financial Reports**: Verify trial balance, sales book, and purchases book
5. **Ensure Data Integrity**: Confirm all financial data is properly recorded and balanced

## 📦 Test Suite Components

### Core Test Files

| File | Purpose |
|------|---------|
| `test_comprehensive_accounting.py` | Main test script with complete business flow |
| `setup_test_user.py` | Setup script for test environment |
| `test_api_connectivity.py` | Basic connectivity verification |
| `run_all_tests.sh` | Orchestration script for all tests |

### Documentation Files

| File | Purpose |
|------|---------|
| `ACCOUNTING_TEST_INSTRUCTIONS.md` | Detailed test execution instructions |
| `TEST_FILES_SUMMARY.md` | Summary of all test files |
| `ACCOUNTING_TEST_README.md` | This file - main overview |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- Running application at `http://localhost:8081`
- Admin user credentials (default: `admin@admin.com` / `admin`)

### Run All Tests

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

### Run Individual Tests

1. **Connectivity Test**
```bash
python test_api_connectivity.py
```

2. **Setup Test Environment**
```bash
python setup_test_user.py
```

3. **Run Comprehensive Test**
```bash
python test_comprehensive_accounting.py
```

## 🧪 What Gets Tested

### Business Operations

1. **Client Management**
   - Client creation with proper fiscal information
   - Client data validation

2. **Supplier Management**
   - Supplier creation with fiscal data
   - Supplier classification

3. **Product Management**
   - Product creation with inventory tracking
   - Tax rate configuration

4. **Equipment Intake**
   - Equipment reception from clients
   - Initial diagnostic recording

5. **Repair Processing**
   - Repair order creation
   - Adding repair items and parts
   - Labor and parts cost tracking

6. **Invoicing**
   - Invoice generation from repairs
   - IVA calculation and breakdown
   - Invoice status management

7. **Purchasing**
   - Purchase order creation
   - Supplier invoice processing
   - Inventory updates

### Accounting Verification

1. **Journal Entries**
   - Automatic entry creation from business transactions
   - Debit/credit balance verification
   - Proper account classification

2. **Trial Balance**
   - Total debit = total credit verification
   - Account balance calculation
   - Period filtering

3. **Sales Book (Libro de Ventas)**
   - Sales invoice registration
   - IVA generation tracking
   - Customer information

4. **Purchases Book (Libro de Compras)**
   - Purchase invoice registration
   - IVA support tracking
   - Supplier information

5. **Financial Reports**
   - Balance sheet verification
   - Income statement validation
   - Tax compliance reports

## 📊 Expected Accounting Entries

### From Sales (Repair Invoicing)

**Régimen Común (Common Regime)**:
```
DEBIT: Cuentas por cobrar (1130) - Total amount
CREDIT: Ingresos por ventas (4100) - Subtotal
CREDIT: Obligaciones fiscales / IVA (2130) - Tax amount
```

**Régimen Simple (Simple Regime)**:
```
DEBIT: Cuentas por cobrar (1130) - Total amount
CREDIT: Ingresos por ventas (4100) - Total amount
```

### From Purchases

**Régimen Común (Common Regime)**:
```
DEBIT: Inventarios (1140) - Subtotal
DEBIT: IVA soportado (2408) - Tax amount
CREDIT: Cuentas por pagar (2205) / Efectivo / Bancos - Total amount
```

**Régimen Simple (Simple Regime)**:
```
DEBIT: Inventarios (1140) - Total amount
CREDIT: Cuentas por pagar (2205) / Efectivo / Bancos - Total amount
```

### From Inventory Usage

```
DEBIT: Costo de ventas (5100) - Cost of parts
CREDIT: Inventarios (1140) - Cost of parts
```

## 📚 Colombian Accounting Standards Coverage

The test suite verifies compliance with:

### Primary Regulations
- **Decreto 2420 de 2015**: General accounting regulations
- **Estatuto Tributario (ET)**: Tax regulations

### Specific Articles
- **Art. 1.6.1.4.1 ET**: General accounting standards
- **Art. 1.6.1.4.10 ET**: Sales and purchases books
- **Art. 437, 468, 486 ET**: IVA declarations
- **Art. 368, 401 ET**: Withholding tax regulations
- **Art. 287, 631 ET**: Income classification

### Regulatory Reports
- **Libro de Ventas**: Sales registration with IVA breakdown
- **Libro de Compras**: Purchases registration with IVA support
- **Declaración de IVA**: IVA declaration (Form 300 DIAN)
- **Libro Mayor**: General ledger with account balances
- **Balance de Prueba**: Trial balance verification

## 🔍 Test Validation Criteria

### ✅ Success Criteria

1. **All journal entries are balanced** (debits = credits)
2. **Trial balance is balanced** (total debits = total credits)
3. **Sales book shows proper IVA generation**
4. **Purchases book shows proper IVA support**
5. **All accounts are properly classified by type**
6. **Financial reports match expected values**
7. **All business transactions generate accounting entries**

### ❌ Failure Criteria

1. **Unbalanced journal entries**
2. **Missing accounting entries for business transactions**
3. **Incorrect account classification**
4. **IVA calculation errors**
5. **Trial balance imbalance**
6. **API connectivity issues**
7. **Authentication failures**

## 🛠️ Troubleshooting

### Common Issues

**Authentication Failed**
- Verify admin credentials in `setup_test_user.py`
- Ensure application is running and accessible
- Check CORS settings in backend

**Permission Denied**
- Run `setup_test_user.py` again
- Verify user has proper company permissions
- Check database for user-company associations

**API Endpoint Not Found**
- Verify application routes in backend
- Check for typos in API URLs
- Ensure backend is properly configured

**Database Connection Issues**
- Verify database configuration
- Check database service is running
- Review connection strings and credentials

**Missing Required Fields**
- Check API schemas for required fields
- Verify all mandatory fields are provided
- Review error messages for specific missing fields

## 📈 Test Results Interpretation

### Journal Entries Output
```
Entry 123:
  Date: 2024-01-15 10:30:00
  Description: Factura por reparación - Orden #456
  Reference: INV-000456
  Posted: True
  
  Line 789:
    Account: 1130 (Cuentas por cobrar)
    Debit: 119000.00
    Credit: 0.00
    Description: Cuentas por cobrar - Factura INV-000456
  
  Line 790:
    Account: 4100 (Ingresos por ventas)
    Debit: 0.00
    Credit: 100000.00
    Description: Ingresos por servicios - Factura INV-000456
  
  Line 791:
    Account: 2130 (Obligaciones fiscales)
    Debit: 0.00
    Credit: 19000.00
    Description: IVA generado - Factura INV-000456
  
  Total Debit: 119000.00
  Total Credit: 119000.00
  ✓ Entry is balanced!
```

### Trial Balance Output
```
=== Trial Balance ===
Period: All time
Total Debit Balance: 500000.00
Total Credit Balance: 500000.00
✓ Trial balance is balanced!

Accounts with non-zero balances:
  111001 Caja principal: Debit=150000.00, Credit=0.00, Net=150000.00
  1130 Cuentas por cobrar: Debit=119000.00, Credit=0.00, Net=119000.00
  1140 Inventarios: Debit=100000.00, Credit=50000.00, Net=50000.00
  2130 Obligaciones fiscales: Debit=0.00, Credit=19000.00, Net=-19000.00
  2205 Cuentas por pagar: Debit=0.00, Credit=119000.00, Net=-119000.00
  4100 Ingresos por ventas: Debit=0.00, Credit=100000.00, Net=-100000.00
  5100 Costo de ventas: Debit=50000.00, Credit=0.00, Net=50000.00
```

## 🔧 Customization

### Test Configuration

Modify these variables in test scripts:

**`test_comprehensive_accounting.py`**:
- `BASE_URL`: Change if application runs on different URL
- `TEST_USERNAME`/`TEST_PASSWORD`: Test user credentials
- Test data (client names, product details, etc.)

**`setup_test_user.py`**:
- `ADMIN_USERNAME`/`ADMIN_PASSWORD`: Admin credentials
- `TEST_USERNAME`/`TEST_PASSWORD`: Test user to create
- Company and user details

### Adding New Tests

To add new test scenarios:

1. **Create new test functions** in `test_comprehensive_accounting.py`
2. **Add test calls** to the `main()` function
3. **Update documentation** in `ACCOUNTING_TEST_INSTRUCTIONS.md`
4. **Add to orchestration** script if needed

## 📖 Additional Resources

### Colombian Accounting Standards
- [Decreto 2420 de 2015](https://www.funcionpublica.gov.co/)
- [Estatuto Tributario](https://www.dian.gov.co/)
- [Normas Internacionales de Información Financiera (NIIF)](https://www.ifrs.org/)

### Technical Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [Python Requests Library](https://docs.python-requests.org/)

## 🤝 Contributing

Contributions to improve the test suite are welcome:

1. **Report issues** with detailed error information
2. **Suggest improvements** to test coverage
3. **Add new test scenarios** for additional business processes
4. **Improve documentation** and error handling
5. **Add more validation** for edge cases

## 📝 License

This test suite is provided as-is for testing purposes. It may be used, modified, and distributed freely for testing the reload_Matrix application.

## 📞 Support

For issues with the test suite:
1. Check application logs for detailed errors
2. Review API documentation for endpoint specifications
3. Verify database schema matches expected structure
4. Consult Colombian accounting standards for compliance requirements
5. Use debugging tools to trace API calls and responses

---

**Last Updated**: 2025
**Test Suite Version**: 1.0
**Compatible with**: reload_Matrix v1.0+
