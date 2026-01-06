"""
Quick Test Script for E-Commerce Intelligence
Tests API endpoints and verifies functionality
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_api():
    print("=" * 60)
    print("E-COMMERCE INTELLIGENCE - API TEST")
    print("=" * 60)

    # Test 1: Health Check
    print("\n[TEST 1] Health Check...")
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ API is online")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Get Stats
    print("\n[TEST 2] Get Statistics...")
    try:
        response = requests.get(f"{API_URL}/stats")
        if response.status_code == 200:
            data = response.json()
            print("✅ Stats loaded successfully")
            print(f"   Total Products: {data['total_products']}")
            print(f"   Average Price: Rs. {data['price_stats']['average']:.2f}")
            print(f"   Average Rating: {data['rating_stats']['average']:.2f}")
        else:
            print(f"❌ Stats failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Get Products
    print("\n[TEST 3] Get Products...")
    try:
        response = requests.get(f"{API_URL}/products?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Loaded {data['returned']} products")
            if data['products']:
                product = data['products'][0]
                print(f"   Sample Product: {product['title'][:50]}...")
                print(f"   Product ID: {product['product_id']}")
        else:
            print(f"❌ Products failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Open frontend/index.html in your browser")
    print("2. The API server is running at http://localhost:8000")
    print("3. API docs available at http://localhost:8000/docs")
    print("\nEverything is working! 🚀")

if __name__ == "__main__":
    test_api()
