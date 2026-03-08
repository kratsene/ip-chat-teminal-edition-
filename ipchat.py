#!/usr/bin/env python3
"""ipchat.py - simple LAN multicast chat for Termux/phones/desktops

Usage: python3 ipchat.py --name Alice

This script uses UDP multicast to broadcast JSON messages to peers
on the same WiFi/LAN. It's single-file, requires only Python 3.
"""
import argparse
import json
import socket
import struct
import threading
import time
from datetime import datetime


def make_listener(sock, name):
    while True:
        try:
            data, addr = sock.recvfrom(65536)
        except OSError:
            break
        if not data:
            continue
        try:
            payload = json.loads(data.decode('utf-8'))
        except Exception:
            continue
        sender = payload.get('name')
        msg = payload.get('msg')
        ts = payload.get('ts')
        if sender == name:
            continue
        try:
            t = datetime.fromisoformat(ts)
            timestr = t.strftime('%H:%M:%S')
        except Exception:
            timestr = ts
        print('\n[{time}] {who}: {m}'.format(time=timestr, who=sender, m=msg))
        print('> ', end='', flush=True)


def send_message(send_sock, group, port, name, text):
    payload = {'name': name, 'ts': datetime.utcnow().isoformat(), 'msg': text}
    b = json.dumps(payload).encode('utf-8')
    send_sock.sendto(b, (group, port))


def build_multicast_socket(group, port, listen_iface=''):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.bind(('', port))
    except Exception:
        sock.bind((listen_iface, port))

    # Join multicast group
    mreq = struct.pack('4sL', socket.inet_aton(group), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock


def main():
    p = argparse.ArgumentParser(description='LAN multicast chat (Termux-friendly)')
    p.add_argument('--name', '-n', required=True, help='display name')
    p.add_argument('--group', default='224.1.1.1', help='multicast group (default 224.1.1.1)')
    p.add_argument('--port', '-p', type=int, default=50000, help='UDP port (default 50000)')
    p.add_argument('--ttl', type=int, default=1, help='multicast TTL (default 1)')
    args = p.parse_args()

    name = args.name
    group = args.group
    port = args.port

    recv_sock = build_multicast_socket(group, port)

    # Sender socket (multicast TTL)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ttl_bin = struct.pack('b', args.ttl)
    send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)

    listener = threading.Thread(target=make_listener, args=(recv_sock, name), daemon=True)
    listener.start()

    print('Joined group {g}:{p} as {n}'.format(g=group, p=port, n=name))
    print('Commands: /nick NEWNAME  /quit')
    try:
        while True:
            try:
                text = input('> ')
            except EOFError:
                break
            if not text:
                continue
            if text.startswith('/nick '):
                newname = text.split(' ', 1)[1].strip()
                if newname:
                    name = newname
                    print('Name changed to', name)
                continue
            if text.strip() in ('/quit', '/exit'):
                break
            send_message(send_sock, group, port, name, text)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            recv_sock.close()
        except Exception:
            pass
        try:
            send_sock.close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
