#!/usr/bin/env python3
"""
Quick accessibility check for all three nodes
"""
import socket
import glob
import sys

def check_tcp_port(host, port=4403, timeout=2):
    """Quick TCP port check"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def find_bb14_port():
    """Find bb14 USB port"""
    ports = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.usbmodem*")
    return ports[0] if ports else None

print("="*70)
print("QUICK NODE ACCESSIBILITY CHECK")
print("="*70)
print()

# Check bb14 (USB)
print("1. bb14 (USB Serial):")
bb14_port = find_bb14_port()
if bb14_port:
    print(f"   ✅ USB device found: {bb14_port}")
else:
    print(f"   ❌ No USB device found")
print()

# Check 7284 (TCP)
print("2. 7284 (TCP/IP at 192.168.0.10):")
if check_tcp_port("192.168.0.10", 4403):
    print(f"   ✅ Port 4403 is open")
else:
    print(f"   ❌ Port 4403 is not accessible")
print()

# Check 666c (TCP)
print("3. 666c (TCP/IP at 192.168.0.11):")
if check_tcp_port("192.168.0.11", 4403):
    print(f"   ✅ Port 4403 is open")
else:
    print(f"   ❌ Port 4403 is not accessible")
print()

print("="*70)
print("Note: Port accessibility does not guarantee Meshtastic connection.")
print("Use configuration scripts to verify full connectivity.")
print("="*70)

