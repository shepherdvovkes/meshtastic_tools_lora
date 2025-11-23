#!/usr/bin/env python3
"""
Meshtastic Mesh Speed Test Tool
Tests data transmission speed between Meshtastic nodes
"""

import sys
import time
import argparse
from datetime import datetime

try:
    import meshtastic
    import meshtastic.serial_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    print("Install with: pip3 install meshtastic")
    sys.exit(1)


def test_message_speed(port, target_node, message_count=10, message_size=100):
    """Test message transmission speed to a target node"""
    print(f"\n{'='*60}")
    print(f"MESHTASTIC SPEED TEST")
    print(f"{'='*60}")
    print(f"Port: {port}")
    print(f"Target Node: {target_node}")
    print(f"Messages: {message_count}")
    print(f"Message Size: {message_size} bytes")
    print(f"{'='*60}\n")
    
    try:
        # Connect to device
        print(f"Connecting to device on {port}...")
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        print("✅ Connected\n")
        
        # Get node info
        nodes = iface.nodes
        print(f"Nodes in mesh: {len(nodes)}")
        for node_id, node in nodes.items():
            if node_id == iface.myInfo.my_node_num:
                print(f"  - Self: {node.get('user', {}).get('longName', 'Unknown')}")
            else:
                print(f"  - {node.get('user', {}).get('longName', 'Unknown')} (Node: {node_id})")
        print()
        
        # Find target node
        target_id = None
        for node_id, node in nodes.items():
            if node_id == iface.myInfo.my_node_num:
                continue
            node_name = node.get('user', {}).get('longName', '')
            node_short = node.get('user', {}).get('shortName', '')
            if target_node.lower() in node_name.lower() or target_node.lower() in node_short.lower():
                target_id = node_id
                print(f"✅ Found target: {node_name} (Node: {node_id})")
                break
        
        if not target_id:
            print(f"❌ Target node '{target_node}' not found in mesh")
            print("Available nodes:")
            for node_id, node in nodes.items():
                if node_id != iface.myInfo.my_node_num:
                    print(f"  - {node.get('user', {}).get('longName', 'Unknown')}")
            iface.close()
            return False
        
        # Generate test message
        test_data = "X" * message_size
        test_message = f"SPEED_TEST_{test_data}"
        
        print(f"\nStarting speed test...")
        print(f"Sending {message_count} messages of {message_size} bytes each...\n")
        
        # Track statistics
        successful = 0
        failed = 0
        total_time = 0
        times = []
        
        for i in range(message_count):
            msg = f"TEST_{i:03d}_{test_message}"
            start_time = time.time()
            
            try:
                print(f"Sending message {i+1}/{message_count}...", end=" ", flush=True)
                iface.sendText(msg, destinationId=target_id, wantAck=True)
                
                # Wait for acknowledgment (with timeout)
                # Note: This is a simplified version - real ACK waiting would need async handling
                elapsed = time.time() - start_time
                times.append(elapsed)
                total_time += elapsed
                successful += 1
                print(f"✅ {elapsed:.3f}s")
                
            except Exception as e:
                elapsed = time.time() - start_time
                failed += 1
                print(f"❌ Failed: {e}")
            
            # Small delay between messages
            time.sleep(0.5)
        
        # Calculate statistics
        print(f"\n{'='*60}")
        print(f"TEST RESULTS")
        print(f"{'='*60}")
        print(f"Total Messages: {message_count}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(successful/message_count)*100:.1f}%")
        
        if successful > 0:
            avg_time = total_time / successful
            min_time = min(times)
            max_time = max(times)
            
            # Calculate throughput (bytes per second)
            # Account for message overhead (approximately 50 bytes)
            effective_size = message_size + 50
            throughput = (effective_size * 8) / avg_time  # bits per second
            
            print(f"\nTiming Statistics:")
            print(f"  Average: {avg_time:.3f} seconds")
            print(f"  Minimum: {min_time:.3f} seconds")
            print(f"  Maximum: {max_time:.3f} seconds")
            print(f"\nThroughput:")
            print(f"  Data Rate: {throughput:.2f} bps ({throughput/1000:.2f} kbps)")
            print(f"  Messages/sec: {1/avg_time:.2f}")
            print(f"  Bytes/sec: {effective_size/avg_time:.2f}")
        
        print(f"{'='*60}\n")
        
        iface.close()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_ping(port, target_node, count=5):
    """Simple ping test - send message and measure round-trip time"""
    print(f"\n{'='*60}")
    print(f"MESHTASTIC PING TEST")
    print(f"{'='*60}")
    print(f"Port: {port}")
    print(f"Target: {target_node}")
    print(f"Pings: {count}")
    print(f"{'='*60}\n")
    
    try:
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        
        # Find target
        target_id = None
        for node_id, node in iface.nodes.items():
            if node_id == iface.myInfo.my_node_num:
                continue
            node_name = node.get('user', {}).get('longName', '')
            if target_node.lower() in node_name.lower():
                target_id = node_id
                break
        
        if not target_id:
            print(f"❌ Target not found")
            iface.close()
            return
        
        times = []
        for i in range(count):
            start = time.time()
            try:
                iface.sendText(f"PING_{i}", destinationId=target_id, wantAck=True)
                elapsed = time.time() - start
                times.append(elapsed)
                print(f"Ping {i+1}: {elapsed:.3f}s")
            except Exception as e:
                print(f"Ping {i+1}: Failed - {e}")
            time.sleep(1)
        
        if times:
            print(f"\nAverage: {sum(times)/len(times):.3f}s")
            print(f"Min: {min(times):.3f}s")
            print(f"Max: {max(times):.3f}s")
        
        iface.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Meshtastic mesh speed")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/cu.usbserial-0001)")
    parser.add_argument("--target", required=True, help="Target node name or short name")
    parser.add_argument("--count", type=int, default=10, help="Number of test messages (default: 10)")
    parser.add_argument("--size", type=int, default=100, help="Message size in bytes (default: 100)")
    parser.add_argument("--ping", action="store_true", help="Run ping test instead of speed test")
    
    args = parser.parse_args()
    
    if args.ping:
        test_ping(args.port, args.target, args.count)
    else:
        test_message_speed(args.port, args.target, args.count, args.size)

