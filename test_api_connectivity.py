#!/usr/bin/env python3
"""
Simple API Connectivity Test
Tests basic connectivity to the application API
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api/v1"

def log_message(message, type="INFO"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{type}] {message}")

def test_api_connectivity():
    """Test basic API connectivity"""
    
    # Test 1: Check if application is running
    log_message("Testing application connectivity...")
    try:
        response = requests.get(BASE_URL, timeout=10)
        if response.status_code == 200:
            log_message("✓ Application is running")
        else:
            log_message(f"✗ Application returned status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_message(f"✗ Cannot connect to application: {str(e)}", "ERROR")
        return False
    
    # Test 2: Check API base endpoint
    log_message("Testing API base endpoint...")
    try:
        response = requests.get(API_BASE, timeout=10)
        if response.status_code in [200, 404]:  # 404 is acceptable for base API path
            log_message("✓ API base endpoint is accessible")
        else:
            log_message(f"✗ API base endpoint returned status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_message(f"✗ Cannot connect to API: {str(e)}", "ERROR")
        return False
    
    # Test 3: Check authentication endpoint
    log_message("Testing authentication endpoint...")
    try:
        auth_url = f"{API_BASE}/auth/token"
        # Use form data instead of JSON for OAuth2 password flow
        auth_data = {
            "username": "test",
            "password": "test"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        response = requests.post(auth_url, data=auth_data, headers=headers, timeout=10)
        if response.status_code in [200, 401, 400]:  # Acceptable responses
            log_message("✓ Authentication endpoint is accessible")
        else:
            log_message(f"✗ Authentication endpoint returned status {response.status_code}", "ERROR")
            return False
    except Exception as e:
        log_message(f"✗ Cannot connect to authentication endpoint: {str(e)}", "ERROR")
        return False
    
    return True

def main():
    """Main test execution"""
    log_message("Starting API Connectivity Test")
    
    if test_api_connectivity():
        log_message("\n✓ All connectivity tests passed!")
        log_message("You can now run the comprehensive accounting test.")
    else:
        log_message("\n✗ Connectivity tests failed!")
        log_message("Please ensure the application is running at http://localhost:8081")

if __name__ == "__main__":
    main()
