#!/usr/bin/env python3
"""
Test the deployed Pong Royale server endpoints
Usage: python test_server.py [server_url]
"""

import requests
import sys
import json
import time

def test_server(base_url):
    """Test all server endpoints"""
    print(f"🏓 Testing Pong Royale Server: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    try:
        print("1. Testing /health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print(f"   ✅ Health check passed: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test stats endpoint
    try:
        print("2. Testing /stats endpoint...")
        response = requests.get(f"{base_url}/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Stats retrieved:")
            print(f"      - Total rooms: {stats.get('total_rooms', 0)}")
            print(f"      - Total players: {stats.get('total_players', 0)}")
            print(f"      - Active games: {stats.get('active_games', 0)}")
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # Test rooms endpoint
    try:
        print("3. Testing /rooms endpoint...")
        response = requests.get(f"{base_url}/rooms", timeout=10)
        if response.status_code == 200:
            rooms = response.json()
            print(f"   ✅ Rooms retrieved: {len(rooms)} rooms found")
        else:
            print(f"   ❌ Rooms failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Rooms error: {e}")
    
    # Test main page
    try:
        print("4. Testing main page (/)...")
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("   ✅ Main page accessible")
        else:
            print(f"   ❌ Main page failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Main page error: {e}")
    
    print("=" * 50)
    print("✅ Server testing complete!")
    print(f"🌐 Visit {base_url} in your browser to see the dashboard")

if __name__ == '__main__':
    # Get server URL from command line or use default
    if len(sys.argv) > 1:
        server_url = sys.argv[1].rstrip('/')
    else:
        server_url = "http://localhost:5000"
    
    test_server(server_url)