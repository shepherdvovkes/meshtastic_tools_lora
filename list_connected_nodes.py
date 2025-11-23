#!/usr/bin/env python3
"""
List all connected Meshtastic devices and their available nodes
"""

import sys
import glob

try:
    import meshtastic
    import meshtastic.serial_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    print("Install with: pip3 install meshtastic")
    sys.exit(1)


def get_device_info(port):
    """Get device information and available nodes"""
    try:
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        
        # Get device name safely
        device_id = iface.myInfo.my_node_num
        device_name = "Unknown"
        device_short = "Unknown"
        
        # Try to get name from nodes list (device appears as favorite)
        for node_id, node in iface.nodes.items():
            if node_id == device_id:
                user_info = node.get('user', {})
                device_name = user_info.get('longName', 'Unknown')
                device_short = user_info.get('shortName', 'Unknown')
                break
        
        # Fallback to myInfo if available
        if device_name == "Unknown":
            try:
                if hasattr(iface.myInfo, 'long_name') and iface.myInfo.long_name:
                    device_name = iface.myInfo.long_name
            except:
                pass
        
        if device_short == "Unknown":
            try:
                if hasattr(iface.myInfo, 'short_name') and iface.myInfo.short_name:
                    device_short = iface.myInfo.short_name
            except:
                pass
        
        # Get available nodes
        nodes = {}
        for node_id, node in iface.nodes.items():
            if node_id == iface.myInfo.my_node_num:
                continue
            node_name = node.get('user', {}).get('longName', 'Unknown')
            node_short = node.get('user', {}).get('shortName', 'Unknown')
            nodes[node_id] = {
                'name': node_name,
                'short': node_short,
                'snr': node.get('snr'),
                'deviceMetrics': node.get('deviceMetrics', {})
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
        print(f"❌ Error connecting to {port}: {e}")
        return None


if __name__ == "__main__":
    # Auto-detect USB serial ports
    ports = glob.glob("/dev/cu.usbserial*")
    if not ports:
        ports = glob.glob("/dev/cu.usbmodem*")
    
    if not ports:
        print("ERROR: No USB serial ports found")
        sys.exit(1)
    
    print("="*70)
    print("CONNECTED MESHTASTIC DEVICES AND NODES")
    print("="*70)
    print()
    
    for port in ports:
        info = get_device_info(port)
        if info:
            print(f"📡 Device on {port}:")
            print(f"   Name: {info['name']} ({info['short']})")
            print(f"   Node ID: {info['id']}")
            print(f"   Connected nodes ({len(info['nodes'])}):")
            
            if info['nodes']:
                for node_id, node in info['nodes'].items():
                    snr_str = f", SNR: {node['snr']:.2f} dB" if node['snr'] is not None else ""
                    print(f"      • {node['name']} ({node['short']}) - ID: {node_id}{snr_str}")
            else:
                print("      (No other nodes visible)")
            print()
        else:
            print(f"❌ {port}: Failed to connect")
            print()
    
    print("="*70)

