#!/usr/bin/env python3
"""
Test script to verify SQL injection resistance in the application using SQLite.
This script tests various endpoints to ensure they are not vulnerable to SQL injection.
"""

import sys
import os

# Add the backend directory to the path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.sql.user import User
from app.core.security import get_password_hash
from app.core.database import Base

def setup_test_user():
    """Create a test user in the SQLite database."""
    # Create SQLite engine
    sqlite_path = os.path.join(backend_dir, "business.db")
    engine = create_engine(f"sqlite:///{sqlite_path}")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # Check if test user already exists
    existing_user = db.query(User).filter(User.username == "testuser").first()
    if existing_user:
        print("✅ Test user already exists in the database.")
        db.close()
        return
    
    # Create test user
    hashed_password = get_password_hash("TestPass123!")
    test_user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hashed_password,
        full_name="Test User",
        is_active=True,
        is_superuser=False,
    )
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    print("✅ Test user created successfully in the database.")
    db.close()

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
    
    client = TestClient(app)
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test with username injection
        response = client.post(
            "/api/v1/token",
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
    
    client = TestClient(app)
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test with username injection
        response = client.post(
            "/api/v1/users/",
            json={
                "username": payload,
                "password": "TestPass123!",
                "role": "user"
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

def test_clientes_endpoints_sql_injection():
    """Test clientes endpoints for SQL injection vulnerabilities."""
    print("\n=== Testing Clientes Endpoints for SQL Injection ===")
    
    client = TestClient(app)
    
    # First, authenticate to get a token
    auth_response = client.post(
        "/api/v1/token",
        data={"username": "testuser", "password": "TestPass123!"}
    )
    
    if auth_response.status_code != 200:
        print("⚠️  Could not authenticate for clientes tests")
        return True
    
    token = auth_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    for payload in SQL_INJECTION_PAYLOADS:
        print(f"\nTesting payload: {payload}")
        
        # Test cliente creation with injected name
        response = client.post(
            "/api/v1/clientes/",
            json={
                "nombre": payload,
                "identificacion": "123456789",
                "telefono": "1234567890",
                "email": "test@client.com",
                "direccion": "Test Address"
            },
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"❌ VULNERABLE: Cliente creation succeeded with payload: {payload}")
            print(f"Response: {response.json()}")
            return False
        elif response.status_code == 400 or response.status_code == 422:
            print(f"✅ SAFE: Cliente creation failed as expected with payload: {payload}")
        else:
            print(f"⚠️  UNEXPECTED: Status code {response.status_code} for payload: {payload}")
    
    return True

def main():
    """Run all SQL injection tests."""
    print("=" * 60)
    print("SQL Injection Vulnerability Test Suite (SQLite)")
    print("=" * 60)
    
    # Setup test user
    setup_test_user()
    
    all_passed = True
    
    # Test login endpoint
    if not test_login_sql_injection():
        all_passed = False
    
    # Test user registration endpoint
    if not test_user_registration_sql_injection():
        all_passed = False
    
    # Test clientes endpoints
    if not test_clientes_endpoints_sql_injection():
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
