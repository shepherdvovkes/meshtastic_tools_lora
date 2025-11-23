#!/usr/bin/env python3
"""
Test message routing and check traceroute information
"""
import sys
import time

try:
    import meshtastic
    import meshtastic.tcp_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    sys.exit(1)

def send_message_with_trace(source_ip, dest_node_id, message_text):
    """Send message and attempt to trace routing"""
    print(f"Connecting to source node at {source_ip}...")
    iface = meshtastic.tcp_interface.TCPInterface(hostname=source_ip)
    time.sleep(1)
    
    print(f"Sending message: '{message_text}'")
    print(f"Destination: {dest_node_id}")
    print()
    
    # Send message
    iface.sendText(message_text, dest=dest_node_id, wantAck=True)
    
    print("✅ Message sent")
    print("Waiting for delivery confirmation...")
    time.sleep(3)
    
    # Check if we can see routing info in nodes
    print("\nChecking routing information...")
    nodes = iface.nodes
    print(f"Nodes visible from source: {len(nodes)}")
    
    for node_id, node in nodes.items():
        if node_id == iface.myInfo.my_node_num:
            continue
        node_name = node.get('user', {}).get('longName', 'Unknown')
        node_short = node.get('user', {}).get('shortName', 'Unknown')
        snr = node.get('snr')
        print(f"  - {node_name} ({node_short}) - ID: {node_id}", end="")
        if snr is not None:
            print(f" - SNR: {snr:.2f} dB")
        else:
            print()
    
    iface.close()
    return True

if __name__ == "__main__":
    source_ip = "192.168.0.10"  # 7284
    dest_node_id = "!9ee8666c"  # 666c
    message = "Routing test: 7284 -> bb14 -> 666c"
    
    print("="*70)
    print("MESSAGE ROUTING TEST")
    print("="*70)
    print()
    print(f"Source: 7284 ({source_ip})")
    print(f"Destination: 666c ({dest_node_id})")
    print(f"Expected route: 7284 → bb14 (REPEATER) → 666c")
    print()
    
    send_message_with_trace(source_ip, dest_node_id, message)
    
    print()
    print("="*70)
    print("Note: Meshtastic doesn't have built-in traceroute.")
    print("Check the destination node to verify message was received.")
    print("Routing is handled automatically by the mesh protocol.")
    print("="*70)

