#!/usr/bin/env python3
"""
Pong Royale - Main entry point for Railway deployment
This file ensures Railway detects this as a Python project
"""

if __name__ == "__main__":
    # Import and run the Flask app
    from wsgi import application
    import os
    
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Pong Royale server on port {port}")
    
    # For Railway, we should use the WSGI application directly
    # This file is just for detection - actual serving is done by gunicorn
    print("This is a Python Flask-SocketIO application")
    print("Server will be started by gunicorn as configured in Procfile")