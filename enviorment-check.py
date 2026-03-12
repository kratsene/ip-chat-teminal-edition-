#!/usr/bin/env python3
"""
AnonymChat - Environment Setup
================================
Installs all dependencies and verifies Tor is working correctly.
Run this ONCE before starting the chat system.
"""

import os
import sys
import platform
import subprocess
import socket
import time
import urllib.request
import json
from pathlib import Path
from datetime import datetime


class C:
    CYAN   = '\033[96m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    RED    = '\033[91m'
    BLUE   = '\033[94m'
    BOLD   = '\033[1m'
    END    = '\033[0m'


def banner():
    print(f"\n{C.BOLD}{C.CYAN}")
    print("╔" + "═" * 68 + "╗")
    print("║" + "  🔐  AnonymChat — Environment Setup  🔐  ".center(68) + "║")
    print("║" + "  No accounts. No logs. No traces.  ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print(C.END)


def section(title):
    print(f"\n{C.BOLD}{C.BLUE}{'─' * 68}{C.END}")
    print(f"{C.BOLD}{C.BLUE}  ▶  {title}{C.END}")
    print(f"{C.BOLD}{C.BLUE}{'─' * 68}{C.END}\n")


def ok(msg):   print(f"{C.GREEN}  ✅  {msg}{C.END}")
def fail(msg): print(f"{C.RED}  ❌  {msg}{C.END}")
def warn(msg): print(f"{C.YELLOW}  ⚠️   {msg}{C.END}")
def info(msg): print(f"{C.CYAN}  ℹ️   {msg}{C.END}")


def run_cmd(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout + r.stderr).strip()
    except Exception as e:
        return False, str(e)


def pip_install(package, label=None):
    label = label or package
    print(f"  ⏳  Installing {label} ...", end=" ", flush=True)
    ok_flag, _ = run_cmd([sys.executable, "-m", "pip", "install",
                          package, "--break-system-packages", "-q"])
    if not ok_flag:
        ok_flag, _ = run_cmd([sys.executable, "-m", "pip", "install",
                              package, "--user", "-q"])
    print(f"{C.GREEN}done{C.END}" if ok_flag else f"{C.RED}failed{C.END}")
    return ok_flag


def port_open(port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex(("127.0.0.1", port))
        s.close()
        return result == 0
    except:
        return False


def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False


def get_os():
    return platform.system().lower()


def fetch(url, timeout=8):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AnonymChat/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode().strip()
    except:
        return None


# ─────────────────────────────────────────────────────────────────────────────

def check_system():
    section("System Check")
    py = sys.version_info
    print(f"  OS       : {platform.system()} {platform.release()}")
    print(f"  Python   : {py.major}.{py.minor}.{py.micro}")
    print(f"  Time     : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    if py < (3, 6):
        fail("Python 3.6+ required.")
        sys.exit(1)
    ok(f"Python {py.major}.{py.minor} — OK")

    good, _ = run_cmd([sys.executable, "-m", "pip", "--version"])
    if not good:
        fail("pip not found.")
        sys.exit(1)
    ok("pip — OK")

    if not has_internet():
        fail("No internet connection.")
        sys.exit(1)
    ok("Internet — connected")


def install_python_packages():
    section("Python Packages")

    try:
        from stem.control import Controller
        ok("stem — already installed")
    except ImportError:
        if pip_install("stem", "stem  (Tor hidden service control)"):
            ok("stem installed")
        else:
            warn("stem install failed")

    try:
        import socks
        ok("PySocks — already installed")
    except ImportError:
        if pip_install("PySocks", "PySocks  (Tor SOCKS5 for client)"):
            ok("PySocks installed")
        else:
            warn("PySocks install failed")


def check_tor_traffic():
    """
    Ask the Tor Project's own API if our traffic is going through Tor.
    Works regardless of HOW Tor is active (daemon, VPN, Orbot, OnionFruit).
    """
    print("  ⏳  Checking if traffic routes through Tor ...", end=" ", flush=True)
    data = fetch("https://check.torproject.org/api/ip", timeout=10)
    if data:
        try:
            parsed = json.loads(data)
            is_tor = parsed.get("IsTor", False)
            exit_ip = parsed.get("IP", "unknown")
            print(f"{C.GREEN}done{C.END}")
            return is_tor, exit_ip
        except:
            pass
    print(f"{C.YELLOW}could not reach check.torproject.org{C.END}")
    return False, None


def detect_and_setup_tor():
    section("Tor Detection & Setup")

    socks_up   = port_open(9050)
    control_up = port_open(9051)
    traffic_tor, exit_ip = check_tor_traffic()

    print()

    # ── Case 1: Everything already perfect ────────────────────────────────
    if socks_up and control_up and traffic_tor:
        ok("Tor SOCKS proxy    — port 9050 active")
        ok("Tor control port   — port 9051 active")
        ok(f"Traffic via Tor    — exit IP: {exit_ip}")
        return True

    # ── Case 2: Ports open but traffic check failed (no internet via Tor) ─
    if socks_up and control_up:
        ok("Tor SOCKS proxy    — port 9050 active")
        ok("Tor control port   — port 9051 active")
        warn("Could not verify traffic through Tor (check.torproject.org unreachable)")
        info("Ports are open — assuming Tor is working. Proceeding...")
        return True

    # ── Case 3: Tor VPN active (traffic through Tor) but no daemon ports ──
    if traffic_tor and not socks_up and not control_up:
        ok(f"Tor VPN detected   — traffic going through Tor (exit IP: {exit_ip})")
        warn("But Tor daemon ports 9050 and 9051 are NOT open")
        warn("Tor VPN routes traffic but cannot create .onion addresses")
        print()
        print(f"  {C.BOLD}The server needs Tor daemon running alongside Tor VPN.{C.END}")
        print(f"  Keep Tor VPN / OnionFruit running AND also start Tor Expert Bundle:\n")
        _print_windows_tor_start() if get_os() == "windows" else _print_linux_tor_start()
        print()
        # Try to start Tor daemon anyway
        return _try_start_tor_daemon()

    # ── Case 4: SOCKS open but no control port ────────────────────────────
    if socks_up and not control_up:
        ok("Tor SOCKS proxy    — port 9050 active")
        fail("Tor control port   — port 9051 NOT open")
        warn("Control port is required to create .onion addresses")
        info("Restarting Tor with correct flags...")
        _kill_tor()
        return _try_start_tor_daemon()

    # ── Case 5: Nothing running at all ────────────────────────────────────
    fail("Tor is not running")
    info("Installing and starting Tor daemon...")
    installed = _install_tor_binary()
    if not installed:
        return False
    return _try_start_tor_daemon()


def _install_tor_binary():
    good, out = run_cmd(["tor", "--version"], timeout=5)
    if good:
        ok(f"Tor binary — {out.split(chr(10))[0]}")
        return True

    os_name = get_os()
    print("  ⏳  Installing Tor...", end=" ", flush=True)

    if os_name == "linux":
        distro = ""
        try:
            with open("/etc/os-release") as f:
                distro = f.read().lower()
        except:
            pass
        if any(x in distro for x in ["ubuntu", "debian", "mint", "pop"]):
            good, _ = run_cmd(["sudo", "apt-get", "install", "-y", "tor"], timeout=120)
        elif any(x in distro for x in ["fedora", "rhel", "centos"]):
            good, _ = run_cmd(["sudo", "dnf", "install", "-y", "tor"], timeout=120)
        elif any(x in distro for x in ["arch", "manjaro"]):
            good, _ = run_cmd(["sudo", "pacman", "-S", "tor", "--noconfirm"], timeout=120)
        print(f"{C.GREEN}done{C.END}" if good else f"{C.RED}failed{C.END}")
        return good

    elif os_name == "darwin":
        good, _ = run_cmd(["brew", "install", "tor"], timeout=180)
        print(f"{C.GREEN}done{C.END}" if good else f"{C.RED}failed{C.END}")
        return good

    elif os_name == "windows":
        print(f"{C.YELLOW}manual install needed{C.END}")
        print()
        fail("Cannot auto-install Tor on Windows.")
        _print_windows_tor_start()
        return False

    print(f"{C.RED}unknown OS{C.END}")
    return False


def _try_start_tor_daemon():
    print("  ⏳  Starting Tor (SocksPort 9050 + ControlPort 9051)...", end="", flush=True)
    proc = _launch_tor()
    if not proc:
        print(f" {C.RED}failed to launch{C.END}")
        _print_manual_start_hint()
        return False

    for _ in range(45):
        time.sleep(1)
        print(".", end="", flush=True)
        if port_open(9050) and port_open(9051):
            print(f" {C.GREEN}ready{C.END}")
            ok("Tor SOCKS proxy    — port 9050 active")
            ok("Tor control port   — port 9051 active")
            return True

    print(f" {C.YELLOW}timeout{C.END}")
    fail("Tor did not start in 45 seconds.")
    _print_manual_start_hint()
    return False


def _launch_tor():
    try:
        return subprocess.Popen(
            ["tor",
             "--SocksPort", "9050",
             "--ControlPort", "9051",
             "--CookieAuthentication", "1",
             "--Log", "notice stdout"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None


def _kill_tor():
    os_name = get_os()
    if os_name in ["linux", "darwin"]:
        run_cmd(["pkill", "-f", "tor"], timeout=5)
    elif os_name == "windows":
        run_cmd(["taskkill", "/F", "/IM", "tor.exe"], timeout=5)
    time.sleep(2)


def _print_manual_start_hint():
    print()
    print("  Start Tor manually in a NEW terminal window:\n")
    if get_os() == "windows":
        _print_windows_tor_start()
    else:
        _print_linux_tor_start()
    print("\n  Then run this script again.\n")


def _print_windows_tor_start():
    print(f"  {C.BOLD}Windows — Tor Expert Bundle:{C.END}")
    print(f"  1. Download from: https://www.torproject.org/download/tor/")
    print(f"  2. Extract the zip")
    print(f"  3. Open PowerShell in the extracted tor\\ folder")
    print(f"  4. Run:")
    print(f"     {C.CYAN}.\\tor.exe --SocksPort 9050 --ControlPort 9051 --CookieAuthentication 1{C.END}")
    print(f"  5. Wait for 'Bootstrapped 100%' then run this script again")


def _print_linux_tor_start():
    print(f"  {C.CYAN}tor --SocksPort 9050 --ControlPort 9051 --CookieAuthentication 1{C.END}")


def test_hidden_service():
    section("Testing .onion Address Creation")

    try:
        from stem.control import Controller
    except ImportError:
        fail("stem not installed.")
        return False

    if not port_open(9051):
        fail("Control port 9051 not open — cannot create .onion address.")
        return False

    print("  ⏳  Connecting to Tor control port ...", end=" ", flush=True)
    try:
        with Controller.from_port(port=9051) as ctrl:
            ctrl.authenticate()
            print(f"{C.GREEN}connected{C.END}")

            print("  ⏳  Creating test .onion address ...", end=" ", flush=True)
            # Use create_ephemeral_hidden_service (correct for stem 1.5+)
            resp  = ctrl.create_ephemeral_hidden_service(
                {80: 5000}, await_publication=False
            )
            onion = resp.service_id
            print(f"{C.GREEN}done{C.END}\n")

            ok(".onion creation works!")
            print(f"\n  {C.BOLD}Sample address generated:{C.END}")
            print(f"  {C.CYAN}{C.BOLD}  {onion}.onion{C.END}\n")
            info("A fresh .onion is generated every time chat-server.py starts.")
            info("Share it only with the person you want to chat with.")

            ctrl.remove_ephemeral_hidden_service(onion)
            return True

    except Exception as e:
        print(f"{C.RED}failed{C.END}")
        fail(f"Tor control error: {e}")
        if "Authentication" in str(e):
            info("Try running this script as administrator / with sudo")
        return False


def print_summary(tor_ok, hidden_ok):
    section("Setup Complete — Quick Start")

    if tor_ok and hidden_ok:
        print(f"  {C.GREEN}{C.BOLD}✅  Everything ready. Your chat is fully traceless.{C.END}\n")
        print(f"  {C.BOLD}Step 1{C.END}  Start the server (new terminal):")
        print(f"           {C.CYAN}python3 chat-server.py{C.END}")
        print(f"           It prints a .onion address + Room Code.\n")
        print(f"  {C.BOLD}Step 2{C.END}  Share ONLY these 2 things with your friend:")
        print(f"           • The .onion address")
        print(f"           • The Room Code\n")
        print(f"  {C.BOLD}Step 3{C.END}  Friend connects (needs Orbot / Tor running):")
        print(f"           {C.CYAN}python3 chat-cilent.py --tor{C.END}\n")
        print(f"  {C.BOLD}Step 4{C.END}  You join too (second terminal):")
        print(f"           {C.CYAN}python3 chat-cilent.py --tor{C.END}")
        print(f"           Enter the same .onion your server printed.\n")
        print(f"  {C.BOLD}Note:{C.END}  If your friend has Tor VPN active (not SOCKS mode):")
        print(f"           {C.CYAN}python3 chat-cilent.py{C.END}  ← no --tor flag needed\n")
    else:
        print(f"  {C.YELLOW}{C.BOLD}⚠️   Setup incomplete.{C.END}\n")
        if not tor_ok:
            print(f"  Tor is not running. Start Tor daemon and run this script again.")
        elif not hidden_ok:
            print(f"  Tor is running but .onion creation failed.")
            print(f"  Make sure Tor is started with --ControlPort 9051 --CookieAuthentication 1")
        print()

    print(f"  {C.BOLD}Why this is traceless:{C.END}")
    print(f"  • Real IPs never revealed — yours or your friend's")
    print(f"  • Encrypted through 3+ Tor relays")
    print(f"  • .onion address changes every session")
    print(f"  • Zero accounts, zero signups, zero third-party services")
    print(f"  • ISP cannot see content or destination\n")


def main():
    banner()
    check_system()
    install_python_packages()
    tor_ok     = detect_and_setup_tor()
    hidden_ok  = test_hidden_service() if tor_ok else False
    print_summary(tor_ok, hidden_ok)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{C.YELLOW}  Setup interrupted.{C.END}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n{C.RED}  Unexpected error: {e}{C.END}\n")
        raise
