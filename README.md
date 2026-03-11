# 🔐 AnonymChat

<div align="center">

[![Python Version](https://img.shields.io/badge/Python-3.6%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=for-the-badge)](https://github.com)
[![Tests](https://img.shields.io/badge/Tests-25%2F25%20Passing-brightgreen?style=for-the-badge)](test-chat.py)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge)](README.md)
[![Security](https://img.shields.io/badge/Security-Tor%20via%20Orbot-red?style=for-the-badge&logo=torproject)](https://www.torproject.org)

## 🚀 Multi-Client Terminal Chat — Works Over the Internet

A terminal-based chat system that works between **any two devices anywhere in the world**, with optional Tor/Orbot encryption for privacy.

[Features](#-features) • [Quick Start](#-quick-start) • [Internet Setup](#-connecting-over-the-internet) • [Tor / Orbot](#-tor--orbot-setup) • [Troubleshooting](#-troubleshooting)

</div>

---

## ✨ Features

- ✅ **Works over the internet** — Connect between Kolkata and Mumbai (or anywhere)
- ✅ **Multi-client** — Multiple users can join at once
- ✅ **Real-time messaging** — Instant delivery with timestamps
- ✅ **Room codes** — Auto-generated 10-character code prevents unwanted joins
- ✅ **Zero dependencies** — Base system uses only Python's standard library
- ✅ **Optional Tor** — Route through Tor network via Orbot for anonymity
- ✅ **Tor hidden services** — Run as .onion for maximum privacy
- ✅ **Cross-platform** — Windows, macOS, Linux

---

## 📋 System Requirements

| Requirement | Version | Purpose |
|---|---|---|
| Python | 3.6+ | Core runtime |
| PySocks | Latest | Tor SOCKS support (optional) |
| Stem | Latest | Tor hidden services (optional) |
| Orbot (Android) | Latest | Tor proxy on mobile (optional) |

---

## 🚀 Quick Start

### Same Network (Local / Same WiFi)

```bash
# Terminal 1 — start server
python3 chat-server.py

# Terminal 2 — start client (same machine or same WiFi)
python3 chat-cilent.py
# Enter the local IP shown by the server
```

### Over the Internet (Different Cities / Networks)

See the [Internet Setup section](#-connecting-over-the-internet) below — this requires one extra step (port forwarding or ngrok).

---

## 🌐 Connecting Over the Internet

This is the most important section if you want to chat with someone far away.

### The Problem

When the server runs, it only has a **local IP** (e.g. `192.168.1.5`) — this is only reachable from the same WiFi. For a friend in another city to connect, they need your **public IP**, and your router needs to forward traffic to your machine.

### Method A — Port Forwarding (Recommended, Free)

**On the server side (the person running `chat-server.py`):**

1. Run the server — it will print your **Public IP** automatically:
   ```
   Public IP (internet) : 103.xx.xx.xx:5000
   ```

2. Open your **router settings** (usually http://192.168.1.1 or http://192.168.0.1 in your browser).

3. Find **Port Forwarding** (may be under "Advanced", "NAT", or "Virtual Server").

4. Add a new rule:
   ```
   External Port : 5000
   Internal IP   : (your local IP shown by the server, e.g. 192.168.1.5)
   Internal Port : 5000
   Protocol      : TCP
   ```

5. Save and apply.

6. Share your **Public IP** and **Room Code** with your friend:
   ```
   IP   → 103.xx.xx.xx
   Port → 5000
   Code → A7B2K9F4M1
   ```

**On the client side (your friend):**
```bash
python3 chat-cilent.py
# When asked for Server IP: enter 103.xx.xx.xx  (the public IP)
# Enter the Room Code
# Enter a username
```

---

### Method B — ngrok (Easiest, No Router Access Needed)

If you can't access your router (e.g. hostel, office, rented connection), use ngrok — it creates a public tunnel to your local server for free.

```bash
# Step 1: Install ngrok
pip3 install pyngrok --break-system-packages
# OR download from https://ngrok.com/download

# Step 2: Start your server first
python3 chat-server.py

# Step 3: In a new terminal, create the tunnel
ngrok tcp 5000
```

ngrok will print something like:
```
Forwarding  tcp://0.tcp.ngrok.io:12345 -> localhost:5000
```

Share `0.tcp.ngrok.io` as the IP and `12345` as the port with your friend.  
Your friend connects using:
```bash
python3 chat-cilent.py
# Server IP: 0.tcp.ngrok.io
# Port: 5000  (the client always uses 5000; ngrok handles the mapping)
```

> **Note:** With ngrok, tell your friend to enter the full host `0.tcp.ngrok.io` at the IP prompt. The client port stays 5000.

---

## 🧅 Tor / Orbot Setup

### ⚠️ Important: Use Orbot, NOT Tor Browser

A common mistake is installing **Tor Browser** (available on Play Store) thinking it enables Tor for other apps. It does not — Tor Browser only routes its own internal traffic.

To use Tor as a SOCKS proxy (which this chat app requires), you need **Orbot**.

| App | What it does | Works for this chat? |
|---|---|---|
| Tor Browser | Browsing only | ❌ No |
| **Orbot** | System-wide SOCKS5 proxy on port 9050 | ✅ Yes |

### Install Orbot

- **Android**: [Orbot on Play Store](https://play.google.com/store/apps/details?id=org.torproject.android) or [F-Droid](https://f-droid.org/packages/org.torproject.android.binary/)
- **iOS**: [Onion Browser](https://apps.apple.com/app/onion-browser/id519296448) (different flow, limited proxy use)
- **Linux/macOS**: `sudo apt install tor` or `brew install tor`
- **Windows**: Download [Tor Expert Bundle](https://www.torproject.org/download/tor/) (not Tor Browser)

### Using Tor Mode

```bash
# Step 1: Start Orbot (Android) or Tor daemon (desktop)
#   Android: Open Orbot → tap Start → wait for "Connected"
#   Linux/macOS: tor --SocksPort 9050
#   Windows: Run tor.exe from the Expert Bundle

# Step 2: Install PySocks
pip3 install PySocks --break-system-packages

# Step 3: Run server (no --tor flag needed unless using hidden service)
python3 chat-server.py

# Step 4: Run client with Tor
python3 chat-cilent.py --tor
```

### Tor Hidden Service (Maximum Privacy — Server IP Hidden)

```bash
# Requires: stem library + Tor running with ControlPort
pip3 install stem --break-system-packages

# Start Tor with control port
tor --SocksPort 9050 --ControlPort 9051 --CookieAuthentication 1

# Start server in Tor hidden service mode
python3 chat-server.py --tor
# Server will print an .onion address

# Client connects to the .onion address
python3 chat-cilent.py --tor
# Enter the .onion address when asked for server IP
```

---

## 📖 Commands (In Chat)

| Command | Description |
|---|---|
| `/users` | List online users |
| `/count` | Show number of online users |
| `/help` | Show available commands |
| `/quit` | Disconnect |

---

## 📁 File Overview

```
AnonymChat/
├── chat-server.py        # Server — run this on the host machine
├── chat-cilent.py        # Client — run this to connect
├── test-chat.py          # Unit tests
├── enviorment-check.py   # Environment checker & auto-installer
├── README.md             # This file
└── LICENSE               # MIT License
```

---

## 🚨 Troubleshooting

### "Connection refused" (no Tor)
- Make sure the server is running before the client tries to connect.
- Check the IP and port are correct.
- If connecting over the internet, verify port forwarding is set up correctly.

### "Connection refused" (Tor mode)
This almost always means the Tor SOCKS proxy is not running on port 9050.
- **Android**: Open **Orbot** (not Tor Browser), tap **Start**, wait until it says **Connected**.
- **Linux/macOS**: Run `tor --SocksPort 9050` in a terminal.
- **Windows**: Start `tor.exe` from the Tor Expert Bundle.

### "Connection timed out"
- Port forwarding may not be set up, or the router firewall is blocking port 5000.
- Try Method B (ngrok) instead.

### "Address already in use"
- Another instance of the server is already running.
- Kill it with `pkill -f chat-server.py` (Linux/macOS) or close the terminal.

### Friend can connect locally but not from internet
- Port forwarding is the missing step. Follow Method A or use ngrok (Method B).

### ngrok tunnel works but port is different
- Your friend should enter the ngrok hostname (e.g. `0.tcp.ngrok.io`) as the server IP.  
  The client code uses port 5000 internally — ngrok handles the external port mapping.

---

## ⚙️ Architecture

### Direct Internet Connection (with port forwarding)
```
Friend's Client → Internet → Router (port forward) → Your Machine (server)
```

### ngrok Tunnel
```
Friend's Client → Internet → ngrok servers → localhost:5000 (your server)
```

### Tor via Orbot
```
Client → Orbot (SOCKS5 :9050) → Tor Network (3+ hops) → Server
```

### Tor Hidden Service
```
Client → Tor Network ← Server (.onion address, IP hidden)
```

---

## 🧪 Testing

```bash
python3 test-chat.py
# Expected: 25/25 tests passing
```

---

## ⚖️ Legal Notice

Tor usage may be restricted in some countries. Verify local laws before use.  
This tool is intended for legitimate privacy protection and secure communication.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Tor Project](https://www.torproject.org/) — Onion routing & anonymity
- [Orbot](https://orbot.app/) — Tor proxy for Android
- [PySocks](https://github.com/Anorov/PySocks) — SOCKS client library
- [Stem](https://stem.torproject.org/) — Tor control library
- [ngrok](https://ngrok.com/) — Secure tunneling

---

<div align="center">

**AnonymChat** | Secure • Cross-network • Open Source

</div>