# Meshtastic LoRa Speed Test Tools

Tools for testing and analyzing transmission speed between Meshtastic devices over LoRa radio channels.

## Configuration

- **Region:** UA_433 (433 MHz - Ukraine)
- **Modem Preset:** SHORT_FAST
- **TX Power:** 10 dBm
- **Channel:** 0 (PRIMARY)

## Speed Test Results

### Device Pair Tests (30 messages per pair)

| From | To | Success Rate | Avg Time | Min Time | Max Time | Throughput | SNR | Status |
|------|-----|--------------|----------|----------|----------|------------|-----|--------|
| Unknown (7284) | 7284 | 30/30 (100%) | 104.2 ms | 101.0 ms | 106.1 ms | 9.65 kbps | N/A | ✅ Excellent |
| Unknown (7284) | 666c | 30/30 (100%) | 104.4 ms | 100.3 ms | 108.1 ms | 9.61 kbps | 11.50 dB | ✅ Excellent |

### Summary Statistics

- **Total Tests:** 2
- **Successful Tests:** 2 (100%)
- **Average Throughput:** 9.63 kbps
- **Average Latency:** 104.3 ms
- **Messages per Second:** ~9.6

### Performance Characteristics

- **Consistent Performance:** All tests show very low variance in latency
- **High Reliability:** 100% success rate across all device pairs
- **Stable Throughput:** ~9.6-9.7 kbps consistently achieved

## 3-Minute Transmission Capacity

Based on measured performance:

- **Measured Performance:** 0.246 MB (252 KB)
- **Message Rate Limit:** 0.312 MB (319 KB)
- **Practical Recommendation:** 0.185 MB (189 KB) - Safe capacity

## Available Tools

### Speed Testing

- **`test_all_device_pairs.py`** - Test speed between all device pairs
  ```bash
  python3 test_all_device_pairs.py --count 30 --json results.json
  ```

- **`test_two_devices.py`** - Automatically detect and test two USB serial devices
  ```bash
  python3 test_two_devices.py
  ```

- **`test_mesh_speed.py`** - Test speed to a specific target node
  ```bash
  python3 test_mesh_speed.py --port /dev/cu.usbserial-0001 --target 666c --count 30
  ```

### Device Discovery

- **`list_connected_nodes.py`** - List all connected devices and their nodes
  ```bash
  python3 list_connected_nodes.py
  ```

### Analysis Tools

- **`calculate_3min_capacity.py`** - Calculate 3-minute transmission capacity
- **`generate_speed_table_html.py`** - Generate HTML report with speed table

## Test Results Files

- `results.json` - Latest speed test results (JSON format)
- `all_device_pairs_results.json` - All device pair test results
- `speed_test_results.txt` - Detailed text report
- `3min_transmission_capacity.txt` - Capacity analysis
- `mesh_speed_table.html` - HTML visualization

## Requirements

- Python 3.x
- `meshtastic` Python package
  ```bash
  pip3 install meshtastic
  ```

## Hardware

- **Device Models:** HELTEC_V3
- **Frequency Band:** 433 MHz (UA_433)
- **Antennas:** 400-450 MHz compatible

## Notes

- Tests measure LoRa radio channel performance, not USB serial speed
- All tests use 30 messages per device pair for statistical reliability
- Message size: ~200 bytes payload + ~50 bytes overhead = ~250 bytes total
- Tests include acknowledgment waiting time

