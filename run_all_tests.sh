#!/bin/bash

# Comprehensive Accounting Integration Test Runner
# This script runs all tests in the correct order

echo "=========================================="
echo "Accounting Integration Test Suite"
echo "=========================================="
echo ""

# Step 1: Check if Python is installed
echo "Step 1: Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi
echo "✅ Python 3 is installed"
echo ""

# Step 2: Install required dependencies
echo "Step 2: Installing required dependencies..."
pip3 install requests --quiet
if [ $? -ne 0 ]; then
    echo "❌ Failed to install required dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Step 3: Run connectivity test
echo "Step 3: Running API connectivity test..."
python3 test_api_connectivity.py
if [ $? -ne 0 ]; then
    echo "❌ Connectivity test failed"
    echo "Please ensure the application is running at http://localhost:8081"
    exit 1
fi
echo ""

# Step 4: Run setup script
echo "Step 4: Setting up test user and company..."
python3 setup_test_user.py
if [ $? -ne 0 ]; then
    echo "❌ Setup failed"
    exit 1
fi
echo ""

# Step 5: Run comprehensive accounting test
echo "Step 5: Running comprehensive accounting test..."
echo "This may take a few minutes..."
python3 test_comprehensive_accounting.py
if [ $? -ne 0 ]; then
    echo "❌ Comprehensive test failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "🎉 All tests completed successfully!"
echo "=========================================="
echo ""
echo "Test results have been logged to the console."
echo "You can review the detailed accounting entries, trial balance,"
echo "sales book, and purchases book in the output above."
echo ""
echo "For more information, see:"
echo "- ACCOUNTING_TEST_INSTRUCTIONS.md for test details"
echo "- TEST_FILES_SUMMARY.md for file descriptions"
echo ""
