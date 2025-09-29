#!/usr/bin/env python3
"""
Production server starter for Pong Royale
Automatically chooses the appropriate WSGI server based on platform
"""

import os
import sys
import subprocess
import platform

def start_production_server():
    """Start the production server with the appropriate WSGI server"""
    port = os.environ.get('PORT', '5000')
    host = os.environ.get('HOST', '0.0.0.0')
    
    # Check if we're on Windows
    is_windows = platform.system() == 'Windows'
    
    print("🏓 Starting Pong Royale Production Server")
    print(f"Platform: {platform.system()}")
    print(f"Host: {host}:{port}")
    
    if is_windows:
        # Use waitress on Windows
        print("Using Waitress WSGI server (Windows)")
        try:
            from waitress import serve
            from wsgi import app
            serve(app, host=host, port=int(port), threads=4)
        except ImportError:
            print("ERROR: waitress not installed. Install with: pip install waitress")
            sys.exit(1)
    else:
        # Use gunicorn on Unix/Linux (production deployment)
        print("Using Gunicorn WSGI server (Unix/Linux)")
        cmd = [
            'gunicorn',
            '--worker-class', 'eventlet',
            '-w', '1',
            '--bind', f'{host}:{port}',
            'wsgi:app'
        ]
        
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to start gunicorn: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("ERROR: gunicorn not found. Install with: pip install gunicorn")
            sys.exit(1)

if __name__ == '__main__':
    start_production_server()