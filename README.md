# Pong Royale

A multiplayer Pong game built with Python, Pygame, and Socket.IO featuring a beautiful pastel aesthetic, glowing effects, and immersive audio.

## ✨ Features

### 🎨 Visual Design
- **Pastel Theme**: Beautiful gradient backgrounds with soft color palette
- **Glowing Effects**: Dynamic glow effects on paddles, ball, and UI elements
- **Retro Aesthetics**: Pixel-perfect fonts and nostalgic visual style
- **Smooth Animations**: 60 FPS rendering with animated UI elements
- **Enhanced UI**: Rounded corners, transparency effects, and visual feedback

### 🔊 Audio Experience
- **Lo-Fi Soundtrack**: Atmospheric background music that loops seamlessly
- **Dynamic Sound Effects**: Soft bounce sounds for paddle and wall collisions
- **Score Celebrations**: Musical chord progressions when players score
- **Procedural Audio**: Auto-generated sound effects if files are missing
- **Volume Control**: Separate controls for music and sound effects

### 🏠 Multiplayer Features
- **Client-Server Architecture**: Real-time multiplayer with room management
- **Room System**: Create and join rooms with shareable room codes
- **Auto-Game Start**: Games begin automatically when both players join
- **Real-time Sync**: Server authoritative state at 60 FPS
- **Smooth Networking**: Local prediction for responsive gameplay

## Architecture

### PongClient Class

The main client class with the following key methods:

- `connect_to_server()`: Establishes connection to the game server
- `send_input()`: Sends player input (keyboard events) to server
- `receive_state()`: Receives and processes game state updates from server
- `render(state)`: Renders the current game state to the screen

### Game Loop

The game loop handles:
- **Input Processing**: Captures keyboard input and sends to server
- **State Updates**: Receives authoritative game state from server
- **Local Prediction**: Smooth interpolation between server updates
- **Rendering**: 60 FPS rendering with Pygame

## Installation

1. Make sure you're in the project directory with the virtual environment activated:
   ```bash
   cd "d:\JEBEZ\07 - FULLSTACK\Pong Royale"
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies (already done if you followed setup):
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Option 1: Using the Launcher
```bash
python launcher.py
```
Then choose to start either the server or client.

### Option 2: Manual Launch

#### Start the Server
```bash
python pong_server.py
```
The server will start on `http://localhost:5000`

#### Start the Client(s)
```bash
python pong_client.py
```
You can run multiple clients to connect different players.

## Controls

- **UP Arrow** or **W**: Move paddle up
- **DOWN Arrow** or **S**: Move paddle down
- **ESC** or **Close Window**: Exit game

## Game Rules

- Classic Pong gameplay
- First player to reach the score limit wins
- Ball bounces off top and bottom walls
- Ball bounces off paddles
- Score increases when ball goes past opponent's paddle

## Network Protocol

The client and server communicate using Socket.IO events:

- `connect`: Client connects to server
- `player_assigned`: Server assigns player ID to client
- `game_state`: Server broadcasts game state to all clients
- `player_input`: Client sends input to server
- `disconnect`: Client disconnects from server

## File Structure

```
Pong Royale/
├── pong_client.py      # Main client with PongClient class
├── pong_server.py      # Game server
├── launcher.py         # Launcher script
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── venv/              # Virtual environment
```

## Development

### Adding Features

The modular design makes it easy to add features:

1. **New Input Types**: Modify `send_input()` method
2. **Enhanced Graphics**: Extend `render()` method
3. **Game Modes**: Add new state handling in `receive_state()`
4. **Sound Effects**: Integrate with pygame.mixer

### Extending the Server

The server can be enhanced with:
- Multiple game rooms
- Spectator mode
- Game replays
- Player statistics
- Tournament brackets

## Troubleshooting

### Connection Issues
- Make sure the server is running before starting clients
- Check that port 5000 is not blocked by firewall
- Verify server URL in client configuration

### Performance Issues
- Adjust frame rate in the game loop if needed
- Check network latency between client and server
- Monitor CPU usage during gameplay

### Input Lag
- The client uses local prediction to minimize perceived lag
- Server authoritative state ensures consistency
- Network latency will affect responsiveness

## Technical Details

### Client-Side Prediction
The client performs local prediction for smooth gameplay:
- Paddle movements are predicted locally
- Ball movement is interpolated between server updates
- Server state overrides local predictions for accuracy

### State Synchronization
- Server runs authoritative game simulation at 60 FPS
- Client receives state updates and renders at 60 FPS
- Input is sent immediately for responsiveness

### Error Handling
- Network disconnection is handled gracefully
- Client can run in offline mode for testing
- Server validates all client input for security