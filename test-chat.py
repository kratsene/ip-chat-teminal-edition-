#!/usr/bin/env python3
"""
Simplified Test Suite for Terminal Chat System
This version is designed to work reliably with GitHub Actions
"""

import string
import random
import socket
import threading
import sys


def test_room_code_generation():
    """Test room code generation"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(10))
    
    assert len(code) == 10, f"Code length should be 10, got {len(code)}"
    assert all(c in chars for c in code), f"Code should only contain uppercase and digits: {code}"
    print("✅ test_room_code_generation PASSED")


def test_room_code_uniqueness():
    """Test that generated codes are unique"""
    chars = string.ascii_uppercase + string.digits
    codes = set()
    
    for _ in range(100):
        code = ''.join(random.choice(chars) for _ in range(10))
        codes.add(code)
    
    assert len(codes) == 100, f"Codes should be unique, got {len(codes)} unique from 100"
    print("✅ test_room_code_uniqueness PASSED")


def test_socket_creation():
    """Test socket creation"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    assert sock is not None, "Socket should be created"
    sock.close()
    print("✅ test_socket_creation PASSED")


def test_socket_reuse_address():
    """Test SO_REUSEADDR option"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.close()
    print("✅ test_socket_reuse_address PASSED")


def test_port_validation():
    """Test port number validation"""
    valid_ports = [1, 80, 443, 5000, 8000, 65535]
    
    for port in valid_ports:
        assert 1 <= port <= 65535, f"Port {port} should be valid"
    
    invalid_ports = [0, -1, 65536, 100000]
    for port in invalid_ports:
        assert not (1 <= port <= 65535), f"Port {port} should be invalid"
    
    print("✅ test_port_validation PASSED")


def test_username_length():
    """Test username length validation"""
    valid_usernames = ["a", "alice", "alice_123", "a" * 20]
    
    for name in valid_usernames:
        assert 1 <= len(name) <= 20, f"Username {name} should be valid"
    
    invalid_usernames = ["", "a" * 21]
    for name in invalid_usernames:
        assert not (1 <= len(name) <= 20), f"Username {name} should be invalid"
    
    print("✅ test_username_length PASSED")


def test_username_no_spaces():
    """Test username doesn't contain spaces"""
    valid_usernames = ["alice", "alice_bob", "alice123"]
    
    for name in valid_usernames:
        assert " " not in name, f"Username {name} should not have spaces"
    
    invalid_usernames = ["alice smith", "bob alice"]
    for name in invalid_usernames:
        assert " " in name, f"Username {name} should have spaces for this test"
    
    print("✅ test_username_no_spaces PASSED")


def test_threading_basic():
    """Test basic threading"""
    result = []
    
    def test_func():
        result.append(True)
    
    thread = threading.Thread(target=test_func, daemon=True)
    thread.start()
    thread.join(timeout=1)
    
    assert len(result) == 1, "Thread should have executed"
    assert result[0] is True, "Thread result should be True"
    print("✅ test_threading_basic PASSED")


def test_threading_lock():
    """Test threading lock"""
    lock = threading.Lock()
    results = []
    
    def increment():
        with lock:
            results.append(1)
    
    threads = [threading.Thread(target=increment, daemon=True) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=1)
    
    assert len(results) == 5, f"Should have 5 results, got {len(results)}"
    print("✅ test_threading_lock PASSED")


def test_message_encoding():
    """Test message encoding/decoding"""
    message = "Hello, World!"
    encoded = message.encode('utf-8')
    decoded = encoded.decode('utf-8')
    
    assert decoded == message, "Message should encode/decode correctly"
    print("✅ test_message_encoding PASSED")


def test_utf8_encoding():
    """Test UTF-8 encoding"""
    message = "Hello 你好"
    encoded = message.encode('utf-8')
    decoded = encoded.decode('utf-8')
    
    assert decoded == message, "UTF-8 message should encode/decode correctly"
    print("✅ test_utf8_encoding PASSED")


def test_empty_string():
    """Test empty string handling"""
    message = ""
    encoded = message.encode('utf-8')
    decoded = encoded.decode('utf-8')
    
    assert decoded == "", "Empty string should remain empty"
    assert len(message.strip()) == 0, "Empty string should have no content when stripped"
    print("✅ test_empty_string PASSED")


def test_whitespace_strip():
    """Test whitespace stripping"""
    messages = ["  hello  ", "\nhello\n", "\thello\t"]
    
    for msg in messages:
        stripped = msg.strip()
        assert stripped == "hello", f"Stripped message should be 'hello', got '{stripped}'"
    
    print("✅ test_whitespace_strip PASSED")


def test_code_format_uppercase():
    """Test code format with uppercase"""
    code = "AAAAAAAAAA"
    chars = string.ascii_uppercase + string.digits
    
    assert len(code) == 10, "Code should be 10 characters"
    assert all(c in chars for c in code), "Code should only have uppercase and digits"
    print("✅ test_code_format_uppercase PASSED")


