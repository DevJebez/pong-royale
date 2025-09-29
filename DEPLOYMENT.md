# 🏓 Pong Royale - Production Deployment Guide

## 📋 Production-Ready Files

✅ **Server configured for deployment:**
- `server.py` - Production Flask-SocketIO server with CORS
- `wsgi.py` - WSGI entry point for gunicorn
- `requirements.txt` - Platform-specific dependencies
- `start_production.py` - Cross-platform production starter
- `test_server.py` - Server endpoint testing utility
- `config.py` - Client server configuration

✅ **Deployment configurations:**
- `Procfile` - Railway/Heroku process file
- `railway.toml` - Railway-specific configuration
- `render.yaml` - Render deployment notes
- `.gitignore` - Production-ready git ignore

## 🚀 Quick Deployment Steps

### 1. Deploy on Railway (Recommended)

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Deploy Pong Royale server"
git remote add origin https://github.com/yourusername/pong-royale.git
git push -u origin main

# 2. Deploy on Railway
# Visit railway.app → Connect GitHub repo → Auto-deploy starts
# Your server: https://your-app-name.railway.app
```

### 2. Deploy on Render

```bash
# 1. Push to GitHub (same as above)

# 2. Create Web Service on render.com
# Build Command: pip install -r requirements.txt
# Start Command: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:app
# Environment: FLASK_ENV=production, SECRET_KEY=your-secret
```

### 3. Update Client Configuration

```python
# Edit config.py after deployment
RAILWAY_SERVER = "https://your-actual-app-name.railway.app"
RENDER_SERVER = "https://your-actual-app-name.onrender.com"
CURRENT_SERVER = RAILWAY_SERVER  # or RENDER_SERVER
```

## 🧪 Testing Your Deployment

```bash
# Test locally first
python start_production.py  # Starts production server locally
python test_server.py       # Tests all endpoints

# Test deployed server
python test_server.py https://your-app-name.railway.app
```

## 🎮 Running the Game

### Server (Production)
```bash
# Platform-agnostic production start
python start_production.py

# Or manual start
python server.py              # Development
gunicorn -w 1 wsgi:app        # Linux production
```

### Client (Local)
```bash
# Make sure config.py points to your deployed server
python pong_client.py
```

## 📊 Production Features

✅ **CORS enabled** for all origins  
✅ **Environment variables** for configuration  
✅ **Health check** endpoint at `/health`  
✅ **Cross-platform** WSGI server selection  
✅ **Thread-safe** room management  
✅ **Auto-scaling** rooms (create/delete)  
✅ **Real-time monitoring** at `/stats`  

## � Server Endpoints

- `/` - Server dashboard with live statistics
- `/health` - Health check (for monitoring)
- `/stats` - Server statistics (JSON)
- `/rooms` - Active rooms list (JSON)

## 🛠️ Architecture

- **Per-room game loops** at 60 FPS
- **Thread-safe** operations with locks
- **Real-time multiplayer** via Socket.IO
- **Auto room cleanup** when empty
- **Eventlet WSGI** for async performance

## 🚨 Production Checklist

- ✅ Flask-CORS installed and configured
- ✅ Gunicorn/Waitress for production serving
- ✅ Environment variables configured
- ✅ Health monitoring endpoint
- ✅ Debug logging disabled in production
- ✅ Secret key from environment
- ✅ Cross-platform compatibility
- ✅ Client configuration updated

## 🌐 Post-Deployment

1. **Test your server:** `python test_server.py https://your-app-url.com`
2. **Update client:** Edit `config.py` with your server URL
3. **Monitor:** Check `/stats` for real-time server information
4. **Scale:** Both Railway and Render auto-scale based on usage

Your multiplayer Pong server is now production-ready! 🎉

## � Pro Tips

- **Railway**: Automatic deploys from GitHub, great for MVP
- **Render**: More configuration options, excellent for scaling
- **Health checks**: Use `/health` endpoint for uptime monitoring
- **Statistics**: Monitor `/stats` for player count and room usage
- **Client**: Update `CURRENT_SERVER` in `config.py` to switch environments