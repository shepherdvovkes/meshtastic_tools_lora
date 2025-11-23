#!/usr/bin/env python3
"""Find which USB port has a specific device"""

import sys
import glob

try:
    import meshtastic
    import meshtastic.serial_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    sys.exit(1)


def find_device_port(device_short_name):
    """Find which port has the device with given short name"""
    ports = glob.glob("/dev/cu.usbserial*")
    if not ports:
        ports = glob.glob("/dev/cu.usbmodem*")
    
    for port in ports:
        try:
            iface = meshtastic.serial_interface.SerialInterface(devPath=port)
            device_id = iface.myInfo.my_node_num
            
            # Check if this device matches
            for node_id, node in iface.nodes.items():
                if node_id == device_id:
                    user_info = node.get('user', {})
                    short_name = user_info.get('shortName', '')
                    if short_name.lower() == device_short_name.lower():
                        iface.close()
                        return port
            
            iface.close()
        except:
            continue
    
    return None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 find_device_port.py <short_name>")
        sys.exit(1)
    
    short_name = sys.argv[1]
    port = find_device_port(short_name)
    
    if port:
        print(port)
    else:
        print(f"Device {short_name} not found")
        sys.exit(1)

