#!/usr/bin/env python3
"""
Quick test of the health endpoint
"""
from server import app

def test_health():
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Health endpoint status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        return response.status_code == 200

if __name__ == "__main__":
    print("Testing health endpoint...")
    success = test_health()
    print(f"Health check {'PASSED' if success else 'FAILED'}")