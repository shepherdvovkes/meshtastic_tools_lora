#!/bin/bash
#
# Check message routing by sending a message and monitoring nodes
#

echo "=========================================="
echo "MESSAGE ROUTING TEST: 7284 → bb14 → 666c"
echo "=========================================="
echo ""

# Send message from 7284 to 666c
echo "1. Sending message from 7284 to 666c..."
python3 -m meshtastic --host 192.168.0.10 --sendtext "Routing test: 7284->bb14->666c" --dest !9ee8666c 2>&1 | grep -v "DeprecationWarning"
echo "✅ Message sent"
echo ""

# Wait a moment
sleep 3

# Check nodes visible from each device
echo "2. Checking routing paths..."
echo ""

echo "From 7284 (192.168.0.10):"
python3 ../query_node_neighbors.py --ip 192.168.0.10 2>&1 | grep -E "REMOTE|bb14|666c" | head -5
echo ""

echo "From bb14 (192.168.0.15):"
python3 ../query_node_neighbors.py --ip 192.168.0.15 2>&1 | grep -E "REMOTE|7284|666c" | head -5
echo ""

echo "From 666c (192.168.0.11):"
python3 ../query_node_neighbors.py --ip 192.168.0.11 2>&1 | grep -E "REMOTE|7284|bb14" | head -5
echo ""

echo "=========================================="
echo "ROUTING ANALYSIS"
echo "=========================================="
echo ""
echo "Expected route: 7284 → bb14 (REPEATER) → 666c"
echo ""
echo "Note: Meshtastic uses automatic mesh routing."
echo "The REPEATER role gives bb14 higher priority in routing decisions."
echo "Even if 7284 and 666c can hear each other directly,"
echo "messages should prefer routing through bb14."
echo ""

