#!/usr/bin/env python3
"""
Meshtastic File Transfer Speed Test
Tests 1MB file transmission between nodes and measures throughput
"""

import sys
import time
import argparse
import json
from datetime import datetime

try:
    import meshtastic
    import meshtastic.serial_interface
except ImportError:
    print("ERROR: meshtastic module not found")
    print("Install with: pip3 install meshtastic")
    sys.exit(1)


def generate_test_data(size_bytes):
    """Generate test data of specified size"""
    # Generate data in chunks to avoid memory issues
    chunk_size = 200  # Max message size is ~240 bytes, use 200 for safety
    chunks = []
    total = 0
    size_bytes = int(size_bytes)  # Ensure it's an integer
    
    while total < size_bytes:
        remaining = size_bytes - total
        current_chunk_size = min(chunk_size, int(remaining))
        chunk = "X" * current_chunk_size
        chunks.append(chunk)
        total += current_chunk_size
    
    return chunks


def test_file_transfer(port, target_node, file_size_mb=1):
    """Test file transfer speed to a target node"""
    file_size_bytes = file_size_mb * 1024 * 1024
    
    print(f"\n{'='*70}")
    print(f"MESHTASTIC FILE TRANSFER TEST")
    print(f"{'='*70}")
    print(f"Port: {port}")
    print(f"Target Node: {target_node}")
    print(f"File Size: {file_size_mb} MB ({file_size_bytes:,} bytes)")
    print(f"{'='*70}\n")
    
    results = {
        "port": port,
        "target_node": target_node,
        "file_size_mb": file_size_mb,
        "file_size_bytes": file_size_bytes,
        "start_time": None,
        "end_time": None,
        "total_time": None,
        "messages_sent": 0,
        "messages_successful": 0,
        "messages_failed": 0,
        "throughput_bps": 0,
        "throughput_kbps": 0,
        "throughput_mbps": 0,
        "messages_per_second": 0,
        "bytes_per_second": 0,
        "snr": None,
        "rssi": None,
        "channel_utilization": None,
        "air_util_tx": None,
        "errors": []
    }
    
    try:
        # Connect to device
        print(f"Connecting to device on {port}...")
        iface = meshtastic.serial_interface.SerialInterface(devPath=port)
        print("✅ Connected\n")
        
        # Get node info
        nodes = iface.nodes
        print(f"Nodes in mesh: {len(nodes)}")
        
        # Find target node
        target_id = None
        target_name = None
        for node_id, node in nodes.items():
            if node_id == iface.myInfo.my_node_num:
                continue
            node_name = node.get('user', {}).get('longName', '')
            node_short = node.get('user', {}).get('shortName', '')
            if target_node.lower() in node_name.lower() or target_node.lower() in node_short.lower():
                target_id = node_id
                target_name = node_name
                print(f"✅ Found target: {node_name} (Node: {node_id})")
                
                # Get signal quality metrics
                if 'snr' in node:
                    results['snr'] = node['snr']
                    print(f"   SNR: {node['snr']:.2f} dB")
                
                if 'deviceMetrics' in node:
                    metrics = node['deviceMetrics']
                    if 'channelUtilization' in metrics:
                        results['channel_utilization'] = metrics['channelUtilization']
                    if 'airUtilTx' in metrics:
                        results['air_util_tx'] = metrics['airUtilTx']
                break
        
        if not target_id:
            print(f"❌ Target node '{target_node}' not found in mesh")
            print("Available nodes:")
            for node_id, node in nodes.items():
                if node_id != iface.myInfo.my_node_num:
                    print(f"  - {node.get('user', {}).get('longName', 'Unknown')}")
            iface.close()
            return None
        
        # Generate test data
        print(f"\nGenerating test data ({file_size_mb} MB)...")
        chunks = generate_test_data(file_size_bytes)
        num_chunks = len(chunks)
        print(f"Split into {num_chunks} messages (~200 bytes each)\n")
        
        # Start transfer
        print(f"Starting file transfer...")
        print(f"{'='*70}")
        
        start_time = time.time()
        results['start_time'] = datetime.now().isoformat()
        
        successful = 0
        failed = 0
        message_times = []
        
        for i, chunk in enumerate(chunks):
            msg = f"FILE_{i:05d}_{chunk}"
            msg_start = time.time()
            
            try:
                if (i + 1) % 50 == 0 or i == 0:
                    progress = ((i + 1) / num_chunks) * 100
                    print(f"Progress: {progress:.1f}% ({i+1}/{num_chunks} messages)", end="\r", flush=True)
                
                iface.sendText(msg, destinationId=target_id, wantAck=True)
                
                elapsed = time.time() - msg_start
                message_times.append(elapsed)
                successful += 1
                
            except Exception as e:
                failed += 1
                results['errors'].append(f"Message {i+1}: {str(e)}")
                if failed <= 5:  # Only show first 5 errors
                    print(f"\n❌ Message {i+1} failed: {e}")
        
        end_time = time.time()
        results['end_time'] = datetime.now().isoformat()
        results['total_time'] = end_time - start_time
        
        print(f"\n{'='*70}")
        print(f"Transfer complete!")
        print(f"{'='*70}\n")
        
        # Calculate statistics
        results['messages_sent'] = num_chunks
        results['messages_successful'] = successful
        results['messages_failed'] = failed
        
        if successful > 0 and results['total_time'] > 0:
            # Calculate throughput
            # Account for message overhead (approximately 50 bytes per message)
            overhead_per_message = 50
            total_bytes_transferred = (file_size_bytes) + (successful * overhead_per_message)
            
            results['throughput_bps'] = (total_bytes_transferred * 8) / results['total_time']
            results['throughput_kbps'] = results['throughput_bps'] / 1000
            results['throughput_mbps'] = results['throughput_kbps'] / 1000
            results['messages_per_second'] = successful / results['total_time']
            results['bytes_per_second'] = file_size_bytes / results['total_time']
        
        # Display results
        print(f"RESULTS:")
        print(f"  Messages Sent: {results['messages_sent']}")
        print(f"  Successful: {results['messages_successful']} ({results['messages_successful']/results['messages_sent']*100:.1f}%)")
        print(f"  Failed: {results['messages_failed']}")
        print(f"  Total Time: {results['total_time']:.2f} seconds")
        print(f"  Throughput: {results['throughput_kbps']:.2f} kbps ({results['throughput_mbps']:.4f} Mbps)")
        print(f"  Messages/sec: {results['messages_per_second']:.2f}")
        print(f"  Bytes/sec: {results['bytes_per_second']:,.0f}")
        if results['snr'] is not None:
            print(f"  SNR: {results['snr']:.2f} dB")
        print()
        
        iface.close()
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        results['errors'].append(str(e))
        return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Meshtastic file transfer speed")
    parser.add_argument("--port", required=True, help="Serial port (e.g., /dev/cu.usbserial-0001)")
    parser.add_argument("--target", required=True, help="Target node name or short name")
    parser.add_argument("--size", type=float, default=1.0, help="File size in MB (default: 1.0)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    results = test_file_transfer(args.port, args.target, args.size)
    
    if args.json and results:
        print(json.dumps(results, indent=2))

