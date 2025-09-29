from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms
from flask_cors import CORS
import time
import threading
import uuid
import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import math

app = Flask(__name__)

# Production-ready configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pong_royale_secret_key_2025_production')
app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

# Enable CORS for all domains
CORS(app, origins="*")

# Configure SocketIO for production
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    logger=False,  # Disable debug logging in production
    engineio_logger=False,
    async_mode='threading',  # Use threading for better compatibility
    ping_timeout=60,
    ping_interval=25
)

@dataclass
class Ball:
    x: float
    y: float
    dx: float
    dy: float
    radius: float = 10
    speed: float = 300

@dataclass
class Paddle:
    x: float
    y: float
    width: float = 20
    height: float = 100
    speed: float = 400
    score: int = 0

@dataclass
class Player:
    id: str
    paddle_id: int  # 1 or 2
    input_state: Dict[str, bool] = None
    connected: bool = True
    
    def __post_init__(self):
        if self.input_state is None:
            self.input_state = {'up': False, 'down': False}

class GameRoom:
    def __init__(self, room_id: str, width: int = 800, height: int = 600):
        self.room_id = room_id
        self.width = width
        self.height = height
        self.max_players = 2
        self.created_at = time.time()
        
        # Game objects
        self.ball = Ball(
            x=width / 2,
            y=height / 2,
            dx=300,
            dy=200
        )
        
        self.paddle1 = Paddle(
            x=30,
            y=height / 2 - 50
        )
        
        self.paddle2 = Paddle(
            x=width - 50,
            y=height / 2 - 50
        )
        
        # Players
        self.players: Dict[str, Player] = {}
        self.game_active = False
        self.game_paused = False
        self.last_update = time.time()
        
        # Game loop management
        self.game_thread = None
        self.game_running = False
        self.lock = threading.Lock()
        
        # Game settings
        self.max_score = 10
        self.ball_speed_increase = 1.05  # Speed multiplier after each hit
        
    def add_player(self, client_id: str) -> Optional[int]:
        """Add a player to the room. Returns paddle number (1 or 2) or None if room is full."""
        if len(self.players) >= self.max_players:
            return None
            
        # Assign paddle based on current players
        paddle_id = 1 if len(self.players) == 0 else 2
        
        self.players[client_id] = Player(
            id=client_id,
            paddle_id=paddle_id
        )
        
        print(f"Player {client_id} added to room {self.room_id} as paddle {paddle_id}")
        
        # Start game when we have 2 players
        if len(self.players) == 2:
            self.start_game_loop()
            
        return paddle_id
    
    def remove_player(self, client_id: str):
        """Remove a player from the room."""
        if client_id in self.players:
            del self.players[client_id]
            print(f"Player {client_id} removed from room {self.room_id}")
            
        # Stop game if we don't have enough players
        if len(self.players) < 2:
            self.stop_game_loop()
    
    def start_game_loop(self):
        """Start the game loop for this room in a background thread."""
        if not self.game_running and len(self.players) == 2:
            self.game_running = True
            self.game_active = True
            self.game_paused = False
            self.reset_ball()
            
            # Start the game thread
            self.game_thread = threading.Thread(
                target=self._room_game_loop, 
                name=f"GameLoop-{self.room_id}",
                daemon=True
            )
            self.game_thread.start()
            print(f"Game loop started for room {self.room_id}")
    
    def stop_game_loop(self):
        """Stop the game loop for this room."""
        if self.game_running:
            self.game_running = False
            self.game_active = False
            self.game_paused = True
            print(f"Game loop stopped for room {self.room_id}")
    
    def _room_game_loop(self):
        """Main game loop for this specific room running at 60 FPS."""
        target_fps = 60
        frame_time = 1.0 / target_fps
        last_time = time.time()
        
        print(f"Room {self.room_id} game loop thread started")
        
        while self.game_running and len(self.players) == 2:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            # Update game state with thread safety
            with self.lock:
                self.update_game_state(dt)
                game_state = self.get_state()
            
            # Emit game state to all clients in this room
            socketio.emit('game_state', game_state, room=self.room_id)
            
            # Sleep to maintain 60 FPS
            elapsed = time.time() - current_time
            sleep_time = max(0, frame_time - elapsed)
            time.sleep(sleep_time)
        
        print(f"Room {self.room_id} game loop thread ended")
    
    def update_player_input(self, client_id: str, input_data: Dict[str, bool]):
        """Update player input state with thread safety."""
        with self.lock:
            if client_id in self.players:
                self.players[client_id].input_state.update(input_data)
    
    def reset_ball(self):
        """Reset ball to center with random direction."""
        self.ball.x = self.width / 2
        self.ball.y = self.height / 2
        
        # Random direction
        direction = 1 if time.time() % 2 < 1 else -1
        angle = (time.time() % 0.5) - 0.25  # -0.25 to 0.25
        
        self.ball.dx = direction * self.ball.speed
        self.ball.dy = angle * self.ball.speed
    
    def update_game_state(self, dt: float):
        """Update the game state for one frame."""
        if not self.game_active or self.game_paused:
            return
            
        # Update paddles based on player input
        for player in self.players.values():
            paddle = self.paddle1 if player.paddle_id == 1 else self.paddle2
            input_state = player.input_state
            
            if input_state.get('up', False):
                paddle.y = max(0, paddle.y - paddle.speed * dt)
            elif input_state.get('down', False):
                paddle.y = min(self.height - paddle.height, paddle.y + paddle.speed * dt)
        
        # Update ball position
        self.ball.x += self.ball.dx * dt
        self.ball.y += self.ball.dy * dt
        
        # Ball collision with top/bottom walls
        if self.ball.y <= self.ball.radius:
            self.ball.y = self.ball.radius
            self.ball.dy = abs(self.ball.dy)
        elif self.ball.y >= self.height - self.ball.radius:
            self.ball.y = self.height - self.ball.radius
            self.ball.dy = -abs(self.ball.dy)
        
        # Ball collision with paddles
        self._check_paddle_collision(self.paddle1)
        self._check_paddle_collision(self.paddle2)
        
        # Ball out of bounds (scoring)
        if self.ball.x < -self.ball.radius:
            # Player 2 scores
            self.paddle2.score += 1
            self._handle_score()
        elif self.ball.x > self.width + self.ball.radius:
            # Player 1 scores
            self.paddle1.score += 1
            self._handle_score()
    
    def _check_paddle_collision(self, paddle: Paddle):
        """Check and handle ball collision with a paddle."""
        # Check if ball is within paddle bounds
        if (self.ball.y + self.ball.radius >= paddle.y and 
            self.ball.y - self.ball.radius <= paddle.y + paddle.height):
            
            # Left paddle (paddle1)
            if (paddle.x < self.width / 2 and 
                self.ball.x - self.ball.radius <= paddle.x + paddle.width and
                self.ball.x > paddle.x and
                self.ball.dx < 0):
                
                self.ball.x = paddle.x + paddle.width + self.ball.radius
                self.ball.dx = abs(self.ball.dx) * self.ball_speed_increase
                
                # Add spin based on where ball hits paddle
                hit_pos = (self.ball.y - paddle.y) / paddle.height  # 0 to 1
                spin_factor = (hit_pos - 0.5) * 2  # -1 to 1
                self.ball.dy += spin_factor * 100
                
            # Right paddle (paddle2)
            elif (paddle.x > self.width / 2 and 
                  self.ball.x + self.ball.radius >= paddle.x and
                  self.ball.x < paddle.x + paddle.width and
                  self.ball.dx > 0):
                
                self.ball.x = paddle.x - self.ball.radius
                self.ball.dx = -abs(self.ball.dx) * self.ball_speed_increase
                
                # Add spin based on where ball hits paddle
                hit_pos = (self.ball.y - paddle.y) / paddle.height  # 0 to 1
                spin_factor = (hit_pos - 0.5) * 2  # -1 to 1
                self.ball.dy += spin_factor * 100
    
    def _handle_score(self):
        """Handle scoring and check for game end."""
        # Check for game end
        if self.paddle1.score >= self.max_score or self.paddle2.score >= self.max_score:
            self.game_active = False
            # Could emit game_end event here
        else:
            # Reset ball for next round
            self.reset_ball()
            time.sleep(0.5)  # Brief pause
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current game state as a dictionary with thread safety."""
        return {
            'room_id': self.room_id,
            'ball': {
                'x': self.ball.x,
                'y': self.ball.y,
                'dx': self.ball.dx,
                'dy': self.ball.dy,
                'radius': self.ball.radius
            },
            'paddle1': {
                'x': self.paddle1.x,
                'y': self.paddle1.y,
                'width': self.paddle1.width,
                'height': self.paddle1.height,
                'score': self.paddle1.score
            },
            'paddle2': {
                'x': self.paddle2.x,
                'y': self.paddle2.y,
                'width': self.paddle2.width,
                'height': self.paddle2.height,
                'score': self.paddle2.score
            },
            'players': {pid: {
                'id': p.id,
                'paddle_id': p.paddle_id,
                'connected': p.connected
            } for pid, p in self.players.items()},
            'game_active': self.game_active,
            'game_paused': self.game_paused,
            'game_running': self.game_running,
            'player_count': len(self.players),
            'max_score': self.max_score,
            'timestamp': time.time()
        }

class GameServer:
    def __init__(self):
        self.rooms: Dict[str, GameRoom] = {}
        self.client_rooms: Dict[str, str] = {}  # client_id -> room_id
        self.lock = threading.Lock()  # For thread-safe room operations
        
        print("Game server initialized with per-room game loops")
    
    def create_room(self, room_name: str = None) -> str:
        """Create a new game room with thread safety."""
        with self.lock:
            room_id = room_name or str(uuid.uuid4())[:8]
            
            # Ensure unique room ID
            while room_id in self.rooms:
                room_id = str(uuid.uuid4())[:8]
                
            self.rooms[room_id] = GameRoom(room_id)
            print(f"Created room: {room_id}")
            return room_id
    
    def join_room(self, client_id: str, room_id: str) -> Optional[int]:
        """Join a client to a room. Returns paddle number or None if failed."""
        with self.lock:
            if room_id not in self.rooms:
                return None
                
            room = self.rooms[room_id]
            paddle_id = room.add_player(client_id)
            
            if paddle_id is not None:
                # Remove client from previous room if any
                if client_id in self.client_rooms:
                    old_room_id = self.client_rooms[client_id]
                    if old_room_id in self.rooms and old_room_id != room_id:
                        self.rooms[old_room_id].remove_player(client_id)
                        
                self.client_rooms[client_id] = room_id
                print(f"Client {client_id} joined room {room_id} as player {paddle_id}")
                
            return paddle_id
    
    def leave_room(self, client_id: str):
        """Remove a client from their current room with thread safety."""
        with self.lock:
            if client_id in self.client_rooms:
                room_id = self.client_rooms[client_id]
                if room_id in self.rooms:
                    room = self.rooms[room_id]
                    room.remove_player(client_id)
                    
                    # Clean up empty rooms
                    if len(room.players) == 0:
                        # Stop the game loop before deleting
                        room.stop_game_loop()
                        del self.rooms[room_id]
                        print(f"Deleted empty room: {room_id}")
                        
                del self.client_rooms[client_id]
                print(f"Client {client_id} left room {room_id}")
    
    def update_player_input(self, client_id: str, input_data: Dict[str, bool]):
        """Update player input for their current room."""
        if client_id in self.client_rooms:
            room_id = self.client_rooms[client_id]
            if room_id in self.rooms:
                self.rooms[room_id].update_player_input(client_id, input_data)
    
    def get_room_list(self) -> Dict[str, Dict[str, Any]]:
        """Get list of all rooms with basic info."""
        with self.lock:
            return {
                room_id: {
                    'room_id': room_id,
                    'player_count': len(room.players),
                    'max_players': room.max_players,
                    'game_active': room.game_active,
                    'game_running': room.game_running,
                    'created_at': room.created_at,
                    'paddle1_score': room.paddle1.score,
                    'paddle2_score': room.paddle2.score
                }
                for room_id, room in self.rooms.items()
            }
    
    def get_room_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        with self.lock:
            total_players = sum(len(room.players) for room in self.rooms.values())
            active_games = sum(1 for room in self.rooms.values() if room.game_running)
            
            return {
                'total_rooms': len(self.rooms),
                'total_players': total_players,
                'active_games': active_games,
                'rooms_with_players': len([r for r in self.rooms.values() if len(r.players) > 0]),
                'server_uptime': time.time() - (min(room.created_at for room in self.rooms.values()) if self.rooms else time.time())
            }

# Create global game server instance
game_server = GameServer()

# Socket.IO Event Handlers
@socketio.on('connect')
def handle_connect():
    client_id = request.sid
    print(f"Client connected: {client_id}")
    emit('connected', {'client_id': client_id})
    emit('room_list', game_server.get_room_list())

@socketio.on('disconnect')
def handle_disconnect():
    client_id = request.sid
    print(f"Client disconnected: {client_id}")
    game_server.leave_room(client_id)

@socketio.on('create_room')
def handle_create_room(data):
    client_id = request.sid
    room_name = data.get('room_name', None)
    
    # Create new room
    room_id = game_server.create_room(room_name)
    
    # Join the creator to the room
    join_room(room_id)
    paddle_id = game_server.join_room(client_id, room_id)
    
    if paddle_id:
        emit('room_created', {
            'room_id': room_id,
            'paddle_id': paddle_id,
            'success': True
        })
        emit('room_list', game_server.get_room_list(), broadcast=True)
        print(f"Client {client_id} created and joined room {room_id}")
    else:
        emit('room_created', {'success': False, 'error': 'Failed to join created room'})

@socketio.on('join_room')
def handle_join_room(data):
    client_id = request.sid
    room_id = data.get('room_id')
    
    if not room_id:
        emit('room_joined', {'success': False, 'error': 'Room ID required'})
        return
    
    # Check if room exists
    if room_id not in game_server.rooms:
        emit('room_joined', {'success': False, 'error': 'Room not found'})
        return
    
    # Join the room
    join_room(room_id)
    paddle_id = game_server.join_room(client_id, room_id)
    
    if paddle_id:
        emit('room_joined', {
            'room_id': room_id,
            'paddle_id': paddle_id,
            'success': True
        })
        
        # Notify other players in the room
        emit('player_joined', {
            'client_id': client_id,
            'paddle_id': paddle_id
        }, room=room_id, include_self=False)
        
        emit('room_list', game_server.get_room_list(), broadcast=True)
        print(f"Client {client_id} joined room {room_id} as player {paddle_id}")
    else:
        emit('room_joined', {'success': False, 'error': 'Room is full'})

@socketio.on('leave_room')
def handle_leave_room():
    client_id = request.sid
    
    if client_id in game_server.client_rooms:
        room_id = game_server.client_rooms[client_id]
        leave_room(room_id)
        game_server.leave_room(client_id)
        
        emit('room_left', {'success': True})
        emit('player_left', {'client_id': client_id}, room=room_id)
        emit('room_list', game_server.get_room_list(), broadcast=True)
    else:
        emit('room_left', {'success': False, 'error': 'Not in a room'})

@socketio.on('player_input')
def handle_player_input(data):
    client_id = request.sid
    input_data = data.get('input', {})
    
    game_server.update_player_input(client_id, input_data)

@socketio.on('get_room_list')
def handle_get_room_list():
    emit('room_list', game_server.get_room_list())

@socketio.on('get_room_state')
def handle_get_room_state():
    client_id = request.sid
    
    if client_id in game_server.client_rooms:
        room_id = game_server.client_rooms[client_id]
        if room_id in game_server.rooms:
            emit('room_state', game_server.rooms[room_id].get_state())
    else:
        emit('room_state', {'error': 'Not in a room'})

# Flask Routes
@app.route('/')
def index():
    stats = game_server.get_room_stats()
    rooms_info = game_server.get_room_list()
    
    return f'''
    <h1>🏓 Pong Royale Server</h1>
    <p>Server Status: <strong style="color: green;">Running</strong></p>
    <p>Active Rooms: <strong>{stats['total_rooms']}</strong></p>
    <p>Active Games: <strong>{stats['active_games']}</strong></p>
    <p>Total Players: <strong>{stats['total_players']}</strong></p>
    
    <h2>Room Details:</h2>
    <table border="1" style="border-collapse: collapse; margin: 10px 0;">
        <tr style="background-color: #f0f0f0;">
            <th style="padding: 8px;">Room ID</th>
            <th style="padding: 8px;">Players</th>
            <th style="padding: 8px;">Status</th>
            <th style="padding: 8px;">Score</th>
        </tr>
        {''.join(f"""
        <tr>
            <td style="padding: 8px;">{room_id}</td>
            <td style="padding: 8px;">{room_info['player_count']}/{room_info['max_players']}</td>
            <td style="padding: 8px;">{'🟢 Playing' if room_info['game_running'] else '🟡 Waiting'}</td>
            <td style="padding: 8px;">{room_info['paddle1_score']} - {room_info['paddle2_score']}</td>
        </tr>
        """ for room_id, room_info in rooms_info.items())}
    </table>
    
    <h2>API Endpoints:</h2>
    <ul>
        <li><a href="/rooms">/rooms</a> - Get room list (JSON)</li>
        <li><a href="/stats">/stats</a> - Get server statistics (JSON)</li>
    </ul>
    
    <p><em>Each room runs its own 60 FPS game loop when both players are connected.</em></p>
    '''

@app.route('/rooms')
def get_rooms():
    return game_server.get_room_list()

@app.route('/stats')
def get_stats():
    return game_server.get_room_stats()

# Production server info endpoint
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'pong-royale-server', 'version': '1.0.0'}

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    print("=" * 50)
    print("🏓 PONG ROYALE SERVER STARTING 🏓")
    print("=" * 50)
    print(f"Server URL: http://{host}:{port}")
    print(f"Architecture: Per-room game loops at 60 FPS")
    print(f"Max Players per Room: 2")
    print(f"Game starts automatically when both players join")
    print(f"Environment: {'Production' if not app.config['DEBUG'] else 'Development'}")
    print("=" * 50)
    
    try:
        socketio.run(app, host=host, port=port, debug=app.config['DEBUG'])
    except KeyboardInterrupt:
        print("\nShutting down server...")
        # Stop all room game loops
        for room in game_server.rooms.values():
            room.stop_game_loop()
else:
    # Production WSGI server (gunicorn)
    print("🏓 Pong Royale Server running in production mode")