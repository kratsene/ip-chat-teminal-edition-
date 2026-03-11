#!/usr/bin/env python3
"""
Terminal Chat System - Server
Auto IP detection + Optional Tor privacy
"""

import socket
import threading
import string
import random
from datetime import datetime
from typing import Dict
import sys

# Optional Tor import
try:
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False


class ChatServer:
    """Chat server with auto IP detection"""
    
    def __init__(self, use_tor=False):
        # Auto-detect device IP
        self.host = self._detect_ip()
        self.port = 5000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()
        self.running = False
        
        # Generate room code
        self.room_code = self._generate_code()
        
        # Optional Tor
        self.use_tor = use_tor and TOR_AVAILABLE
        self.onion_address = None
        if self.use_tor:
            self._setup_tor()
    
    def _detect_ip(self):
        """Auto-detect device IP from network"""
        try:
            # Connect to external service to get real IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                # Fallback: get hostname IP
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"
    
    def _generate_code(self):
        """Generate 10-digit room code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(10))
    
    def _setup_tor(self):
        """Optional: Setup Tor hidden service"""
        try:
            print("[TOR] Setting up hidden service...")
            controller = Controller.from_port(port=9051)
            controller.authenticate()
            
            response = controller.add_ephemeral_hidden_service(
                ports={80: (self.host, self.port)},
                await_publication=True
            )
            
            self.onion_address = response.service_id
            print(f"[TOR] ✅ Onion: {self.onion_address}.onion")
            controller.close()
        except Exception as e:
            print(f"[TOR] ⚠️  Failed: {e}")
            self.use_tor = False
    
    def start(self):
        """Start the server"""
        try:
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.running = True
            
            print("\n" + "="*70)
            print("     TERMINAL CHAT SYSTEM - SERVER")
            print("="*70)
            print(f"\n🚀 Server started")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n🔐 ROOM CODE: {self.room_code}")
            
            if self.use_tor and self.onion_address:
                print(f"\n🧅 TOR MODE")
                print(f"   Onion: {self.onion_address}.onion")
            else:
                print(f"\n🌐 DIRECT MODE")
                print(f"   IP: {self.host}")
                print(f"   Port: {self.port}")
            
            print(f"\n📱 Share code with clients")
            print("="*70)
            print("Waiting for connections...\n")
            
            while self.running:
                try:
                    client_socket, address = self.server.accept()
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    thread.start()
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] {e}")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle client connection"""
        username = None
        try:
            # Request code
            client_socket.send(b"CODE:")
            received_code = client_socket.recv(1024).decode('utf-8').strip()
            
            if received_code != self.room_code:
                client_socket.send(b"INVALID_CODE")
                client_socket.close()
                return
            
            client_socket.send(b"CODE_OK")
            
            # Request username
            client_socket.send(b"USERNAME:")
            username = client_socket.recv(1024).decode('utf-8').strip()
            
            if not username or len(username) > 20:
                client_socket.send(b"INVALID_USERNAME")
                client_socket.close()
                return
            
            with self.lock:
                if username in self.clients.values():
                    client_socket.send(b"USERNAME_TAKEN")
                    client_socket.close()
                    return
                self.clients[client_socket] = username
            
            client_socket.send(b"USERNAME_OK")
            
            print(f"[+] {username} joined")
            self.broadcast(f"✅ {username} joined", exclude=client_socket, is_system=True)
            
            # Send user list
            user_list = ", ".join(sorted(self.clients.values()))
            client_socket.send(f"USERS:{user_list}".encode('utf-8'))
            
            # Message loop
            while self.running:
                try:
                    message = client_socket.recv(1024).decode('utf-8').strip()
                    
                    if not message:
                        continue
                    
                    if message.lower() in ['/quit', '/exit', '/leave']:
                        break
                    
                    if message.startswith('/'):
                        self.handle_command(client_socket, message)
                    else:
                        self.broadcast_message(username, message)
                except:
                    break
        
        finally:
            if client_socket in self.clients:
                with self.lock:
                    username = self.clients.pop(client_socket, username)
                if username:
                    print(f"[-] {username} left")
                    self.broadcast(f"👋 {username} left", is_system=True)
            
            try:
                client_socket.close()
            except:
                pass
    
    def handle_command(self, client_socket: socket.socket, command: str):
        """Handle chat commands"""
        cmd = command.lower().strip()
        
        if cmd == '/users':
            user_list = ", ".join(sorted(self.clients.values()))
            client_socket.send(f"👥 Online: {user_list}".encode('utf-8'))
        elif cmd == '/help':
            client_socket.send("/users, /help, /quit".encode('utf-8'))
        elif cmd == '/count':
            client_socket.send(f"👥 Users: {len(self.clients)}".encode('utf-8'))
    
    def broadcast_message(self, username: str, message: str):
        """Broadcast message from user"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {username}: {message}"
        self.broadcast(formatted)
        print(f"[MSG] {formatted}")
    
    def broadcast(self, message: str, exclude: socket.socket = None, is_system: bool = False):
        """Send message to all clients"""
        with self.lock:
            for sock in list(self.clients.keys()):
                if sock == exclude:
                    continue
                try:
                    prefix = "SYSTEM:" if is_system else "MSG:"
                    sock.send(f"{prefix}{message}".encode('utf-8'))
                except:
                    pass
    
    def stop(self):
        """Stop server"""
        self.running = False
        try:
            self.server.close()
        except:
            pass
        print("\n[SERVER] Stopped\n")


if __name__ == "__main__":
    use_tor = len(sys.argv) > 1 and sys.argv[1] == '--tor'
    
    if use_tor and not TOR_AVAILABLE:
        print("\n⚠️  Tor not installed!")
        print("   pip3 install stem --break-system-packages\n")
        sys.exit(1)
    
    try:
        server = ChatServer(use_tor=use_tor)
        server.start()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"Error: {e}")