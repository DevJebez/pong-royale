# WSGI entry point for production deployment
import os
from server import app, socketio

# For Railway and other WSGI servers
application = app

if __name__ == "__main__":
    # For local testing
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)