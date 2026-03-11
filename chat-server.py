#!/usr/bin/env python3
"""
Terminal Chat System - Server
Internet-ready + Optional Tor privacy
"""

import socket
import threading
import string
import random
from datetime import datetime
from typing import Dict
import sys
import urllib.request

# Optional Tor import
try:
    from stem.control import Controller
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False


class ChatServer:
    """Chat server with internet connectivity"""

    def __init__(self, use_tor=False):
        # Bind to all interfaces so anyone on the internet can connect
        self.host = "0.0.0.0"
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

    def _get_local_ip(self):
        """Get local network IP (LAN)"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"

    def _get_public_ip(self):
        """Fetch public IP so friends over the internet know where to connect"""
        services = [
            "https://api.ipify.org",
            "https://checkip.amazonaws.com",
            "https://icanhazip.com",
        ]
        for url in services:
            try:
                with urllib.request.urlopen(url, timeout=5) as resp:
                    return resp.read().decode("utf-8").strip()
            except:
                continue
        return None

    def _generate_code(self):
        """Generate 10-character room code"""
        chars = string.ascii_uppercase + string.digits
        return "".join(random.choice(chars) for _ in range(10))

    def _setup_tor(self):
        """Optional: Setup Tor hidden service"""
        try:
            print("[TOR] Setting up hidden service...")
            controller = Controller.from_port(port=9051)
            controller.authenticate()
            response = controller.add_ephemeral_hidden_service(
                ports={80: ("127.0.0.1", self.port)},
                await_publication=True,
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
            self.server.listen(10)
            self.running = True

            local_ip = self._get_local_ip()
            print("\n" + "=" * 70)
            print("     TERMINAL CHAT SYSTEM - SERVER")
            print("=" * 70)
            print(f"\n🚀 Server started")
            print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n🔐 ROOM CODE: {self.room_code}")

            if self.use_tor and self.onion_address:
                print(f"\n🧅 TOR MODE")
                print(f"   Onion: {self.onion_address}.onion")
            else:
                print(f"\n🌐 NETWORK INFO")
                print(f"   Local IP  (same WiFi) : {local_ip}:{self.port}")

                print(f"\n⏳ Fetching your public IP...")
                public_ip = self._get_public_ip()
                if public_ip:
                    print(f"   Public IP (internet)  : {public_ip}:{self.port}")
                    print(f"\n📌 SHARE THIS WITH YOUR FRIEND:")
                    print(f"   IP   → {public_ip}")
                    print(f"   Port → {self.port}")
                    print(f"   Code → {self.room_code}")
                else:
                    print(f"   Public IP : Could not detect (check your internet connection)")
                    print(f"               Visit https://whatismyip.com to find it manually")

                print(f"\n⚠️  PORT FORWARDING REQUIRED for internet connections:")
                print(f"   1. Open your router settings (usually http://192.168.1.1)")
                print(f"   2. Add a port forwarding rule:")
                print(f"      External Port : {self.port}")
                print(f"      Internal IP   : {local_ip}")
                print(f"      Internal Port : {self.port}")
                print(f"      Protocol      : TCP")
                print(f"   3. Share your Public IP + Room Code with your friend")
                print(f"\n   💡 No router access? Use ngrok instead:")
                print(f"      pip3 install ngrok --break-system-packages")
                print(f"      ngrok tcp {self.port}")
                print(f"      (Share the ngrok address instead of your IP)")

            print(f"\n{'=' * 70}")
            print("Waiting for connections...\n")

            while self.running:
                try:
                    client_socket, address = self.server.accept()
                    print(f"[+] Incoming connection from {address[0]}")
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True,
                    )
                    thread.start()
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    if self.running:
                        print(f"[ERROR] {e}")
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"\n❌ Port {self.port} is already in use!")
                print(f"   Kill the process using it or restart your terminal.\n")
            else:
                print(f"[ERROR] {e}")
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            self.stop()

    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle client connection"""
        username = None
        try:
            client_socket.settimeout(30)

            # Request code
            client_socket.send(b"CODE:")
            received_code = client_socket.recv(1024).decode("utf-8").strip()

            if received_code != self.room_code:
                client_socket.send(b"INVALID_CODE")
                client_socket.close()
                print(f"[-] {address[0]} sent wrong room code")
                return

            client_socket.send(b"CODE_OK")

            # Request username
            client_socket.send(b"USERNAME:")
            username = client_socket.recv(1024).decode("utf-8").strip()

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
            client_socket.settimeout(None)  # Remove timeout for chat phase

            print(f"[+] {username} joined (from {address[0]})")
            self.broadcast(f"✅ {username} joined", exclude=client_socket, is_system=True)

            user_list = ", ".join(sorted(self.clients.values()))
            client_socket.send(f"USERS:{user_list}".encode("utf-8"))

            # Message loop
            while self.running:
                try:
                    message = client_socket.recv(4096).decode("utf-8").strip()

                    if not message:
                        continue

                    if message.lower() in ["/quit", "/exit", "/leave"]:
                        break

                    if message.startswith("/"):
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

        if cmd == "/users":
            user_list = ", ".join(sorted(self.clients.values()))
            client_socket.send(f"SYSTEM:👥 Online: {user_list}".encode("utf-8"))
        elif cmd == "/help":
            client_socket.send(b"SYSTEM:/users, /help, /count, /quit")
        elif cmd == "/count":
            client_socket.send(
                f"SYSTEM:👥 Users online: {len(self.clients)}".encode("utf-8")
            )

    def broadcast_message(self, username: str, message: str):
        """Broadcast message from user"""
        timestamp = datetime.now().strftime("%H:%M")
        formatted = f"[{timestamp}] {username}: {message}"
        self.broadcast(formatted)
        print(f"[MSG] {formatted}")

    def broadcast(
        self,
        message: str,
        exclude: socket.socket = None,
        is_system: bool = False,
    ):
        """Send message to all clients"""
        with self.lock:
            for sock in list(self.clients.keys()):
                if sock == exclude:
                    continue
                try:
                    prefix = "SYSTEM:" if is_system else "MSG:"
                    sock.send(f"{prefix}{message}".encode("utf-8"))
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
    use_tor = len(sys.argv) > 1 and sys.argv[1] == "--tor"

    if use_tor and not TOR_AVAILABLE:
        print("\n⚠️  Stem not installed!")
        print("   pip3 install stem --break-system-packages\n")
        sys.exit(1)

    try:
        server = ChatServer(use_tor=use_tor)
        server.start()
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"Error: {e}")