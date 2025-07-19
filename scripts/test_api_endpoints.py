#!/usr/bin/env python3
"""Test the API endpoints to ensure they work correctly"""

import requests
import json

BASE_URL = "http://localhost:8002"

def test_endpoint(endpoint, description):
    """Test an endpoint and display results"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}")
        print(f"✅ {description}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"   Results: {len(data)} items")
                if data:
                    print(f"   First item: {list(data[0].keys()) if isinstance(data[0], dict) else data[0]}")
            elif isinstance(data, dict):
                print(f"   Results: {len(data)} keys")
                if 'meetings' in data:
                    print(f"   Meetings: {len(data['meetings'])} items")
                    print(f"   Total: {data.get('total', 'N/A')}")
        else:
            print(f"   Error: {response.text}")

        print()

    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {e}")
        print()

def main():
    """Test all API endpoints"""
    print("🚀 Testing API Endpoints...")
    print()

    # Test health endpoint
    test_endpoint("/health", "Health Endpoint")

    # Test categories endpoint
    test_endpoint("/api/v1/meetings/categories/", "Categories Endpoint")

    # Test meetings list endpoint
    test_endpoint("/api/v1/meetings/", "Meetings List Endpoint")

    # Test meetings with filters
    test_endpoint("/api/v1/meetings/?limit=5", "Meetings List with Limit")

    # Test meetings by category
    test_endpoint("/api/v1/meetings/categories/Municipal%20Services", "Meetings by Category")

    # Test meeting statistics
    test_endpoint("/api/v1/meetings/stats/overview", "Meeting Statistics")

    # Test search
    test_endpoint("/api/v1/meetings/search/keywords?q=council", "Search by Keywords")

    # Test specific meeting (if exists)
    test_endpoint("/api/v1/meetings/1", "Specific Meeting Detail")

    print("✅ API endpoint testing complete!")

if __name__ == "__main__":
    main()
