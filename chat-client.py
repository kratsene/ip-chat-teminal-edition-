#!/usr/bin/env python3
"""
AnonymChat - Client
Connects to server via .onion address through Tor.
Use --tor flag if Tor daemon / Orbot (SOCKS mode) is running on port 9050.
If Tor VPN is active system-wide, run without --tor flag.
"""

import socket
import threading
import sys

try:
    import socks
    TOR_AVAILABLE = True
except ImportError:
    TOR_AVAILABLE = False
    socks = None


class ChatClient:
    def __init__(self, use_tor=False):
        self.socket = None
        self.username = None
        self.room_code = None
        self.connected = False
        self.receiving = False
        self.use_tor = use_tor and TOR_AVAILABLE

    def connect(self):
        print("\n" + "=" * 70)
        print("     AnonymChat — CLIENT")
        if self.use_tor:
            print("     🧅 Routing through Tor SOCKS proxy (port 9050)")
        else:
            print("     🌐 Direct connection (use --tor for Tor SOCKS mode)")
        print("=" * 70 + "\n")

        print("🌐 Server address (.onion or IP):")
        print("   For Tor hidden service enter the .onion address")
        print("   For local test enter 127.0.0.1")
        host = input("   > ").strip()
        if not host:
            host = "127.0.0.1"

        # Port — default 5000, but allow override for ngrok etc.
        print("\n🔌 Port (press Enter for 5000):")
        port_input = input("   > ").strip()
        try:
            port = int(port_input) if port_input else 5000
        except ValueError:
            port = 5000

        print("\n🔐 Room Code (10 characters):")
        self.room_code = input("   > ").strip().upper()

        if len(self.room_code) != 10:
            print("❌ Room code must be exactly 10 characters!")
            return

        print("\n👤 Username (no spaces, max 20 chars):")
        self.username = input("   > ").strip()

        if not self.username or len(self.username) > 20 or " " in self.username:
            print("❌ Invalid username!")
            return

        print(f"\n{'=' * 70}")
        print(f"📡 Connecting to {host}:{port} ...")
        if self.use_tor:
            print("   Routing through Tor SOCKS5 on 127.0.0.1:9050")
        print()

        try:
            if self.use_tor and socks:
                self.socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # .onion connections can take longer — use 120s timeout
            self.socket.settimeout(120)
            self.socket.connect((host, port))
            self.connected = True

            # Authentication
            prompt = self.socket.recv(1024).decode("utf-8").strip()
            if prompt == "CODE:":
                self.socket.send(self.room_code.encode("utf-8"))
                response = self.socket.recv(1024).decode("utf-8").strip()
                if response != "CODE_OK":
                    print("❌ Wrong room code!")
                    self.disconnect()
                    return

            prompt = self.socket.recv(1024).decode("utf-8").strip()
            if prompt == "USERNAME:":
                self.socket.send(self.username.encode("utf-8"))
                response = self.socket.recv(1024).decode("utf-8").strip()
                if response == "USERNAME_TAKEN":
                    print("Username already taken. Try a different one.")
                    self.disconnect()
                    return
                elif not response.startswith("USERNAME_OK"):
                    print(f"Error: {response}")
                    self.disconnect()
                    return

            # USERNAME_OK and USERS: sometimes arrive merged in one packet
            # e.g. "USERNAME_OKUSERS:alice, bob" — handle both cases
            if "USERS:" in response:
                users = response.split("USERS:", 1)[1].strip()
            else:
                users_msg = self.socket.recv(1024).decode("utf-8").strip()
                users = users_msg.replace("USERS:", "").strip() if users_msg.startswith("USERS:") else "?"

            self.socket.settimeout(None)

            print(f"✅ Connected!")
            print(f"👤 You      : {self.username}")
            print(f"👥 Online   : {users}")
            print(f"{'=' * 70}")
            print("💬 Type a message and press Enter to send.")
            print("   Commands: /users  /count  /help  /quit\n")

            self.receiving = True
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.input_loop()

        except socket.timeout:
            print(f"\n❌ Connection timed out!")
            if host.endswith(".onion"):
                print("   Make sure Tor is running and the .onion address is correct.")
                print("   .onion connections can take up to 60 seconds — try again.")
            else:
                print(f"   Is the server running at {host}:{port}?")
            if self.use_tor:
                print("   Also check Tor daemon / Orbot is running on port 9050.")

        except ConnectionRefusedError:
            print(f"\n❌ Connection refused!")
            if self.use_tor:
                print("   → Tor SOCKS proxy is not running on port 9050.")
                print("   → Start Tor daemon or Orbot first, then try again.")
            else:
                print(f"   → Is the server running at {host}:{port}?")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            if "Proxy connection" in str(e) or "SOCKS" in str(e):
                print("   Tor SOCKS proxy issue — make sure Tor is running on port 9050.")

        finally:
            self.disconnect()

    def input_loop(self):
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
        try:
            while self.connected and self.receiving:
                try:
                    data = self.socket.recv(4096).decode("utf-8").strip()
                    if not data:
                        print("\r⚠️  Disconnected from server.\n")
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
        self.connected = False
        self.receiving = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        print("\n👋 Disconnected\n")


if __name__ == "__main__":
    use_tor = "--tor" in sys.argv

    if use_tor and not TOR_AVAILABLE:
        print("\n⚠️  PySocks not installed!")
        print("   Run: python3 enviorment-check.py")
        print("   Or:  pip install PySocks --break-system-packages\n")
        sys.exit(1)

    try:
        client = ChatClient(use_tor=use_tor)
        client.connect()
    except KeyboardInterrupt:
        print("\n👋 Client stopped")
    except Exception as e:
        print(f"Error: {e}")
