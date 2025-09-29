# WSGI entry point for production deployment
from server import app, socketio

if __name__ == "__main__":
    socketio.run(app)
else:
    # For gunicorn
    application = app