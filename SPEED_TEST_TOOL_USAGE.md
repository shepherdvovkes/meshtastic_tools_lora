# Meshtastic All-Device-Pairs Speed Test Tool

## Overview

This tool tests transmission speed from each device to every other device in the mesh network, sending 30 messages per pair and calculating throughput.

## Usage

### Basic Usage

```bash
# Test all devices (auto-detect ports)
python3 test_all_device_pairs.py --count 30

# Test specific devices
python3 test_all_device_pairs.py --ports /dev/cu.usbserial-0001 /dev/cu.usbserial-4 --count 30

# Save results to JSON
python3 test_all_device_pairs.py --ports /dev/cu.usbserial-0001 --count 30 --json results.json
```

### Generate HTML Report

```bash
# After running tests, generate HTML table
python3 generate_speed_table_html.py all_device_pairs_results.json
```

This creates `mesh_speed_table.html` with:
- Beautiful Tailwind CSS styling
- Responsive design (works on mobile)
- Animated tables
- Speed matrix showing all device pairs
- Detailed results with SNR and success rates

## Output

The tool provides:

1. **Console Output:**
   - Real-time progress
   - Summary table with all results
   - Speed matrix showing throughput between devices
   - Statistics summary

2. **JSON File** (if `--json` specified):
   - Complete test results
   - Timestamps
   - All metrics (throughput, SNR, success rates, etc.)

3. **HTML Report:**
   - Interactive table
   - Color-coded throughput values
   - Signal quality indicators
   - Summary statistics

## Example Output

```
TRANSMISSION SPEED TEST RESULTS
====================================================================================================
From            To              Success    Avg Time     Throughput      SNR        Status    
----------------------------------------------------------------------------------------------------
7284            666c            30/30      104.5ms      9.61 kbps       11.25 dB   ✅ Excellent
7284            bb14            30/30      105.2ms      9.58 kbps       10.50 dB   ✅ Excellent
```

## Parameters

- `--ports`: List of serial ports to test (e.g., `/dev/cu.usbserial-0001`)
- `--count`: Number of messages per test pair (default: 30)
- `--json`: Output file for JSON results

## Requirements

- Python 3
- meshtastic module: `pip3 install meshtastic`
- Connected Meshtastic devices via USB

## Notes

- Each test sends 30 messages (configurable)
- Tests all device pairs (from each device to every other device)
- Measures: throughput, latency, success rate, SNR
- Results are color-coded by performance level

