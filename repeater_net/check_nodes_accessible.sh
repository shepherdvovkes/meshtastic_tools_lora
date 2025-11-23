#!/bin/bash
#
# Check if all three nodes are accessible
#

echo "=========================================="
echo "CHECKING NODE ACCESSIBILITY"
echo "=========================================="
echo ""

# Check bb14 via USB serial
echo "1. Checking bb14 (USB Serial)..."
BB14_PORT=$(python3 ../find_device_port.py bb14 2>/dev/null || echo "")

if [ -z "$BB14_PORT" ]; then
    echo "❌ bb14: NOT FOUND via USB"
    echo "   Please connect bb14 via USB cable"
    BB14_OK=0
else
    echo "✅ bb14: Found at $BB14_PORT"
    # Try to get info
    if python3 -m meshtastic --port "$BB14_PORT" --info >/dev/null 2>&1; then
        echo "✅ bb14: Connection verified"
        BB14_OK=1
    else
        echo "⚠️  bb14: Port found but connection failed"
        BB14_OK=0
    fi
fi
echo ""

# Check 7284 via TCP/IP
echo "2. Checking 7284 (TCP/IP at 192.168.0.10)..."
if timeout 3 python3 -m meshtastic --host 192.168.0.10 --info >/dev/null 2>&1; then
    echo "✅ 7284: Accessible at 192.168.0.10"
    NODE_7284_OK=1
else
    echo "❌ 7284: NOT accessible at 192.168.0.10"
    echo "   Check: Wi-Fi connection, IP address, TCP/IP enabled"
    NODE_7284_OK=0
fi
echo ""

# Check 666c via TCP/IP
echo "3. Checking 666c (TCP/IP at 192.168.0.11)..."
if timeout 3 python3 -m meshtastic --host 192.168.0.11 --info >/dev/null 2>&1; then
    echo "✅ 666c: Accessible at 192.168.0.11"
    NODE_666C_OK=1
else
    echo "❌ 666c: NOT accessible at 192.168.0.11"
    echo "   Check: Wi-Fi connection, IP address, TCP/IP enabled"
    NODE_666C_OK=0
fi
echo ""

# Summary
echo "=========================================="
echo "ACCESSIBILITY SUMMARY"
echo "=========================================="
TOTAL=$((BB14_OK + NODE_7284_OK + NODE_666C_OK))
echo "Accessible nodes: $TOTAL/3"
echo ""
if [ "$BB14_OK" -eq 1 ]; then
    echo "✅ bb14 (REPEATER) - $BB14_PORT"
else
    echo "❌ bb14 (REPEATER) - Not accessible"
fi

if [ "$NODE_7284_OK" -eq 1 ]; then
    echo "✅ 7284 (CLIENT) - 192.168.0.10"
else
    echo "❌ 7284 (CLIENT) - Not accessible"
fi

if [ "$NODE_666C_OK" -eq 1 ]; then
    echo "✅ 666c (CLIENT) - 192.168.0.11"
else
    echo "❌ 666c (CLIENT) - Not accessible"
fi
echo ""

if [ "$TOTAL" -eq 3 ]; then
    echo "✅ All nodes are accessible!"
    echo "Ready to configure the repeater network."
    exit 0
else
    echo "⚠️  Not all nodes are accessible."
    echo "Please verify connections before configuration."
    exit 1
fi

