#!/usr/bin/env python3
"""
Terminal Chat System - Environment Test & Auto-Installer
========================================================

This script:
  ✅ Tests all system requirements
  ✅ Checks Python version
  ✅ Verifies installed packages
  ✅ Tests Tor availability
  ✅ Auto-installs missing dependencies
  ✅ Generates comprehensive report
  ✅ Provides next steps

Run this FIRST to prepare your system!
"""

import os
import sys
import platform
import subprocess
import socket
import time
from pathlib import Path
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class EnvironmentTester:
    """Test and manage chat system environment"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.failed_tests = []
        self.warnings = []
        self.installed_new = []
        self.test_results = {}
        
    def print_header(self):
        """Print beautiful header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}")
        print("╔" + "=" * 78 + "╗")
        print("║" + " " * 78 + "║")
        print("║" + "  🔐 TERMINAL CHAT SYSTEM - ENVIRONMENT TEST & AUTO-INSTALLER  🔐".center(78) + "║")
        print("║" + " " * 78 + "║")
        print("╚" + "=" * 78 + "╝")
        print(f"{Colors.END}\n")
        
    def print_section(self, title):
        """Print section header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'═' * 80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}▶ {title}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'═' * 80}{Colors.END}\n")
    
    def print_success(self, message):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def print_error(self, message):
        """Print error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
        
    def print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def print_info(self, message):
        """Print info message"""
        print(f"{Colors.CYAN}ℹ️  {message}{Colors.END}")
    
    # ═════════════════════════════════════════════════════════════════════════
    # TEST FUNCTIONS
    # ═════════════════════════════════════════════════════════════════════════
    
    def test_system_info(self):
        """Display system information"""
        self.print_section("System Information")
        
        print(f"  OS:              {self.system}")
        print(f"  Platform:        {platform.platform()}")
        print(f"  Python:          {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print(f"  Python Path:     {sys.executable}")
        print(f"  Time:            {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Architecture:    {platform.machine()}")
        
        return True
    
    def test_python_version(self):
        """Test if Python version meets requirements"""
        self.print_section("Python Version Check")
        
        required_version = (3, 6)
        current_version = (self.python_version.major, self.python_version.minor)
        
        if current_version >= required_version:
            self.print_success(f"Python {self.python_version.major}.{self.python_version.minor} meets requirements (3.6+)")
            self.test_results['python_version'] = True
            return True
        else:
            self.print_error(f"Python {self.python_version.major}.{self.python_version.minor} is too old (need 3.6+)")
            self.failed_tests.append("Python version too old")
            self.test_results['python_version'] = False
            return False
    
    def test_pip(self):
        """Test if pip is available"""
        self.print_section("Pip Package Manager")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.print_success(f"Pip is available: {result.stdout.strip()}")
                self.test_results['pip'] = True
                return True
            else:
                self.print_error("Pip not available")
                self.failed_tests.append("Pip not working")
                self.test_results['pip'] = False
                return False
        except Exception as e:
            self.print_error(f"Error testing pip: {e}")
            self.failed_tests.append("Pip test failed")
            self.test_results['pip'] = False
            return False
    
    def test_socket(self):
        """Test socket availability (built-in)"""
        self.print_section("Socket Library (Built-in)")
        
        try:
            import socket as sock_test
            self.print_success("Socket library available (built-in)")
            self.test_results['socket'] = True
            return True
        except ImportError:
            self.print_error("Socket library not available")
            self.failed_tests.append("Socket import failed")
            self.test_results['socket'] = False
            return False
    
    def test_threading(self):
        """Test threading availability (built-in)"""
        self.print_section("Threading Library (Built-in)")
        
        try:
            import threading as thread_test
            self.print_success("Threading library available (built-in)")
            self.test_results['threading'] = True
            return True
        except ImportError:
            self.print_error("Threading library not available")
            self.failed_tests.append("Threading import failed")
            self.test_results['threading'] = False
            return False
    
    def test_pysocks(self):
        """Test if PySocks is installed"""
        self.print_section("PySocks Library (For Tor Support)")
        
        try:
            import socks
            version = socks.__version__ if hasattr(socks, '__version__') else "unknown"
            self.print_success(f"PySocks is installed (version: {version})")
            self.test_results['pysocks'] = True
            return True
        except ImportError:
            self.print_warning("PySocks not installed (optional, needed for Tor)")
            self.print_info("Install with: pip3 install PySocks --break-system-packages")
            self.test_results['pysocks'] = False
            return False
    
    def test_stem(self):
        """Test if Stem is installed"""
        self.print_section("Stem Library (For Tor Hidden Services)")
        
        try:
            from stem.control import Controller
            self.print_success("Stem is installed (Tor hidden services supported)")
            self.test_results['stem'] = True
            return True
        except ImportError:
            self.print_warning("Stem not installed (optional, needed for hidden services)")
            self.print_info("Install with: pip3 install stem --break-system-packages")
            self.test_results['stem'] = False
            return False
    
    def test_tor_installed(self):
        """Test if Tor is installed on system"""
        self.print_section("Tor Binary (System)")
        
        try:
            result = subprocess.run(
                ["tor", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                self.print_success(f"Tor is installed: {version_line}")
                self.test_results['tor_installed'] = True
                return True
            else:
                self.print_error("Tor binary not working")
                self.test_results['tor_installed'] = False
                return False
        except FileNotFoundError:
            self.print_warning("Tor binary not found in PATH")
            self.print_info("Download from: https://www.torproject.org/download/")
            self.test_results['tor_installed'] = False
            return False
        except Exception as e:
            self.print_warning(f"Could not verify Tor: {e}")
            self.test_results['tor_installed'] = False
            return False
    
    def test_network(self):
        """Test internet connectivity"""
        self.print_section("Internet Connectivity")
        
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            self.print_success("Internet connectivity verified")
            self.test_results['network'] = True
            return True
        except (socket.timeout, socket.error):
            self.print_warning("No internet connection (needed for installation only)")
            self.test_results['network'] = False
            return False
    
    def test_chat_files(self):
        """Test if chat application files exist"""
        self.print_section("Chat Application Files")
        
        required_files = [
            "chat_server.py",
            "chat_client.py",
            "test_chat.py"
        ]
        
        current_dir = Path(".")
        found_files = 0
        
        for filename in required_files:
            if (current_dir / filename).exists():
                self.print_success(f"Found: {filename}")
                found_files += 1
            else:
                self.print_warning(f"Missing: {filename}")
        
        self.test_results['chat_files'] = found_files == len(required_files)
        return found_files > 0
    
    def test_chat_files_tor(self):
        """Test if Tor chat files exist"""
        self.print_section("Tor Chat Files (Optional)")
        
        tor_files = [
            "chat_client_tor.py",
            "chat_server_onion.py"
        ]
        
        current_dir = Path(".")
        found_files = 0
        
        for filename in tor_files:
            if (current_dir / filename).exists():
                self.print_success(f"Found: {filename}")
                found_files += 1
            else:
                self.print_warning(f"Missing: {filename}")
        
        self.test_results['tor_chat_files'] = found_files == len(tor_files)
        return found_files > 0
    
    # ═════════════════════════════════════════════════════════════════════════
    # INSTALLATION FUNCTIONS
    # ═════════════════════════════════════════════════════════════════════════
    
    def install_pysocks(self):
        """Install PySocks library"""
        print(f"\n{Colors.YELLOW}Installing PySocks...{Colors.END}")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "PySocks", "--break-system-packages", "-q"
            ])
            self.print_success("PySocks installed successfully!")
            self.installed_new.append("PySocks")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Failed to install PySocks via pip")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install",
                    "PySocks", "--user", "-q"
                ])
                self.print_success("PySocks installed (user mode)")
                self.installed_new.append("PySocks")
                return True
            except subprocess.CalledProcessError:
                self.print_error("Could not install PySocks")
                return False
    
    def install_stem(self):
        """Install Stem library"""
        print(f"\n{Colors.YELLOW}Installing Stem...{Colors.END}")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "stem", "--break-system-packages", "-q"
            ])
            self.print_success("Stem installed successfully!")
            self.installed_new.append("Stem")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Failed to install Stem")
            return False
    
    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        print(f"\n{Colors.YELLOW}Upgrading pip...{Colors.END}")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install",
                "--upgrade", "pip", "-q"
            ])
            self.print_success("Pip upgraded successfully!")
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Could not upgrade pip (not critical)")
            return False
    
    # ═════════════════════════════════════════════════════════════════════════
    # REPORT FUNCTIONS
    # ═════════════════════════════════════════════════════════════════════════
    
    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_section("Test Results Summary")
        
        print(f"\n{Colors.BOLD}Core Requirements:{Colors.END}")
        print(f"  Python Version:      {'✅ PASS' if self.test_results.get('python_version') else '❌ FAIL'}")
        print(f"  Pip:                 {'✅ PASS' if self.test_results.get('pip') else '❌ FAIL'}")
        print(f"  Socket (built-in):   {'✅ PASS' if self.test_results.get('socket') else '❌ FAIL'}")
        print(f"  Threading (built-in):{'✅ PASS' if self.test_results.get('threading') else '❌ FAIL'}")
        
        print(f"\n{Colors.BOLD}Optional (Tor Support):{Colors.END}")
        print(f"  PySocks:             {'✅ PASS' if self.test_results.get('pysocks') else '⚠️  MISSING (optional)'}")
        print(f"  Stem:                {'✅ PASS' if self.test_results.get('stem') else '⚠️  MISSING (optional)'}")
        print(f"  Tor Binary:          {'✅ PASS' if self.test_results.get('tor_installed') else '⚠️  MISSING (optional)'}")
        
        print(f"\n{Colors.BOLD}System:{Colors.END}")
        print(f"  Internet:            {'✅ PASS' if self.test_results.get('network') else '⚠️  NO CONNECTION'}")
        print(f"  Chat Files:          {'✅ PASS' if self.test_results.get('chat_files') else '⚠️  MISSING'}")
        print(f"  Tor Chat Files:      {'✅ PASS' if self.test_results.get('tor_chat_files') else '⚠️  MISSING (optional)'}")
    
    def print_summary(self):
        """Print installation summary"""
        self.print_section("Installation Summary")
        
        if self.installed_new:
            print(f"{Colors.GREEN}✅ Successfully installed:{Colors.END}")
            for package in self.installed_new:
                print(f"   • {package}")
        else:
            print(f"{Colors.CYAN}ℹ️  No new packages needed to install{Colors.END}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  Warnings:{Colors.END}")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        if self.failed_tests:
            print(f"\n{Colors.RED}❌ Failed tests:{Colors.END}")
            for test in self.failed_tests:
                print(f"   • {test}")
        else:
            print(f"\n{Colors.GREEN}✅ All critical tests passed!{Colors.END}")
    
    def print_next_steps(self):
        """Print next steps"""
        self.print_section("Next Steps")
        
        print(f"{Colors.BOLD}Your environment is ready!{Colors.END}\n")
        
        if not self.test_results.get('pysocks'):
            print(f"1. {Colors.YELLOW}(Optional) Install PySocks for Tor support:{Colors.END}")
            print(f"   pip3 install PySocks --break-system-packages\n")
        
        if not self.test_results.get('tor_installed'):
            print(f"2. {Colors.YELLOW}(Optional) Install Tor:{Colors.END}")
            print(f"   Download from: https://www.torproject.org/download/\n")
        
        print(f"3. {Colors.GREEN}Start the chat system:{Colors.END}")
        print(f"   {Colors.CYAN}Terminal 1: python3 chat_server.py{Colors.END}")
        print(f"   {Colors.CYAN}Terminal 2: python3 chat_client.py{Colors.END}\n")
        
        if self.test_results.get('pysocks') and self.test_results.get('tor_installed'):
            print(f"4. {Colors.GREEN}Or use Tor encryption:{Colors.END}")
            print(f"   {Colors.CYAN}Terminal 1: tor --SocksPort 9050{Colors.END}")
            print(f"   {Colors.CYAN}Terminal 2: python3 chat_server.py{Colors.END}")
            print(f"   {Colors.CYAN}Terminal 3: python3 chat_client_tor.py{Colors.END}\n")
        
        print(f"5. {Colors.GREEN}Run tests to verify:{Colors.END}")
        print(f"   {Colors.CYAN}python3 test_chat.py{Colors.END}\n")
    
    def print_environment_info(self):
        """Print environment information for debugging"""
        self.print_section("Environment Information")
        
        print(f"Python Executable: {sys.executable}")
        print(f"Python Prefix:     {sys.prefix}")
        print(f"Python Path:")
        for path in sys.path[:3]:
            print(f"  • {path}")
        
        print(f"\nPIP Location:")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "pip"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n')[:3]:
                    if line:
                        print(f"  {line}")
        except:
            print(f"  (Could not determine)")
    
    # ═════════════════════════════════════════════════════════════════════════
    # MAIN RUN FUNCTION
    # ═════════════════════════════════════════════════════════════════════════
    
    def run_all_tests(self, auto_install=True):
        """Run all tests and install missing packages"""
        
        self.print_header()
        
        # System information
        self.test_system_info()
        
        # Core tests
        self.test_python_version()
        self.test_pip()
        self.test_socket()
        self.test_threading()
        self.test_network()
        
        # Optional tests
        self.test_pysocks()
        self.test_stem()
        self.test_tor_installed()
        
        # Application files
        self.test_chat_files()
        self.test_chat_files_tor()
        
        # Print report
        self.generate_report()
        self.print_environment_info()
        
        # Auto-install missing packages (if network available)
        if auto_install and self.test_results.get('network'):
            self.print_section("Auto-Installation (Optional)")
            
            if not self.test_results.get('pysocks'):
                print(f"\nPySocks is recommended for Tor encryption.")
                try:
                    response = input(f"{Colors.CYAN}Install PySocks? (y/n): {Colors.END}").lower().strip()
                    if response in ['y', 'yes']:
                        self.install_pysocks()
                except (KeyboardInterrupt, EOFError):
                    print("\n(Skipped)")
            
            if not self.test_results.get('stem'):
                print(f"\nStem is needed for Tor hidden services (advanced).")
                try:
                    response = input(f"{Colors.CYAN}Install Stem? (y/n): {Colors.END}").lower().strip()
                    if response in ['y', 'yes']:
                        self.install_stem()
                except (KeyboardInterrupt, EOFError):
                    print("\n(Skipped)")
        
        # Print summary
        self.print_summary()
        
        # Print next steps
        self.print_next_steps()
        
        # Final status
        self.print_final_status()
    
    def print_final_status(self):
        """Print final status"""
        self.print_section("Final Status")
        
        if self.test_results.get('python_version') and self.test_results.get('pip'):
            print(f"{Colors.GREEN}{Colors.BOLD}✅ YOUR SYSTEM IS READY!{Colors.END}\n")
            print(f"Your Terminal Chat System is ready to use.")
            print(f"All required dependencies are installed or available.\n")
            
            if self.test_results.get('pysocks'):
                print(f"{Colors.GREEN}✅ Tor encryption is available{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Tor encryption not available (optional){Colors.END}")
            
            if self.test_results.get('tor_installed'):
                print(f"{Colors.GREEN}✅ Tor binary is installed{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️  Tor binary not installed (optional){Colors.END}")
            
            print(f"\n{Colors.BOLD}Next: Read README.md or run:${Colors.END}")
            print(f"  {Colors.CYAN}python3 chat_server.py{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}❌ System has critical issues{Colors.END}\n")
            print(f"Please fix the errors above and try again.")
        
        print(f"\n{Colors.BOLD}{'═' * 80}{Colors.END}\n")


def main():
    """Main entry point"""
    tester = EnvironmentTester()
    
    try:
        tester.run_all_tests(auto_install=True)
        return 0
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Test interrupted by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}❌ Unexpected error: {e}{Colors.END}")
        return 1


if __name__ == "__main__":
    sys.exit(main())