#!/usr/bin/env python3
"""
Automatically detect two USB serial devices and test speed between them
"""

import sys
import time
import glob

try:
    import meshtastic
    import meshtastic.serial_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    print("Install with: pip3 install meshtastic")
    sys.exit(1)


def get_device_info(port):
    """Get device information"""
    try:
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        device_id = iface.myInfo.my_node_num
        device_name = "Unknown"
        device_short = "Unknown"
        
        # Try to get name from nodes list
        for node_id, node in iface.nodes.items():
            if node_id == device_id:
                user_info = node.get('user', {})
                device_name = user_info.get('longName', 'Unknown')
                device_short = user_info.get('shortName', 'Unknown')
                break
        
        # Get available nodes
        nodes = {}
        for node_id, node in iface.nodes.items():
            if node_id == device_id:
                continue
            node_name = node.get('user', {}).get('longName', 'Unknown')
            node_short = node.get('user', {}).get('shortName', 'Unknown')
            nodes[node_id] = {
                'name': node_name,
                'short': node_short,
                'snr': node.get('snr')
            }
        
        iface.close()
        return {
            'name': device_name,
            'short': device_short,
            'id': device_id,
            'port': port,
            'nodes': nodes
        }
    except Exception as e:
        return None


def find_target_node_id(port, target_device_id):
    """Find target node ID by matching device ID"""
    try:
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        device_id = iface.myInfo.my_node_num
        
        # Convert target device ID to hex format (like !9ee87284)
        target_hex = f"!{target_device_id:08x}"
        
        # Look for the target device ID in the nodes list
        for node_id, node in iface.nodes.items():
            if node_id == device_id:
                continue
            # Check if this node matches the target device ID
            # Node IDs are stored as strings like "!9ee87284"
            if str(node_id) == target_hex or str(node_id) == str(target_device_id):
                iface.close()
                return node_id
        
        iface.close()
        return None
    except Exception as e:
        print(f"Error in find_target_node_id: {e}")
        return None


def test_speed(port, target_node_id, message_count=30):
    """Test transmission speed to a target node"""
    try:
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        
        test_message = "X" * 200
        successful = 0
        failed = 0
        times = []
        
        for i in range(message_count):
            msg = f"TEST_{i:03d}_{test_message}"
            msg_start = time.time()
            
            try:
                iface.sendText(msg, destinationId=target_node_id, wantAck=True)
                elapsed = time.time() - msg_start
                times.append(elapsed)
                successful += 1
            except Exception as e:
                failed += 1
            
            time.sleep(0.1)
        
        iface.close()
        
        if times:
            avg_time = sum(times) / len(times)
            bytes_per_message = 250
            total_bytes = successful * bytes_per_message
            total_time = sum(times)
            throughput_bps = (total_bytes * 8) / total_time if total_time > 0 else 0
            throughput_kbps = throughput_bps / 1000
            
            return {
                'successful': successful,
                'failed': failed,
                'avg_time': avg_time,
                'min_time': min(times),
                'max_time': max(times),
                'throughput_kbps': throughput_kbps,
                'messages_per_sec': successful / total_time if total_time > 0 else 0
            }
        else:
            return {
                'successful': 0,
                'failed': failed,
                'avg_time': 0,
                'min_time': 0,
                'max_time': 0,
                'throughput_kbps': 0,
                'messages_per_sec': 0
            }
    except Exception as e:
        return {
            'successful': 0,
            'failed': message_count,
            'error': str(e)
        }


if __name__ == "__main__":
    # Auto-detect USB serial ports
    ports = glob.glob("/dev/cu.usbserial*")
    if not ports:
        ports = glob.glob("/dev/cu.usbmodem*")
    
    if len(ports) < 2:
        print("ERROR: Need at least 2 USB serial devices connected")
        print(f"Found {len(ports)} device(s)")
        sys.exit(1)
    
    print("="*70)
    print("AUTOMATIC TWO-DEVICE SPEED TEST")
    print("="*70)
    print()
    
    # Get info for all devices
    devices = []
    for port in ports[:2]:  # Use first 2 devices
        info = get_device_info(port)
        if info:
            devices.append(info)
            print(f"✅ Device on {port}:")
            print(f"   Name: {info['name']} ({info['short']})")
            print(f"   Node ID: {info['id']}")
            print()
    
    if len(devices) < 2:
        print("ERROR: Could not connect to 2 devices")
        sys.exit(1)
    
    device1 = devices[0]
    device2 = devices[1]
    
    # Get node names from connected nodes if available
    device1_name = device1['short']
    device2_name = device2['short']
    
    # Try to get better names from nodes list
    for node_id, node in device1['nodes'].items():
        if str(node_id) == str(device1['id']) or node_id == device1['id']:
            device1_name = node.get('short', device1_name)
            break
    
    for node_id, node in device2['nodes'].items():
        if str(node_id) == str(device2['id']) or node_id == device2['id']:
            device2_name = node.get('short', device2_name)
            break
    
    # Also check if device2 is visible from device1's perspective
    for node_id, node in device1['nodes'].items():
        if str(node_id) == str(device2['id']) or node_id == device2['id']:
            device2_name = node.get('short', f"Node {device2['id']}")
            break
    
    print(f"Testing from: {device1_name} (Node ID: {device1['id']})")
    print(f"         to:   {device2_name} (Node ID: {device2['id']})")
    print()
    
    # Find target node ID by matching device2's ID
    target_id = find_target_node_id(device1['port'], device2['id'])
    
    if not target_id:
        print(f"❌ Could not find target node (ID: {device2['id']}) from {device1['port']}")
        print(f"Available nodes from {device1['port']}:")
        for node_id, node in device1['nodes'].items():
            print(f"  - {node.get('name', 'Unknown')} ({node.get('short', 'Unknown')}) - ID: {node_id}")
        sys.exit(1)
    
    print(f"Starting speed test (30 messages)...")
    print("(This may take a few moments...)\n")
    
    result = test_speed(device1['port'], target_id, 30)
    
    print("="*70)
    print("TEST RESULTS")
    print("="*70)
    print(f"From: {device1_name} (Node ID: {device1['id']})")
    print(f"To:   {device2_name} (Node ID: {device2['id']})")
    print()
    print(f"Successful: {result['successful']}/30")
    print(f"Failed: {result['failed']}/30")
    
    if result['successful'] > 0:
        print(f"Average time: {result['avg_time']*1000:.1f} ms")
        print(f"Min/Max time: {result['min_time']*1000:.1f} ms / {result['max_time']*1000:.1f} ms")
        print(f"Throughput: {result['throughput_kbps']:.2f} kbps")
        print(f"Messages/sec: {result['messages_per_sec']:.2f}")
    else:
        if 'error' in result:
            print(f"Error: {result['error']}")
    
    print("="*70)

