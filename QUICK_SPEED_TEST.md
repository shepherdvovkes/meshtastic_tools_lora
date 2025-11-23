# Quick Speed Test Guide

## Fastest Method: Python Script

```bash
# Test speed from Device 1 to Device 2
python3 test_mesh_speed.py --port /dev/cu.usbserial-0001 --target 7284 --count 20

# Test from Device 2 to Device 1
python3 test_mesh_speed.py --port /dev/cu.usbserial-4 --target 666c --count 20

# Simple ping test (5 pings)
python3 test_mesh_speed.py --port /dev/cu.usbserial-0001 --target 7284 --ping --count 5
```

## Built-in Stress Test

```bash
# Run stress test on device
python3 -m meshtastic --port /dev/cu.usbserial-0001 --test
```

## Check Signal Quality (SNR)

```bash
# Check SNR between devices
python3 -m meshtastic --port /dev/cu.usbserial-0001 --info | grep -E "snr|SNR"
```

## Monitor Real-time Metrics

```bash
# Check channel utilization and air utilization
python3 -m meshtastic --port /dev/cu.usbserial-0001 --info | grep -E "channelUtilization|airUtil"
```

## Expected Performance (SHORT_FAST on UA_433)

- **Theoretical max**: ~50 kbps
- **Practical**: ~10-30 kbps
- **Latency**: 100-500ms (close range)
- **Message size**: Up to ~240 bytes

## What Good Performance Looks Like

✅ Success rate > 95%  
✅ Latency < 500ms  
✅ SNR > 10 dB  
✅ Low channel utilization

