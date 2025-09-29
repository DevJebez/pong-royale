#!/usr/bin/env python3
"""
Room Management Test Script
==========================

This script demonstrates the room management functionality of the Pong Royale server.
It can be used to test room creation, joining, and basic game flow.
"""

import socketio
import time
import threading

class TestClient:
    def __init__(self, client_name, server_url="http://localhost:5000"):
        self.client_name = client_name
        self.server_url = server_url
        self.sio = socketio.Client()
        self.connected = False
        self.room_id = None
        self.paddle_id = None
        
        self.setup_events()
    
    def setup_events(self):
        @self.sio.event
        def connect():
            print(f"[{self.client_name}] Connected to server")
            self.connected = True
            
        @self.sio.event
        def disconnect():
            print(f"[{self.client_name}] Disconnected from server")
            self.connected = False
            
        @self.sio.event
        def connected(data):
            print(f"[{self.client_name}] Received client ID: {data.get('client_id')}")
            
        @self.sio.event
        def room_created(data):
            if data.get('success'):
                self.room_id = data.get('room_id')
                self.paddle_id = data.get('paddle_id')
                print(f"[{self.client_name}] Created room {self.room_id} as player {self.paddle_id}")
            else:
                print(f"[{self.client_name}] Failed to create room: {data.get('error')}")
                
        @self.sio.event
        def room_joined(data):
            if data.get('success'):
                self.room_id = data.get('room_id')
                self.paddle_id = data.get('paddle_id')
                print(f"[{self.client_name}] Joined room {self.room_id} as player {self.paddle_id}")
            else:
                print(f"[{self.client_name}] Failed to join room: {data.get('error')}")
                
        @self.sio.event
        def player_joined(data):
            print(f"[{self.client_name}] Player {data.get('client_id')} joined as player {data.get('paddle_id')}")
            
        @self.sio.event
        def game_state(data):
            # Only print game state occasionally to avoid spam
            if hasattr(self, '_last_state_print'):
                if time.time() - self._last_state_print < 2:  # Print every 2 seconds
                    return
            self._last_state_print = time.time()
            
            ball = data.get('ball', {})
            p1_score = data.get('paddle1', {}).get('score', 0)
            p2_score = data.get('paddle2', {}).get('score', 0)
            print(f"[{self.client_name}] Game state - Ball: ({ball.get('x', 0):.0f}, {ball.get('y', 0):.0f}), Score: {p1_score}-{p2_score}")
    
    def connect_to_server(self):
        try:
            self.sio.connect(self.server_url)
            time.sleep(0.5)  # Wait for connection
            return self.connected
        except Exception as e:
            print(f"[{self.client_name}] Connection error: {e}")
            return False
    
    def create_room(self, room_name=None):
        if self.connected:
            self.sio.emit('create_room', {'room_name': room_name})
    
    def join_room(self, room_id):
        if self.connected:
            self.sio.emit('join_room', {'room_id': room_id})
    
    def send_input(self, up=False, down=False):
        if self.connected and self.room_id:
            self.sio.emit('player_input', {
                'input': {'up': up, 'down': down}
            })
    
    def disconnect(self):
        if self.connected:
            self.sio.disconnect()

def test_room_creation_and_joining():
    """Test creating a room and having another client join."""
    print("=" * 60)
    print("Testing Room Creation and Joining")
    print("=" * 60)
    
    # Create first client (will create room)
    client1 = TestClient("Client1")
    if not client1.connect_to_server():
        print("Failed to connect Client1")
        return
    
    # Create room
    room_name = f"test_room_{int(time.time())}"
    print(f"Client1 creating room: {room_name}")
    client1.create_room(room_name)
    time.sleep(2)  # Wait for room creation
    
    if not client1.room_id:
        print("Room creation failed")
        client1.disconnect()
        return
    
    # Create second client (will join room)
    client2 = TestClient("Client2")
    if not client2.connect_to_server():
        print("Failed to connect Client2")
        client1.disconnect()
        return
    
    # Join room
    print(f"Client2 joining room: {client1.room_id}")
    client2.join_room(client1.room_id)
    time.sleep(2)  # Wait for join
    
    if client2.room_id:
        print(f"✅ Successfully created and joined room {client1.room_id}")
        
        # Simulate some game input
        print("Simulating game input for 10 seconds...")
        for i in range(100):  # 10 seconds at 10 FPS
            # Client1 moves up and down alternately
            client1.send_input(up=(i % 20 < 10))
            # Client2 moves opposite
            client2.send_input(down=(i % 20 < 10))
            time.sleep(0.1)
            
    else:
        print("❌ Failed to join room")
    
    # Cleanup
    print("Disconnecting clients...")
    client1.disconnect()
    client2.disconnect()
    time.sleep(1)

def test_multiple_rooms():
    """Test creating multiple rooms simultaneously."""
    print("=" * 60)
    print("Testing Multiple Rooms")
    print("=" * 60)
    
    clients = []
    
    # Create 3 pairs of clients (3 rooms)
    for i in range(3):
        room_name = f"room_{i+1}_{int(time.time())}"
        
        # Creator client
        creator = TestClient(f"Creator{i+1}")
        if creator.connect_to_server():
            creator.create_room(room_name)
            clients.append(creator)
            time.sleep(1)
            
            # Joiner client
            joiner = TestClient(f"Joiner{i+1}")
            if joiner.connect_to_server():
                time.sleep(1)  # Wait for room creation
                if creator.room_id:
                    joiner.join_room(creator.room_id)
                    clients.append(joiner)
                    time.sleep(1)
    
    print(f"Created {len(clients)//2} rooms with {len(clients)} total clients")
    
    # Let them run for a bit
    print("Running multiple rooms for 5 seconds...")
    time.sleep(5)
    
    # Cleanup
    print("Disconnecting all clients...")
    for client in clients:
        client.disconnect()
    time.sleep(1)

def main():
    print("🏓 Pong Royale Server Test Suite 🏓")
    print("Make sure the server is running on localhost:5000")
    
    while True:
        print("\nSelect a test:")
        print("1. Test room creation and joining")
        print("2. Test multiple rooms")
        print("3. Exit")
        
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            test_room_creation_and_joining()
        elif choice == "2":
            test_multiple_rooms()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()