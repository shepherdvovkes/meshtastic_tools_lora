#!/usr/bin/env python3
"""
Monitor message delivery to 666c
Listens for incoming messages and displays routing information
"""
import sys
import time
import signal

try:
    import meshtastic
    import meshtastic.tcp_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    sys.exit(1)

# Global flag for graceful shutdown
running = True

def signal_handler(sig, frame):
    global running
    print("\n\nStopping message monitor...")
    running = False

def on_receive(packet, interface):
    """Callback for received messages"""
    if packet.get('decoded'):
        decoded = packet['decoded']
        if decoded.get('portnum') == 'TEXT_MESSAGE_APP':
            text = decoded.get('text', '')
            sender = packet.get('from')
            sender_id = packet.get('fromId', 'Unknown')
            
            # Get sender name
            sender_name = "Unknown"
            if sender in interface.nodes:
                sender_name = interface.nodes[sender].get('user', {}).get('longName', 'Unknown')
            
            print(f"\n{'='*70}")
            print(f"📨 MESSAGE RECEIVED on 666c")
            print(f"{'='*70}")
            print(f"From: {sender_name} ({sender_id})")
            print(f"Message: {text}")
            print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*70}\n")

def monitor_messages(ip_address, duration=60):
    """Monitor messages on a node"""
    print("="*70)
    print(f"MONITORING MESSAGE DELIVERY ON 666c")
    print(f"IP: {ip_address}")
    print(f"Duration: {duration} seconds (or until Ctrl+C)")
    print("="*70)
    print()
    print("Waiting for messages...")
    print("(Send messages from 7284 to test routing)")
    print()
    
    try:
        iface = meshtastic.tcp_interface.TCPInterface(hostname=ip_address)
        time.sleep(1)
        
        # Register callback for received messages
        iface.subscribe(on_receive)
        
        # Get node info
        local_node = iface.myInfo.my_node_num
        print(f"✅ Connected to 666c (Node ID: {local_node})")
        print(f"✅ Listening for incoming messages...\n")
        
        # Monitor for specified duration
        start_time = time.time()
        while running and (time.time() - start_time) < duration:
            time.sleep(0.5)
        
        iface.close()
        print("\n✅ Monitoring stopped")
        
    except KeyboardInterrupt:
        print("\n\nMonitoring interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    
    # Monitor on 666c
    monitor_messages("192.168.0.11", duration=120)

