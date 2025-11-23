#!/bin/bash
#
# Configuration script for bb14 (REPEATER node)
# This node will relay messages between 666c and 7284
#
# Usage: ./configure_bb14_repeater.sh [USB_PORT]
#   If USB_PORT is not provided, script will try to find bb14 automatically

set -e

# Find bb14 port if not provided
if [ -z "$1" ]; then
    echo "Finding bb14 device..."
    PORT=$(python3 ../find_device_port.py bb14 2>/dev/null || echo "")
    
    if [ -z "$PORT" ]; then
        echo "❌ Error: Could not find bb14 device"
        echo "Please provide USB port manually: $0 /dev/cu.usbserial-XXXX"
        exit 1
    fi
else
    PORT="$1"
fi

echo "=========================================="
echo "Configuring bb14 as REPEATER"
echo "Port: $PORT"
echo "=========================================="
echo ""

# Verify connection
echo "1. Verifying connection to bb14..."
python3 -m meshtastic --port "$PORT" --info | grep -E "Owner|bb14" || {
    echo "❌ Error: Could not connect to bb14 on $PORT"
    exit 1
}
echo "✅ Connected"
echo ""

# Set REPEATER role
echo "2. Setting device role to REPEATER..."
python3 -m meshtastic --port "$PORT" --set device.role REPEATER
echo "✅ Role set to REPEATER"
echo ""

# Set rebroadcast mode to ALL (REPEATER always rebroadcasts, but this ensures it)
echo "3. Setting rebroadcast mode to ALL..."
python3 -m meshtastic --port "$PORT" --set device.rebroadcast_mode ALL
echo "✅ Rebroadcast mode set to ALL"
echo ""

# Set LoRa region to UA_433 (433 MHz - Ukraine)
echo "4. Setting LoRa region to UA_433..."
python3 -m meshtastic --port "$PORT" --set lora.region UA_433
echo "✅ Region set to UA_433"
echo ""

# Set modem preset to SHORT_FAST (fastest data speed)
echo "5. Setting modem preset to SHORT_FAST..."
python3 -m meshtastic --port "$PORT" --set lora.modem_preset SHORT_FAST
echo "✅ Modem preset set to SHORT_FAST"
echo ""

# Set hop limit (default is 3, but ensure it's set)
echo "6. Setting hop limit to 3..."
python3 -m meshtastic --port "$PORT" --set lora.hop_limit 3
echo "✅ Hop limit set to 3"
echo ""

# Ensure TX is enabled
echo "7. Ensuring TX is enabled..."
python3 -m meshtastic --port "$PORT" --set lora.tx_enabled true
echo "✅ TX enabled"
echo ""

# Get PRIMARY channel URL for sharing with clients
echo "8. Getting PRIMARY channel URL..."
CHANNEL_URL=$(python3 -m meshtastic --port "$PORT" --info | grep "Primary channel URL" | cut -d: -f2- | xargs)
echo "✅ PRIMARY channel URL: $CHANNEL_URL"
echo ""

# Save channel URL to file for clients
echo "$CHANNEL_URL" > primary_channel_url.txt
echo "✅ Channel URL saved to primary_channel_url.txt"
echo ""

echo "=========================================="
echo "✅ bb14 REPEATER configuration complete!"
echo "=========================================="
echo ""
echo "Configuration summary:"
echo "  Role: REPEATER"
echo "  Rebroadcast Mode: ALL"
echo "  Region: UA_433 (433 MHz)"
echo "  Modem Preset: SHORT_FAST"
echo "  Hop Limit: 3"
echo "  PRIMARY Channel URL: $CHANNEL_URL"
echo ""
echo "Next steps:"
echo "  1. Configure 666c client: ./configure_666c_client.sh"
echo "  2. Configure 7284 client: ./configure_7284_client.sh"
echo "  3. Share the PRIMARY channel URL with both clients"
echo ""

