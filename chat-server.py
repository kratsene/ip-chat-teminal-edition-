#!/usr/bin/env python3
"""
Terminal Chat System - Server
Automatic setup with zero configuration
"""

import socket
import threading
import string
import random
from datetime import datetime
from typing import Dict
import sys


class ChatServer:
    """Simple chat server with auto-detection"""
    
    def __init__(self):
        # Auto-detect the best host
        self.host = self._get_host()
        self.port = 5000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients: Dict[socket.socket, str] = {}
        self.lock = threading.Lock()
        self.running = False
        
        # Generate room code
        self.room_code = self._generate_code()
    
    def _get_host(self):
        """Auto-detect best host to use"""
        try:
            # Try to get actual network IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "0.0.0.0"
    
    def _generate_code(self):
        """Generate 10-digit room code"""
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(10))
    
    def start(self):
        """Start the chat server"""
        try:
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.host, self.port))
            self.server.listen(5)
            self.running = True
            
            print("\n" + "="*70)
            print("     TERMINAL CHAT SYSTEM - SERVER")
            print("="*70)
            print(f"\n🚀 Server started on {self.host}:{self.port}")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n🔐 ROOM AUTHENTICATION CODE: {self.room_code}")
            print(f"   📱 Share this code with clients")
            print(f"   🌐 IP Address: {self.host}")
            print(f"   🔌 Port: {self.port}\n")
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
            print(f"[ERROR] Failed to start server: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client"""
        username = None
        try:
            # Request code
            client_socket.send(b"CODE:")
            received_code = client_socket.recv(1024).decode('utf-8').strip()
            
            if received_code != self.room_code:
                print(f"[AUTH] ❌ Invalid code from {address[0]}")
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
            
            print(f"[SERVER] ✅ {username} connected from {address[0]}:{address[1]}")
            self.broadcast(f"✅ {username} joined the chat", exclude=client_socket, is_system=True)
            
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
                        self.handle_command(client_socket, message, username)
                    else:
                        self.broadcast_message(username, message)
                except:
                    break
        
        finally:
            if client_socket in self.clients:
                with self.lock:
                    username = self.clients.pop(client_socket, username)
                if username:
                    print(f"[SERVER] ❌ {username} disconnected")
                    self.broadcast(f"👋 {username} left the chat", is_system=True)
            
            try:
                client_socket.close()
            except:
                pass
    
    def handle_command(self, client_socket: socket.socket, command: str, username: str):
        """Handle commands"""
        cmd = command.lower().strip()
        
        if cmd == '/users':
            user_list = ", ".join(sorted(self.clients.values()))
            response = f"👥 Users online: {user_list}"
            client_socket.send(response.encode('utf-8'))
        elif cmd == '/help':
            help_text = (
                "📋 Commands:\n"
                "  /users - List online users\n"
                "  /help - Show this help\n"
                "  /quit - Disconnect"
            )
            client_socket.send(help_text.encode('utf-8'))
        elif cmd == '/count':
            count = len(self.clients)
            client_socket.send(f"👥 Total users: {count}".encode('utf-8'))
    
    def broadcast_message(self, username: str, message: str):
        """Broadcast message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] {username}: {message}"
        self.broadcast(formatted)
        print(f"[MESSAGE] {formatted}")
    
    def broadcast(self, message: str, exclude: socket.socket = None, is_system: bool = False):
        """Send to all clients"""
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
        print("\n[SERVER] Shutting down...\n")


if __name__ == "__main__":
    try:
        server = ChatServer()
        server.start()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)