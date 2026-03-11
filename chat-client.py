#!/usr/bin/env python3
"""
Terminal Chat System - Client
Internet-ready + Optional Tor privacy via Orbot
"""

import socket
import threading
import sys

# Optional Tor (PySocks) import
try:
    import socks
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False
    socks = None


class ChatClient:
    """Chat client for local and internet connections"""

    def __init__(self, use_tor=False):
        self.socket = None
        self.username = None
        self.room_code = None
        self.connected = False
        self.receiving = False
        self.use_tor = use_tor and TOR_AVAILABLE

    def connect(self):
        """Connect to server"""
        print("\n" + "=" * 70)
        print("     TERMINAL CHAT SYSTEM - CLIENT")
        if self.use_tor:
            print("     🧅 TOR MODE (via Orbot/Tor SOCKS proxy)")
        print("=" * 70 + "\n")

        # Get server IP
        print("🌐 Server IP or domain (press Enter for 127.0.0.1):")
        print("   (For internet: enter the server's PUBLIC IP address)")
        host = input("   > ").strip()
        if not host:
            host = "127.0.0.1"

        port = 5000

        # Get room code
        print("\n🔐 Room code (10 characters, from server):")
        self.room_code = input("   > ").strip().upper()

        if len(self.room_code) != 10:
            print("❌ Room code must be exactly 10 characters!")
            return

        # Get username
        print("\n👤 Username (1–20 characters, no spaces):")
        self.username = input("   > ").strip()

        if not self.username or len(self.username) > 20:
            print("❌ Username must be 1–20 characters!")
            return

        if " " in self.username:
            print("❌ Username cannot contain spaces!")
            return

        print(f"\n{'=' * 70}")
        print(f"📡 Connecting to {host}:{port}...")
        if self.use_tor:
            print("   Routing through Tor SOCKS proxy (localhost:9050)...")
        print()

        try:
            # Create socket
            if self.use_tor and socks:
                self.socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.set_proxy(socks.SOCKS5, "localhost", 9050)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.socket.settimeout(15)  # Longer timeout for internet connections
            self.socket.connect((host, port))
            self.connected = True

            # --- Authentication ---
            prompt = self.socket.recv(1024).decode("utf-8").strip()
            if prompt == "CODE:":
                self.socket.send(self.room_code.encode("utf-8"))
                response = self.socket.recv(1024).decode("utf-8").strip()

                if response != "CODE_OK":
                    print("❌ Invalid room code! Double-check with the server host.")
                    self.disconnect()
                    return

            prompt = self.socket.recv(1024).decode("utf-8").strip()
            if prompt == "USERNAME:":
                self.socket.send(self.username.encode("utf-8"))
                response = self.socket.recv(1024).decode("utf-8").strip()

                if response == "USERNAME_TAKEN":
                    print("❌ That username is already taken! Try a different one.")
                    self.disconnect()
                    return
                elif response != "USERNAME_OK":
                    print(f"❌ {response}")
                    self.disconnect()
                    return

            users_msg = self.socket.recv(1024).decode("utf-8").strip()
            users = "Unknown"
            if users_msg.startswith("USERS:"):
                users = users_msg.replace("USERS:", "").strip()

            self.socket.settimeout(None)  # No timeout during chat

            print(f"✅ Connected!")
            print(f"👤 You are: {self.username}")
            print(f"👥 Online : {users}")
            print(f"{'=' * 70}")
            print("💬 Type a message and press Enter to send.")
            print("   Commands: /users  /help  /count  /quit\n")

            # Start receive thread
            self.receiving = True
            receive_thread = threading.Thread(
                target=self.receive_messages, daemon=True
            )
            receive_thread.start()

            self.input_loop()

        except socket.timeout:
            print(f"\n❌ Connection timed out!")
            print(f"   • Is the server running?")
            print(f"   • Is the IP address correct? ({host})")
            print(f"   • If connecting over internet: is port {port} forwarded on the server's router?")
            if self.use_tor:
                print(f"   • Is Orbot running and connected? Check the Orbot app.")
        except ConnectionRefusedError:
            print(f"\n❌ Connection refused!")
            print(f"   • The server is not running, or the port is blocked.")
            print(f"   • Server IP: {host}, Port: {port}")
            if self.use_tor:
                print(f"\n   🧅 TOR NOTE: 'Connection refused' on Tor usually means:")
                print(f"      • Orbot is not running → Open Orbot app and tap 'Start'")
                print(f"      • Orbot is not connected → Wait for it to show 'Connected'")
                print(f"      • You are using Tor Browser (Play Store) instead of Orbot.")
                print(f"        Tor Browser does NOT provide a SOCKS proxy for other apps.")
                print(f"        ✅ Install ORBOT from Play Store or F-Droid instead.")
        except OSError as e:
            if "Network is unreachable" in str(e):
                print(f"\n❌ Network unreachable. Check your internet connection.")
            else:
                print(f"\n❌ Connection error: {e}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self.disconnect()

    def input_loop(self):
        """Main input loop"""
        try:
            while self.connected:
                try:
                    message = input(f"{self.username}: ").strip()
                    if not message:
                        continue

                    self.socket.send(message.encode("utf-8"))

                    if message.lower() in ["/quit", "/exit", "/leave"]:
                        break
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
        except:
            pass

    def receive_messages(self):
        """Receive messages from server in background"""
        try:
            while self.connected and self.receiving:
                try:
                    data = self.socket.recv(4096).decode("utf-8").strip()
                    if not data:
                        print("\r\n⚠️  Connection lost (server closed or network issue).")
                        break

                    if data.startswith("MSG:"):
                        content = data.replace("MSG:", "", 1).strip()
                        print(f"\r{content}\n{self.username}: ", end="", flush=True)
                    elif data.startswith("SYSTEM:"):
                        content = data.replace("SYSTEM:", "", 1).strip()
                        print(f"\r💬 {content}\n{self.username}: ", end="", flush=True)
                    else:
                        print(f"\r{data}\n{self.username}: ", end="", flush=True)
                except:
                    break
        except:
            pass
        finally:
            self.connected = False

    def disconnect(self):
        """Disconnect cleanly"""
        self.connected = False
        self.receiving = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass

        print("\n👋 Disconnected\n")

    def _divider(self):
        return "=" * 70


if __name__ == "__main__":
    use_tor = len(sys.argv) > 1 and sys.argv[1] == "--tor"

    if use_tor and not TOR_AVAILABLE:
        print("\n⚠️  PySocks is not installed (required for Tor mode)!")
        print("   Install it with:")
        print("   pip3 install PySocks --break-system-packages\n")
        print("   Also make sure Orbot is running on your device (NOT Tor Browser).")
        sys.exit(1)

    try:
        client = ChatClient(use_tor=use_tor)
        client.connect()
    except KeyboardInterrupt:
        print("\n👋 Client stopped")
    except Exception as e:
        print(f"Error: {e}")