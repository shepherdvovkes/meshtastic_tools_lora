#!/bin/bash
#
# Send message from 7284 to 666c and monitor delivery
#

echo "=========================================="
echo "MESSAGE DELIVERY TEST"
echo "=========================================="
echo ""
echo "This will:"
echo "  1. Start monitoring on 666c (background)"
echo "  2. Send test message from 7284"
echo "  3. Display received message on 666c"
echo ""

# Start monitoring in background
echo "Starting message monitor on 666c..."
python3 monitor_message_delivery.py &
MONITOR_PID=$!

# Wait a moment for monitor to start
sleep 3

# Send test message
echo "Sending test message from 7284 to 666c..."
python3 -m meshtastic --host 192.168.0.10 --sendtext "Delivery test: 7284->bb14->666c $(date +%H:%M:%S)" --dest !9ee8666c 2>&1 | grep -v "DeprecationWarning"
echo "✅ Message sent"
echo ""

# Wait for message to arrive
echo "Waiting for message delivery (10 seconds)..."
sleep 10

# Stop monitor
echo "Stopping monitor..."
kill $MONITOR_PID 2>/dev/null
wait $MONITOR_PID 2>/dev/null

echo ""
echo "=========================================="
echo "Test complete"
echo "=========================================="

