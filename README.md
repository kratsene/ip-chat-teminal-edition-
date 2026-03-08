# ip-chat-teminal-edition-# AnonymChat - Terminal-Based Anonymous Messaging

A lightweight, privacy-focused terminal application for anonymous real-time conversations. Connect with others without revealing your identity, powered by end-to-end encryption and zero-knowledge architecture.

## Features

- **Complete Anonymity**: No account creation, no personal data collection
- **Real-Time Messaging**: Instant message delivery with minimal latency
- **End-to-End Encryption**: All messages encrypted before leaving your device
- **Terminal-Native**: Works seamlessly in your favorite shell
- **Peer Discovery**: Find and connect with other users anonymously
- **Session-Based**: Temporary connections that leave no permanent trace
- **Cross-Platform**: Runs on Linux, macOS, and Windows (WSL)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Internet connection

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/anonymchat.git
cd anonymchat

# Install dependencies
pip install -r requirements.txt

# Run the application
python anonymchat.py
```

### Via pip

```bash
pip install anonymchat
anonymchat
```

## Usage

### Starting a Session

```bash
$ anonymchat
Welcome to AnonymChat
================================

[1] Start New Chat
[2] Join Existing Chat
[3] Settings
[4] Exit

Choose an option: 1
```

### Creating a New Chat

```
[1] Start New Chat

Your Session ID: c7f2e9a1
Share this ID with someone to let them join your chat.

Waiting for connection...
```

### Joining a Chat

```
[2] Join Existing Chat
Enter Session ID: c7f2e9a1

Connected to anonymous user
Type messages below (press Ctrl+C to exit)
```

### Sending Messages

```
You: Hello, is anyone there?
Other: Hi! How's it going?
You: Just exploring this app
```

## Configuration

Create a `.anonymchat` config file in your home directory to customize settings:

```yaml
# ~/.anonymchat
encryption: aes-256-gcm
server: wss://relay.anonymchat.io
timeout: 300
buffer_size: 1024
show_timestamps: true
theme: dark
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `encryption` | string | aes-256-gcm | Encryption algorithm to use |
| `server` | string | wss://relay.anonymchat.io | Server URL |
| `timeout` | int | 300 | Session timeout in seconds |
| `buffer_size` | int | 1024 | Message buffer size |
| `show_timestamps` | bool | true | Display message timestamps |
| `theme` | string | dark | Color theme (dark/light) |

## Security & Privacy

### How It Works

1. **No Registration**: Connect instantly without creating an account
2. **Ephemeral Sessions**: Conversations exist only during active connection
3. **Encryption**: All messages encrypted using AES-256-GCM
4. **No Logging**: Server does not store message content or metadata
5. **Zero Knowledge**: Server cannot decrypt your messages even if breached

### Privacy Policy

- We never collect personal information
- Messages are encrypted end-to-end and not stored server-side
- Session IDs are temporary and single-use
- No cookies, tracking, or analytics
- IP addresses are not logged

## Commands

While in a chat session, use these commands:

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/exit` | Leave the chat session |
| `/info` | Show session information |
| `/clear` | Clear chat history from screen |
| `/ping` | Check connection status |
| `/block` | Block future connections from this user |
| `/report` | Report inappropriate behavior |

## Examples

### Example 1: Quick Peer-to-Peer Chat

```bash
# User A
$ anonymchat
Session ID: a1b2c3d4

# User B (in another terminal/machine)
$ anonymchat
Enter Session ID: a1b2c3d4
Connected!
```

### Example 2: Using with Shell Piping

```bash
echo "Hello from the pipe" | anonymchat --session a1b2c3d4
```

## Troubleshooting

### Connection Issues

**Problem**: "Failed to connect to server"
- Check your internet connection
- Verify the server URL in config
- Try reconnecting in a few moments

**Problem**: "Invalid Session ID"
- Ensure the Session ID is typed correctly (case-sensitive)
- Session IDs expire after 30 minutes of inactivity

### Message Delivery

**Problem**: Messages not appearing
- Check that both users are connected
- Verify encryption is enabled
- Try `/ping` to test connection

**Problem**: Slow message delivery
- Network latency may affect speed
- Try connecting to a closer server location

## System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|------------|
| Python | 3.8 | 3.10+ |
| RAM | 64 MB | 256 MB |
| Bandwidth | 10 Kbps | 1 Mbps |
| Storage | 10 MB | 50 MB |

## Architecture

```
┌─────────────────┐         ┌─────────────────┐
│   Client A      │         │   Client B      │
│  (Terminal)     │         │  (Terminal)     │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │  Encrypted Messages       │
         │  (AES-256-GCM)           │
         └───────────┬───────────────┘
                     │
            ┌────────▼─────────┐
            │  Relay Server    │
            │  (Message Pass)  │
            └──────────────────┘
```

## API (For Developers)

If you want to integrate AnonymChat into your own application:

```python
from anonymchat import Client

# Create client
client = Client()

# Start a session
session = client.create_session()
print(f"Session ID: {session.id}")

# Connect to existing session
other = client.connect(session_id="c7f2e9a1")

# Send message
client.send("Hello!")

# Receive messages
for message in client.listen():
    print(f"Received: {message}")
```

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

- Use responsibly and respectfully
- This tool is for legitimate anonymous communication
- Users are responsible for complying with local laws and regulations
- The developers are not responsible for misuse of this application

## Support

- **Documentation**: [docs.anonymchat.io](https://docs.anonymchat.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/anonymchat/issues)
- **Email**: support@anonymchat.io

## Roadmap

- [ ] Voice messaging support
- [ ] File transfer with encryption
- [ ] Message reactions and emojis
- [ ] Group chat sessions
- [ ] Mobile app (iOS/Android)
- [ ] Offline message queuing
- [ ] Multi-language support

## Acknowledgments

- Cryptography library contributors
- Open-source community
- Privacy advocates and security researchers

---

**Stay Anonymous. Stay Safe. Stay Connected.**

*Last Updated: 2026*
