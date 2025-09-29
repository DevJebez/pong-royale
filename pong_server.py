from flask import Flask
from flask_socketio import SocketIO, emit
import time
import threading
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pong_royale_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class PongServer:
    def __init__(self):
        self.game_state = {
            'ball': {'x': 400, 'y': 300, 'dx': 200, 'dy': 150, 'radius': 10},
            'paddle1': {'x': 50, 'y': 250, 'width': 20, 'height': 100, 'score': 0},
            'paddle2': {'x': 730, 'y': 250, 'width': 20, 'height': 100, 'score': 0},
            'players': {},
            'game_width': 800,
            'game_height': 600
        }
        self.players = {}
        self.game_running = True
        self.lock = threading.Lock()
        
        # Start game loop in a separate thread
        self.game_thread = threading.Thread(target=self.game_loop)
        self.game_thread.daemon = True
        self.game_thread.start()
    
    def add_player(self, sid):
        """Add a new player to the game."""
        with self.lock:
            if len(self.players) < 2:
                player_id = len(self.players) + 1
                self.players[sid] = {
                    'id': player_id,
                    'input': {'up': False, 'down': False}
                }
                return player_id
            return None
    
    def remove_player(self, sid):
        """Remove a player from the game."""
        with self.lock:
            if sid in self.players:
                del self.players[sid]
    
    def update_player_input(self, sid, input_data):
        """Update player input."""
        with self.lock:
            if sid in self.players:
                self.players[sid]['input'] = input_data
    
    def game_loop(self):
        """Main game loop running on the server."""
        last_time = time.time()
        
        while self.game_running:
            current_time = time.time()
            dt = current_time - last_time
            last_time = current_time
            
            with self.lock:
                self.update_game_state(dt)
            
            # Broadcast game state to all clients
            socketio.emit('game_state', self.game_state)
            
            # Run at 60 FPS
            time.sleep(1/60)
    
    def update_game_state(self, dt):
        """Update the game state."""
        # Update paddles based on player input
        paddle_speed = 300  # pixels per second
        
        for sid, player in self.players.items():
            player_id = player['id']
            input_data = player['input']
            
            if player_id == 1:
                paddle = self.game_state['paddle1']
            elif player_id == 2:
                paddle = self.game_state['paddle2']
            else:
                continue
            
            # Update paddle position
            if input_data.get('up'):
                paddle['y'] = max(0, paddle['y'] - paddle_speed * dt)
            elif input_data.get('down'):
                paddle['y'] = min(self.game_state['game_height'] - paddle['height'], 
                                paddle['y'] + paddle_speed * dt)
        
        # Update ball
        ball = self.game_state['ball']
        ball['x'] += ball['dx'] * dt
        ball['y'] += ball['dy'] * dt
        
        # Ball collision with top/bottom walls
        if ball['y'] <= ball['radius'] or ball['y'] >= self.game_state['game_height'] - ball['radius']:
            ball['dy'] = -ball['dy']
        
        # Ball collision with paddles
        paddle1 = self.game_state['paddle1']
        paddle2 = self.game_state['paddle2']
        
        # Left paddle collision
        if (ball['x'] - ball['radius'] <= paddle1['x'] + paddle1['width'] and
            ball['y'] >= paddle1['y'] and ball['y'] <= paddle1['y'] + paddle1['height'] and
            ball['dx'] < 0):
            ball['dx'] = -ball['dx']
        
        # Right paddle collision
        if (ball['x'] + ball['radius'] >= paddle2['x'] and
            ball['y'] >= paddle2['y'] and ball['y'] <= paddle2['y'] + paddle2['height'] and
            ball['dx'] > 0):
            ball['dx'] = -ball['dx']
        
        # Ball out of bounds (scoring)
        if ball['x'] < 0:
            # Player 2 scores
            paddle2['score'] += 1
            self.reset_ball()
        elif ball['x'] > self.game_state['game_width']:
            # Player 1 scores
            paddle1['score'] += 1
            self.reset_ball()
    
    def reset_ball(self):
        """Reset ball to center."""
        self.game_state['ball']['x'] = self.game_state['game_width'] // 2
        self.game_state['ball']['y'] = self.game_state['game_height'] // 2
        self.game_state['ball']['dx'] = 200 if self.game_state['ball']['dx'] > 0 else -200
        self.game_state['ball']['dy'] = 150

# Create server instance
pong_server = PongServer()

@socketio.on('connect')
def handle_connect():
    print(f"Client {request.sid} connected")
    player_id = pong_server.add_player(request.sid)
    
    if player_id:
        emit('player_assigned', {'player_id': player_id})
        emit('game_state', pong_server.game_state)
        print(f"Assigned player {player_id} to client {request.sid}")
    else:
        emit('error', {'message': 'Game is full'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client {request.sid} disconnected")
    pong_server.remove_player(request.sid)

@socketio.on('player_input')
def handle_player_input(data):
    player_id = data.get('player_id')
    input_data = data.get('input', {})
    pong_server.update_player_input(request.sid, input_data)

@app.route('/')
def index():
    return '''
    <h1>Pong Royale Server</h1>
    <p>Server is running. Connect with the Pong client to play!</p>
    <p>Players connected: ''' + str(len(pong_server.players)) + '''</p>
    '''

if __name__ == '__main__':
    print("Starting Pong Royale server...")
    print("Server will be available at http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)