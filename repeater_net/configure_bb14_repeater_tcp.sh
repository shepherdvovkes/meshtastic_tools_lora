#!/bin/bash
#
# Configuration script for bb14 (REPEATER node) via TCP/IP
# Uses IP address 192.168.0.15 instead of USB serial
#

set -e

IP_ADDRESS="192.168.0.15"

echo "=========================================="
echo "Configuring bb14 as REPEATER (via TCP/IP)"
echo "IP: $IP_ADDRESS"
echo "=========================================="
echo ""

# Verify connection
echo "1. Verifying connection to bb14 at $IP_ADDRESS..."
if ! timeout 5 python3 -m meshtastic --host "$IP_ADDRESS" --info 2>&1 | grep -q "bb14"; then
    echo "❌ Error: Could not connect to bb14 at $IP_ADDRESS"
    echo "   Make sure the device is connected to Wi-Fi and TCP/IP is enabled"
    exit 1
fi
echo "✅ Connected"
echo ""

# Set REPEATER role
echo "2. Setting device role to REPEATER..."
python3 -m meshtastic --host "$IP_ADDRESS" --set device.role REPEATER
echo "✅ Role set to REPEATER"
sleep 2
echo ""

# Set rebroadcast mode to ALL
echo "3. Setting rebroadcast mode to ALL..."
python3 -m meshtastic --host "$IP_ADDRESS" --set device.rebroadcast_mode ALL
echo "✅ Rebroadcast mode set to ALL"
sleep 2
echo ""

# Set LoRa region to UA_433
echo "4. Setting LoRa region to UA_433..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.region UA_433
echo "✅ Region set to UA_433"
sleep 2
echo ""

# Set modem preset to SHORT_FAST
echo "5. Setting modem preset to SHORT_FAST..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.modem_preset SHORT_FAST
echo "✅ Modem preset set to SHORT_FAST"
sleep 2
echo ""

# Set hop limit
echo "6. Setting hop limit to 3..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.hop_limit 3
echo "✅ Hop limit set to 3"
sleep 2
echo ""

# Ensure TX is enabled
echo "7. Ensuring TX is enabled..."
python3 -m meshtastic --host "$IP_ADDRESS" --set lora.tx_enabled true
echo "✅ TX enabled"
sleep 2
echo ""

# Get PRIMARY channel URL
echo "8. Getting PRIMARY channel URL..."
CHANNEL_URL=$(python3 -m meshtastic --host "$IP_ADDRESS" --info 2>/dev/null | grep "Primary channel URL" | cut -d: -f2- | xargs)

if [ -z "$CHANNEL_URL" ]; then
    echo "⚠️  Warning: Could not get channel URL"
else
    echo "✅ PRIMARY channel URL: $CHANNEL_URL"
    echo "$CHANNEL_URL" > primary_channel_url.txt
    echo "✅ Channel URL saved to primary_channel_url.txt"
fi
echo ""

# Verify configuration
echo "9. Verifying configuration..."
echo ""
python3 -m meshtastic --host "$IP_ADDRESS" --info | grep -E "role|rebroadcast|region|modemPreset|hop" || true
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
if [ -n "$CHANNEL_URL" ]; then
    echo "  PRIMARY Channel URL: $CHANNEL_URL"
fi
echo ""
echo "Next steps:"
echo "  1. Configure 666c client: ./configure_666c_client.sh"
echo "  2. Configure 7284 client: ./configure_7284_client.sh"
echo ""