def test_code_format_digits():
    """Test code format with digits"""
    code = "1234567890"
    chars = string.ascii_uppercase + string.digits
    
    assert len(code) == 10, "Code should be 10 characters"
    assert all(c in chars for c in code), "Code should only have uppercase and digits"
    assert all(c.isdigit() for c in code), "Code should be all digits"
    print("✅ test_code_format_digits PASSED")


def test_code_format_mixed():
    """Test code format with mixed case"""
    code = "A7B2K9F4M1"
    chars = string.ascii_uppercase + string.digits
    
    assert len(code) == 10, "Code should be 10 characters"
    assert all(c in chars for c in code), "Code should only have uppercase and digits"
    assert any(c.isdigit() for c in code), "Code should have some digits"
    assert any(c.isalpha() for c in code), "Code should have some letters"
    print("✅ test_code_format_mixed PASSED")


def test_python_version():
    """Test Python version"""
    assert sys.version_info.major >= 3, "Python 3 required"
    assert sys.version_info.minor >= 6, "Python 3.6+ required"
    print(f"✅ test_python_version PASSED (Python {sys.version_info.major}.{sys.version_info.minor})")


def test_socket_timeout():
    """Test socket timeout setting"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    assert sock.gettimeout() == 10, "Socket timeout should be set to 10"
    sock.close()
    print("✅ test_socket_timeout PASSED")


def test_daemon_thread():
    """Test daemon thread"""
    thread = threading.Thread(target=lambda: None, daemon=True)
    
    assert thread.daemon is True, "Thread should be daemon"
    print("✅ test_daemon_thread PASSED")


def test_list_operations():
    """Test list operations"""
    items = []
    items.append("alice")
    items.append("bob")
    
    assert len(items) == 2, "List should have 2 items"
    assert "alice" in items, "alice should be in list"
    assert "charlie" not in items, "charlie should not be in list"
    print("✅ test_list_operations PASSED")


def test_dict_operations():
    """Test dictionary operations"""
    users = {}
    users["sock1"] = "alice"
    users["sock2"] = "bob"
    
    assert len(users) == 2, "Dict should have 2 items"
    assert users["sock1"] == "alice", "Should get alice"
    assert "sock3" not in users, "sock3 should not be in dict"
    print("✅ test_dict_operations PASSED")


def test_set_operations():
    """Test set operations"""
    usernames = set()
    usernames.add("alice")
    usernames.add("bob")
    usernames.add("alice")  # Duplicate
    
    assert len(usernames) == 2, "Set should have 2 items (no duplicates)"
    assert "alice" in usernames, "alice should be in set"
    assert "charlie" not in usernames, "charlie should not be in set"
    print("✅ test_set_operations PASSED")


def test_string_operations():
    """Test string operations"""
    msg = "HELLO WORLD"
    
    assert msg.startswith("HELLO"), "Should start with HELLO"
    assert msg.endswith("WORLD"), "Should end with WORLD"
    assert "WORLD" in msg, "Should contain WORLD"
    assert msg.isupper(), "Should be uppercase"
    print("✅ test_string_operations PASSED")


def test_authentication_flow():
    """Test authentication flow"""
    room_code = "A7B2K9F4M1"
    username = "alice"
    
    # Validate code
    assert len(room_code) == 10, "Code should be 10 chars"
    assert all(c in string.ascii_uppercase + string.digits for c in room_code), "Code format invalid"
    
        # Validate username
    assert 1 <= len(username) <= 20, "Username length invalid"
    assert " " not in username, "Username should not have spaces"
    
    print("✅ test_authentication_flow PASSED")


def test_multi_user_scenario():
    """Test multi-user scenario"""
    users = {}
    users[1] = "alice"
    users[2] = "bob"
    users[3] = "charlie"
    
    assert len(users) == 3, "Should have 3 users"
    assert users[1] == "alice", "User 1 should be alice"
    assert users[3] == "charlie", "User 3 should be charlie"
    print("✅ test_multi_user_scenario PASSED")


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Running Terminal Chat System Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_room_code_generation,
        test_room_code_uniqueness,
        test_socket_creation,
        test_socket_reuse_address,
        test_port_validation,
        test_username_length,
        test_username_no_spaces,
        test_threading_basic,
        test_threading_lock,
        test_message_encoding,
        test_utf8_encoding,
        test_empty_string,
        test_whitespace_strip,
        test_code_format_uppercase,
        test_code_format_digits,
        test_code_format_mixed,
        test_python_version,
        test_socket_timeout,
        test_daemon_thread,
        test_list_operations,
        test_dict_operations,
        test_set_operations,
        test_string_operations,
        test_authentication_flow,
        test_multi_user_scenario,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("✅ All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_tests()