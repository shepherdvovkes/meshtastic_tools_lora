#!/bin/bash
#
# Configuration script for 7284 (CLIENT node)
# This node will communicate only through bb14 repeater
# It will NOT see 666c directly
#
# Usage: ./configure_7284_client.sh [CHANNEL_URL]
#   If CHANNEL_URL is not provided, script will try to read from primary_channel_url.txt

set -e

IP_ADDRESS="192.168.0.10"

echo "=========================================="
echo "Configuring 7284 as CLIENT"
echo "IP: $IP_ADDRESS"
echo "=========================================="
echo ""

# Get channel URL
if [ -z "$1" ]; then
    if [ -f "primary_channel_url.txt" ]; then
        CHANNEL_URL=$(cat primary_channel_url.txt | xargs)
        echo "Using channel URL from primary_channel_url.txt"
    else
        echo "❌ Error: No channel URL provided and primary_channel_url.txt not found"
        echo "Usage: $0 [CHANNEL_URL]"
        echo "   Or: Run configure_bb14_repeater.sh first to generate primary_channel_url.txt"
        exit 1
    fi
else
    CHANNEL_URL="$1"
fi

echo "Channel URL: $CHANNEL_URL"
echo ""

# Verify connection
echo "1. Verifying connection to 7284 at $IP_ADDRESS..."
python3 -m meshtastic --host "$IP_ADDRESS" --info | grep -E "Owner|7284" || {
    echo "❌ Error: Could not connect to 7284 at $IP_ADDRESS"
    echo "   Make sure the device is connected to Wi-Fi and TCP/IP is enabled"
    exit 1
}
echo "✅ Connected"
echo ""

# Set CLIENT role
echo "2. Setting device role to CLIENT..."
python3 -m meshtastic --host "$IP_ADDRESS" --set device.role CLIENT
echo "✅ Role set to CLIENT"
echo ""

# Set rebroadcast mode to ALL (to participate in mesh routing)
echo "3. Setting rebroadcast mode to ALL..."
python3 -m meshtastic --host "$IP_ADDRESS" --set device.rebroadcast_mode ALL
echo "✅ Rebroadcast mode set to ALL"
echo ""

# Set LoRa region to UA_433 (must match repeater)
echo "4. Setting LoRa region to UA_433..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.region UA_433
echo "✅ Region set to UA_433"
echo ""

# Set modem preset to SHORT_FAST (must match repeater)
echo "5. Setting modem preset to SHORT_FAST..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.modem_preset SHORT_FAST
echo "✅ Modem preset set to SHORT_FAST"
echo ""

# Set hop limit (must match repeater)
echo "6. Setting hop limit to 3..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.hop_limit 3
echo "✅ Hop limit set to 3"
echo ""

# Ensure TX is enabled
echo "7. Ensuring TX is enabled..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.tx_enabled true
echo "✅ TX enabled"
echo ""

# Set PRIMARY channel to match repeater
echo "8. Setting PRIMARY channel to match repeater..."
python3 -m meshtastic --host "$IP_ADDRESS" --ch-set url "$CHANNEL_URL"
echo "✅ PRIMARY channel synchronized with repeater"
echo ""

# Wait a moment for configuration to apply
sleep 2

# Verify configuration
echo "9. Verifying configuration..."
echo ""
python3 -m meshtastic --host "$IP_ADDRESS" --info | grep -E "role|rebroadcast|region|modemPreset|hop" || true
echo ""

echo "=========================================="
echo "✅ 7284 CLIENT configuration complete!"
echo "=========================================="
echo ""
echo "Configuration summary:"
echo "  Role: CLIENT"
echo "  Rebroadcast Mode: ALL"
echo "  Region: UA_433 (433 MHz)"
echo "  Modem Preset: SHORT_FAST"
echo "  Hop Limit: 3"
echo "  PRIMARY Channel: Synchronized with bb14 repeater"
echo ""
echo "This node will communicate through bb14 repeater"
echo "and will NOT see 666c directly (if properly isolated)"
echo ""

