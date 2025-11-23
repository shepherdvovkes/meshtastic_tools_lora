#!/usr/bin/env python3
"""
Meshtastic All-Device-Pairs Speed Test
Tests transmission speed from each device to every other device
"""

import sys
import time
import json
import argparse
from datetime import datetime
from collections import defaultdict

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


def test_transmission(port, target_node_id, message_count=30):
    """Test transmission speed to a target node"""
    results = {
        'port': port,
        'target_id': target_node_id,
        'message_count': message_count,
        'successful': 0,
        'failed': 0,
        'total_time': 0,
        'times': [],
        'avg_time': 0,
        'min_time': 0,
        'max_time': 0,
        'throughput_bps': 0,
        'throughput_kbps': 0,
        'messages_per_sec': 0,
        'snr': None,
        'errors': []
    }
    
    try:
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        
        # Generate test message (~200 bytes)
        test_message = "X" * 200
        
        start_time = time.time()
        times = []
        
        for i in range(message_count):
            msg = f"TEST_{i:03d}_{test_message}"
            msg_start = time.time()
            
            try:
                iface.sendText(msg, destinationId=target_node_id, wantAck=True)
                elapsed = time.time() - msg_start
                times.append(elapsed)
                results['successful'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Message {i+1}: {str(e)}")
            
            # Small delay between messages
            time.sleep(0.1)
        
        end_time = time.time()
        results['total_time'] = end_time - start_time
        
        if times:
            results['times'] = times
            results['avg_time'] = sum(times) / len(times)
            results['min_time'] = min(times)
            results['max_time'] = max(times)
            
            # Calculate throughput (accounting for ~250 bytes per message with overhead)
            bytes_per_message = 250
            total_bytes = results['successful'] * bytes_per_message
            results['throughput_bps'] = (total_bytes * 8) / results['total_time'] if results['total_time'] > 0 else 0
            results['throughput_kbps'] = results['throughput_bps'] / 1000
            results['messages_per_sec'] = results['successful'] / results['total_time'] if results['total_time'] > 0 else 0
        
        # Get SNR if available
        for node_id, node in iface.nodes.items():
            if node_id == target_node_id:
                if 'snr' in node:
                    results['snr'] = node['snr']
                break
        
        iface.close()
        return results
        
    except Exception as e:
        results['errors'].append(str(e))
        return results


def discover_devices(ports):
    """Discover all devices and their connections"""
    devices = {}
    
    print("Discovering devices...")
    print("="*70)
    
    for port in ports:
        info = get_device_info(port)
        if info:
            devices[port] = info
            print(f"✅ {port}: {info['name']} ({info['short']})")
            print(f"   Available nodes: {len(info['nodes'])}")
            for node_id, node in info['nodes'].items():
                print(f"      - {node['name']} ({node['short']})")
        else:
            print(f"❌ {port}: Failed to connect")
        print()
    
    return devices


def run_all_tests(devices, message_count=30):
    """Run tests for all device pairs"""
    all_results = []
    
    print("="*70)
    print(f"RUNNING ALL DEVICE PAIR TESTS ({message_count} messages per pair)")
    print("="*70)
    print()
    
    total_tests = sum(len(dev['nodes']) for dev in devices.values())
    current_test = 0
    
    for from_port, from_device in devices.items():
        from_name = from_device['short']
        print(f"📡 Testing from: {from_device['name']} ({from_name})")
        
        for target_id, target_node in from_device['nodes'].items():
            current_test += 1
            target_name = target_node['short']
            print(f"   → To: {target_node['name']} ({target_name}) [{current_test}/{total_tests}]... ", end="", flush=True)
            
            result = test_transmission(from_port, target_id, message_count)
            
            # Add metadata
            result['from_name'] = from_name
            result['from_full_name'] = from_device['name']
            result['to_name'] = target_name
            result['to_full_name'] = target_node['name']
            
            all_results.append(result)
            
            if result['successful'] > 0:
                print(f"✅ {result['throughput_kbps']:.2f} kbps ({result['successful']}/{message_count} success)")
            else:
                print(f"❌ Failed")
        
        print()
    
    return all_results


def print_table(results):
    """Print results in a formatted table"""
    print("\n" + "="*100)
    print("TRANSMISSION SPEED TEST RESULTS")
    print("="*100)
    print()
    
    # Table header
    print(f"{'From':<15} {'To':<15} {'Success':<10} {'Avg Time':<12} {'Throughput':<15} {'SNR':<10} {'Status':<10}")
    print("-" * 100)
    
    for result in results:
        from_name = result['from_name'][:14]
        to_name = result['to_name'][:14]
        success = f"{result['successful']}/{result['message_count']}"
        avg_time = f"{result['avg_time']*1000:.1f}ms" if result['avg_time'] > 0 else "N/A"
        throughput = f"{result['throughput_kbps']:.2f} kbps" if result['throughput_kbps'] > 0 else "N/A"
        snr = f"{result['snr']:.2f} dB" if result['snr'] is not None else "N/A"
        
        # Status
        success_rate = (result['successful'] / result['message_count']) * 100 if result['message_count'] > 0 else 0
        if success_rate >= 95:
            status = "✅ Excellent"
        elif success_rate >= 80:
            status = "⚠️  Good"
        else:
            status = "❌ Poor"
        
        print(f"{from_name:<15} {to_name:<15} {success:<10} {avg_time:<12} {throughput:<15} {snr:<10} {status:<10}")
    
    print("-" * 100)
    print()


def print_summary_table(results):
    """Print a summary matrix table"""
    print("\n" + "="*100)
    print("TRANSMISSION SPEED MATRIX (kbps)")
    print("="*100)
    print()
    
    # Get unique device names
    devices = set()
    for result in results:
        devices.add(result['from_name'])
        devices.add(result['to_name'])
    
    devices = sorted(list(devices))
    
    # Create matrix
    matrix = {}
    for result in results:
        key = (result['from_name'], result['to_name'])
        matrix[key] = result['throughput_kbps']
    
    # Print header
    print(f"{'From \\ To':<15}", end="")
    for to_dev in devices:
        print(f"{to_dev[:12]:<13}", end="")
    print()
    print("-" * (15 + len(devices) * 13))
    
    # Print rows
    for from_dev in devices:
        print(f"{from_dev[:14]:<15}", end="")
        for to_dev in devices:
            if from_dev == to_dev:
                print(f"{'---':<13}", end="")
            else:
                key = (from_dev, to_dev)
                if key in matrix:
                    value = matrix[key]
                    print(f"{value:>6.2f} kbps  ", end="")
                else:
                    print(f"{'N/A':<13}", end="")
        print()
    
    print()


def save_json(results, filename):
    """Save results to JSON file"""
    with open(filename, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f, indent=2)
    print(f"Results saved to: {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test transmission speed between all device pairs")
    parser.add_argument("--ports", nargs="+", help="Serial ports to test (e.g., /dev/cu.usbserial-0001 /dev/cu.usbserial-4)")
    parser.add_argument("--count", type=int, default=30, help="Number of messages per test (default: 30)")
    parser.add_argument("--json", help="Save results to JSON file")
    
    args = parser.parse_args()
    
    # Default ports if not specified
    if not args.ports:
        # Try to auto-detect
        import glob
        ports = glob.glob("/dev/cu.usbserial*")
        if not ports:
            ports = glob.glob("/dev/cu.usbmodem*")
        if not ports:
            print("ERROR: No USB serial ports found. Please specify with --ports")
            sys.exit(1)
    else:
        ports = args.ports
    
    print("="*70)
    print("MESHTASTIC ALL-DEVICE-PAIRS SPEED TEST")
    print("="*70)
    print(f"Ports: {', '.join(ports)}")
    print(f"Messages per pair: {args.count}")
    print()
    
    # Discover devices
    devices = discover_devices(ports)
    
    if not devices:
        print("ERROR: No devices found")
        sys.exit(1)
    
    # Run all tests
    results = run_all_tests(devices, args.count)
    
    # Print results
    print_table(results)
    print_summary_table(results)
    
    # Calculate statistics
    if results:
        total_tests = len(results)
        successful_tests = len([r for r in results if r['successful'] > 0])
        avg_throughput = sum(r['throughput_kbps'] for r in results if r['throughput_kbps'] > 0) / successful_tests if successful_tests > 0 else 0
        
        print("="*100)
        print("SUMMARY STATISTICS")
        print("="*100)
        print(f"Total tests: {total_tests}")
        print(f"Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        print(f"Average throughput: {avg_throughput:.2f} kbps")
        print()
    
    # Save to JSON if requested
    if args.json:
        save_json(results, args.json)

