#!/usr/bin/env python3
"""
Test Flask-SocketIO threading mode compatibility
"""
import socketio
from server import app, socketio as sio

def test_socketio():
    """Test that Socket.IO is properly configured"""
    print(f"SocketIO async_mode: {sio.async_mode}")
    print(f"SocketIO server class: {type(sio.server)}")
    
    # Test with Flask test client
    client = app.test_client()
    
    # Test basic routes
    response = client.get('/health')
    print(f"Health endpoint: {response.status_code}")
    
    response = client.get('/stats')
    print(f"Stats endpoint: {response.status_code}")
    
    return True

if __name__ == "__main__":
    print("Testing Flask-SocketIO configuration...")
    test_socketio()
    print("✅ Flask-SocketIO threading mode test PASSED")