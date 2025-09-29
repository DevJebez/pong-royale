# Server configuration for Pong Royale client
# Update these URLs after deploying your server

# Local development server
LOCAL_SERVER = "http://localhost:5000"

# Production server URLs (update after deployment)
RAILWAY_SERVER = "https://your-app-name.up.railway.app"  # Update this after Railway deployment
RENDER_SERVER = "https://your-app-name.onrender.com"     # Update this after Render deployment

# Current server to use (change this to switch servers)
CURRENT_SERVER = LOCAL_SERVER  # Change to RAILWAY_SERVER or RENDER_SERVER after deployment

# Or use environment variable for dynamic switching
import os
SERVER_URL = os.environ.get('PONG_SERVER_URL', CURRENT_SERVER)